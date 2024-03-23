from io import TextIOWrapper
from zipfile import ZipFile
import httpx
import os
import platform
import time
from itertools import groupby


def creation_date(path_to_file):
    if platform.system() == 'Windows':
        return os.path.getctime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            return stat.st_mtime


class Rates:
    def __init__(self, text, split_reviews):
        self.__data = []
        for row in text.splitlines():
            val = row.split(';')
            try:
                self.__data.append({
                    'give_id': int(val[0]),
                    'get_id': int(val[1]),
                    'exchange_id': int(val[2]),
                    'rate': float(val[3]) / float(val[4]),
                    'reserve': float(val[5]),
                    'reviews': val[6].split('.') if split_reviews else val[6],
                    'min_sum': float(val[8]),
                    'max_sum': float(val[9]),
                    'city_id': int(val[10]),
                })
            except ZeroDivisionError:
                pass

    def get(self):
        return self.__data

    def filter(self, give_id, get_id):
        data = [val for val in self.__data if val['give_id'] == give_id and val['get_id'] == get_id]
        for val in data:
            val['give'] = 1 if val['rate'] < 1 else val['rate']
            val['get'] = 1 / val['rate'] if val['rate'] < 1 else 1
        return sorted(data, key=lambda x: x['rate'])


class Common:
    def __init__(self):
        self.data = {}

    def get(self):
        return self.data

    def get_by_id(self, id, only_name=True):
        return self.data[id]['name'] if only_name and id in self.data else self.data.get(id)

    def search_by_name(self, name):
        return {k: v for k, v in self.data.items() if name.lower() in v['name'].lower()}


class Currencies(Common):
    def __init__(self, text):
        super().__init__()
        for row in text.splitlines():
            val = row.split(';')
            self.data[int(val[0])] = {'id': int(val[0]), 'pos_id': int(val[1]), 'name': val[2]}
        self.data = dict(sorted(self.data.items(), key=lambda x: x[1]['name']))


class Exchangers(Common):
    def __init__(self, text):
        super().__init__()
        for row in text.splitlines():
            val = row.split(';')
            self.data[int(val[0])] = {'id': int(val[0]), 'name': val[1], 'wmbl': int(val[3]),
                                      'reserve_sum': float(val[4])}
        self.data = dict(sorted(self.data.items()))

    def extract_reviews(self, rates):
        for k, v in groupby(sorted(rates, key=lambda x: x['exchange_id']), lambda x: x['exchange_id']):
            if k in self.data:
                self.data[k]['reviews'] = next(v)['reviews']


class Cities(Common):
    def __init__(self, text):
        super().__init__()
        for row in text.splitlines():
            val = row.split(';')
            self.data[int(val[0])] = {'id': int(val[0]), 'name': val[1]}
        self.data = dict(sorted(self.data.items(), key=lambda x: x[1]['name']))


class Top(Common):
    def __init__(self, text):
        super().__init__()
        self.data = [dict(zip(['give_id', 'get_id', 'perc'], map(float, row.split(';')))) for row in text.splitlines()]
        self.data = sorted(self.data, key=lambda x: x['perc'], reverse=True)


class BestChange:
    __version = '1.0'
    __filename = 'info.zip'
    __url = 'http://api.bestchange.ru/info.zip'
    __enc = 'windows-1251'

    __file_currencies = 'bm_cy.dat'
    __file_exchangers = 'bm_exch.dat'
    __file_rates = 'bm_rates.dat'
    __file_cities = 'bm_cities.dat'
    __file_top = 'bm_top.dat'

    def __init__(self, load=True, cache=True, cache_seconds=15, cache_path='./', exchangers_reviews=False,
                 split_reviews=False):
        self.__is_error = False
        self.__cache = cache
        self.__cache_seconds = cache_seconds
        self.__cache_path = cache_path + self.__filename
        self.__exchangers_reviews = exchangers_reviews
        self.__split_reviews = split_reviews
        if load:
            self.load()

    def load(self):
        try:
            if not (
                    os.path.isfile(self.__cache_path) and
                    time.time() - creation_date(self.__cache_path) < self.__cache_seconds
            ):
                with httpx.Client() as client:
                    r = client.get(self.__url)
                    if r.status_code == 200:
                        with open(self.__cache_path, 'wb') as f:
                            f.write(r.content)
                    else:
                        raise Exception("Failed to download file")

            with ZipFile(self.__cache_path) as zipfile:
                with zipfile.open(self.__file_rates) as f, TextIOWrapper(f, encoding=self.__enc) as r:
                    self.__rates = Rates(r.read(), self.__split_reviews)
                with zipfile.open(self.__file_currencies) as f, TextIOWrapper(f, encoding=self.__enc) as r:
                    self.__currencies = Currencies(r.read())
                with zipfile.open(self.__file_exchangers) as f, TextIOWrapper(f, encoding=self.__enc) as r:
                    self.__exchangers = Exchangers(r.read())
                with zipfile.open(self.__file_cities) as f, TextIOWrapper(f, encoding=self.__enc) as r:
                    self.__cities = Cities(r.read())
                with zipfile.open(self.__file_top) as f, TextIOWrapper(f, encoding=self.__enc) as r:
                    self.__top = Top(r.read())

            if self.__exchangers_reviews:
                self.__exchangers.extract_reviews(self.__rates.get())

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

    def top(self):
        return self.__top


if __name__ == '__main__':
    api = BestChange(load=True, cache=True, cache_seconds=3600, exchangers_reviews=True, split_reviews=True)
    if api.is_error():
        print("Error:", api.is_error())
    else:
        print("Data loaded successfully.")

        # Пример вывода топовых направлений обмена
        top = api.top().get()
        currencies = api.currencies().get()
        for val in top[:5]:  # выводим первые 5 направлений
            give_currency_name = currencies[val['give_id']]['name']
            get_currency_name = currencies[val['get_id']]['name']
            print(f"{give_currency_name} -> {get_currency_name} with percentage {val['perc']}%")

        # Дополнительно: пример фильтрации обменных курсов
        dir_from, dir_to = 93, 42  # Примерные ID валют для обмена
        rates_filtered = api.rates().filter(dir_from, dir_to)
        print(f"Exchange rates from {currencies[dir_from]['name']} to {currencies[dir_to]['name']}:")
        for rate in rates_filtered[:3]:  # Показать топ 3 курса обмена
            print(f"Exchange ID: {rate['exchange_id']}, Rate: {rate['rate']}, Reserve: {rate['reserve']}")
