from io import TextIOWrapper
from zipfile import ZipFile
from urllib.request import urlretrieve
import os
import platform
import time


def creation_date(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == 'Windows':
        return os.path.getctime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime


class Rates:
    __data = []

    def __init__(self, text):
        for row in text.splitlines():
            val = row.split(';')
            try:
                self.__data.append({
                    'give_id': int(val[0]),
                    'get_id': int(val[1]),
                    'exchange_id': int(val[2]),
                    'rate': float(val[3]) / float(val[4]),
                    # 'give': float(val[3]),
                    # 'get': float(val[4]),
                    'reserve': float(val[5]),
                    'reviews': val[6],
                    'min_sum': float(val[8]),
                    'max_sum': float(val[9]),
                    'city_id': int(val[10]),
                })
            except ZeroDivisionError:
                # Иногда бывает курс N:0 и появляется ошибка деления на 0.
                pass

    def filter(self, give_id, get_id):
        data = []
        for val in self.__data:
            if val['give_id'] == give_id and val['get_id'] == get_id:
                val['give'] = 1 if val['rate'] < 1 else val['rate']
                val['get'] = 1 / val['rate'] if val['rate'] < 1 else 1
                data.append(val)

        return sorted(data, key=lambda x: x['rate'])


class Common:
    def __init__(self):
        self.data = {}

    def get(self):
        return self.data

    def get_by_id(self, id, only_name=True):
        if id not in self.data:
            return False

        return self.data[id]['name'] if only_name else self.data[id]

    def search_by_name(self, name):
        return {k: val for k, val in self.data.items() if val['name'].lower().count(name.lower())}


class Currencies(Common):
    def __init__(self, text):
        super().__init__()
        for row in text.splitlines():
            val = row.split(';')
            self.data[int(val[0])] = {
                'id': int(val[0]),
                'pos_id': int(val[1]),
                'name': val[2],
            }

        self.__data = dict(sorted(self.data.items(), key=lambda x: x[1]['name']))


class Exchangers(Common):
    def __init__(self, text):
        super().__init__()
        for row in text.splitlines():
            val = row.split(';')
            self.data[int(val[0])] = {
                'id': int(val[0]),
                'name': val[1],
            }

        self.__data = dict(sorted(self.data.items()))


class Cities(Common):
    def __init__(self, text):
        super().__init__()
        for row in text.splitlines():
            val = row.split(';')
            self.data[int(val[0])] = {
                'id': int(val[0]),
                'name': val[1],
            }

        self.__data = dict(sorted(self.data.items(), key=lambda x: x[1]['name']))


class BestChange:
    __version = None
    __filename = 'info.zip'
    __url = 'http://api.bestchange.ru/info.zip'
    __enc = 'windows-1251'

    __file_currencies = 'bm_cy.dat'
    __file_exchangers = 'bm_exch.dat'
    __file_rates = 'bm_rates.dat'
    __file_cities = 'bm_cities.dat'

    __currencies = None
    __exchangers = None
    __rates = None
    __cities = None

    def __init__(self, load=True, cache=True, cache_seconds=15, cache_path='./'):
        """
        :param load: True (default). Загружать всю базу сразу
        :param cache: True (default). Использовать кеширование
            (в связи с тем, что сервис отдает данные, в среднем, 15 секунд)
        :param cache_seconds: 15 (default). Сколько времени хранятся кешированные данные.
        В поддержке писали, что загружать архив можно не чаще раз в 30 секунд, но я не обнаружил никаких проблем,
        если загружать его чаще
        :param cache_path: './' (default). Папка хранения кешированных данных (zip-архива)
        """
        self.__cache = cache
        self.__cache_seconds = cache_seconds
        self.__cache_path = cache_path + self.__filename
        if load:
            self.load()

    def load(self):
        try:
            if os.path.isfile(self.__cache_path) \
                    and time.time() - creation_date(self.__cache_path) < self.__cache_seconds:
                filename = self.__cache_path
            else:
                filename, headers = urlretrieve(self.__url, self.__cache_path if self.__cache else None)
        except Exception as e:
            pass
        else:
            zipfile = ZipFile(filename)
            files = zipfile.namelist()

            if self.__file_rates in files:
                text = TextIOWrapper(zipfile.open(self.__file_rates), encoding=self.__enc).read()
                self.__rates = Rates(text)

            if self.__file_currencies in files:
                text = TextIOWrapper(zipfile.open(self.__file_currencies), encoding=self.__enc).read()
                self.__currencies = Currencies(text)

            if self.__file_exchangers in files:
                text = TextIOWrapper(zipfile.open(self.__file_exchangers), encoding=self.__enc).read()
                self.__exchangers = Exchangers(text)

            if self.__file_cities in files:
                text = TextIOWrapper(zipfile.open(self.__file_cities), encoding=self.__enc).read()
                self.__cities = Cities(text)

    def rates(self):
        return self.__rates

    def currencies(self):
        return self.__currencies

    def exchangers(self):
        return self.__exchangers

    def cities(self):
        return self.__cities


if __name__ == '__main__':
    api = BestChange(cache_seconds=3600)

    # print(api.exchangers().search_by_name('обмен'))
    # print(api.currencies().search_by_name('налич'))
    # exit()
    currencies = api.currencies().get()
    exchangers = api.exchangers().get()
    cities = api.cities().get()

    dir_from = 93
    dir_to = 42
    rows = api.rates().filter(dir_from, dir_to)
    title = 'Exchange rates in the direction (https://www.bestchange.ru/index.php?from={}&to={}) {} : {}'
    print(title.format(dir_from, dir_to, api.currencies().get_by_id(dir_from), api.currencies().get_by_id(dir_to)))
    for val in rows[:3]:
        print('{} ({}) {}'.format(exchangers[val['exchange_id']]['name'], cities[val['city_id']]['name'], val))
