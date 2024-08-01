import os
import ssl
import time
from io import TextIOWrapper
from urllib.request import ProxyHandler, build_opener, install_opener, urlretrieve
from zipfile import ZipFile

from bestchange_api.tools import creation_date
from bestchange_api.list_types import Currencies, Exchangers, Cities, Top
from bestchange_api.rates import Rates


class BestChange:
    __version = None
    __filename = 'info.zip'
    __url = 'http://api.bestchange.ru/info.zip'
    __enc = 'windows-1251'

    __file_currencies = 'bm_cy.dat'
    __file_exchangers = 'bm_exch.dat'
    __file_rates = 'bm_rates.dat'
    __file_cities = 'bm_cities.dat'
    __file_top = 'bm_top.dat'
    # __file_bcodes = 'bm_bcodes.dat'
    # __file_brates = 'bm_brates.dat'

    __currencies = None
    __exchangers = None
    __rates = None
    __cities = None
    # __bcodes = None
    # __brates = None
    __top = None

    def __init__(self,
                 load=True,
                 cache=True,
                 cache_seconds=15,
                 cache_path='./',
                 exchangers_reviews=False,
                 split_reviews=False,
                 ssl=True,
                 proxy=None
                 ):
        """
        :param load: True (default). Загружать всю базу сразу
        :param cache: True (default). Использовать кеширование
            (в связи с тем, что сервис отдает данные, в среднем, 15 секунд)
        :param cache_seconds: 15 (default). Сколько времени хранятся кешированные данные.
        В поддержке писали, что загружать архив можно не чаще раз в 30 секунд, но я не обнаружил никаких проблем,
        если загружать его чаще
        :param cache_path: './' (default). Папка хранения кешированных данных (zip-архива)
        :param exchangers_reviews: False (default). Добавить в информацию об обменниках количество отзывов. Работает
        только с включенными обменниками и у которых минимум одно направление на BestChange.
        :param split_reviews: False (default). По-умолчанию BestChange отдает отрицательные и положительные отзывы
        одним значением через точку. Так как направлений обмена и обменников огромное количество, то это значение
        по-умолчанию отключено, чтобы не вызывать лишнюю нагрузку
        :param ssl: Использовать SSL соединение для загрузки данных
        :param proxy: Использовать прокси. Пример: {'http': '127.0.0.1', 'https': '127.0.0.1'}
        """
        self.__is_error = False
        self.__cache = cache
        self.__cache_seconds = cache_seconds
        self.__cache_path = cache_path + self.__filename
        self.__exchangers_reviews = exchangers_reviews
        self.__split_reviews = split_reviews
        self.__ssl = ssl
        self.__proxy = proxy
        if load:
            self.load()

    def load(self) -> None:
        """Загрузить данные через API"""
        try:
            if os.path.isfile(self.__cache_path) \
                    and time.time() - creation_date(self.__cache_path) < self.__cache_seconds:
                filename = self.__cache_path
            else:
                if self.__ssl:
                    # Отключаем проверку сертификата, так как BC его не выпустил для этой страницы
                    ssl._create_default_https_context = ssl._create_unverified_context
                    self.__url = self.__url.replace('http', 'https')

                if self.__proxy is not None:
                    proxy = ProxyHandler(self.__proxy)
                    opener = build_opener(proxy)
                    install_opener(opener)

                filename, headers = urlretrieve(self.__url, self.__cache_path if self.__cache else None)

            zipfile = ZipFile(filename)
            files = zipfile.namelist()

            if self.__file_rates not in files:
                raise Exception('File "{}" not found'.format(self.__file_rates))

            if self.__file_currencies not in files:
                raise Exception('File "{}" not found'.format(self.__file_currencies))

            if self.__file_exchangers not in files:
                raise Exception('File "{}" not found'.format(self.__file_exchangers))

            if self.__file_cities not in files:
                raise Exception('File "{}" not found'.format(self.__file_cities))

            if self.__file_top not in files:
                raise Exception('File "{}" not found'.format(self.__file_top))

            with zipfile.open(self.__file_rates) as f:
                with TextIOWrapper(f, encoding=self.__enc) as r:
                    self.__rates = Rates(r.read(), self.__split_reviews)

            with zipfile.open(self.__file_currencies) as f:
                with TextIOWrapper(f, encoding=self.__enc) as r:
                    self.__currencies = Currencies(r.read())

            with zipfile.open(self.__file_exchangers) as f:
                with TextIOWrapper(f, encoding=self.__enc) as r:
                    self.__exchangers = Exchangers(r.read())

            with zipfile.open(self.__file_cities) as f:
                with TextIOWrapper(f, encoding=self.__enc) as r:
                    self.__cities = Cities(r.read())
            '''
            if self.__file_bcodes in files:
                text = TextIOWrapper(zipfile.open(self.__file_bcodes), encoding=self.__enc).read()
                self.__bcodes = Bcodes(text)

            if self.__file_brates in files:
                text = TextIOWrapper(zipfile.open(self.__file_brates), encoding=self.__enc).read()
                self.__brates = Brates(text)
            '''
            with zipfile.open(self.__file_top) as f:
                with TextIOWrapper(f, encoding=self.__enc) as r:
                    self.__top = Top(r.read())

            # ...
            if self.__exchangers_reviews:
                self.exchangers().extract_reviews(self.rates().get())

            zipfile.close()

            if not self.__cache:
                os.remove(filename)

        except Exception as e:
            self.__is_error = str(e)

    def is_error(self):
        return self.__is_error

    def rates(self):
        return self.__rates

    def currencies(self):
        return self.__currencies

    def exchangers(self):
        return self.__exchangers

    def cities(self):
        return self.__cities

    '''
    def bcodes(self):
        return self.__bcodes

    def brates(self):
        return self.__brates
    '''

    def top(self):
        return self.__top
