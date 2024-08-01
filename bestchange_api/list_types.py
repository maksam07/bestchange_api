from itertools import groupby


class Common:
    data: dict[int, dict] | list

    def __init__(self):
        self.data = {}

    def get(self):
        """Получить данные"""
        return self.data

    def get_by_id(self, id: int, only_name=True):
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

        self.data = dict(sorted(self.data.items(), key=lambda x: x[1]['name']))


class Exchangers(Common):
    def __init__(self, text):
        super().__init__()
        for row in text.splitlines():
            val = row.split(';')
            self.data[int(val[0])] = {
                'id': int(val[0]),
                'name': val[1],
                'wmbl': int(val[3]),
                'reserve_sum': float(val[4]),
            }

        self.data = dict(sorted(self.data.items()))

    def extract_reviews(self, rates):
        for k, v in groupby(sorted(rates, key=lambda x: x['exchange_id']), lambda x: x['exchange_id']):
            if k in self.data.keys():
                self.data[k]['reviews'] = list(v)[0]['reviews']


class Cities(Common):
    def __init__(self, text):
        super().__init__()
        for row in text.splitlines():
            val = row.split(';')
            self.data[int(val[0])] = {
                'id': int(val[0]),
                'name': val[1],
            }

        self.data = dict(sorted(self.data.items(), key=lambda x: x[1]['name']))


class Top(Common):
    data: list[dict]

    def __init__(self, text: str):
        super().__init__()
        self.data = []
        for row in text.splitlines():
            val = row.split(';')
            self.data.append({
                'give_id': int(val[0]),
                'get_id': int(val[1]),
                'perc': float(val[2]),
            })

        self.data = sorted(self.data, key=lambda x: x['perc'], reverse=True)
