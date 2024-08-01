from bestchange_api import BestChange

'''
class Bcodes(Common):
    def __init__(self, text):
        super().__init__()
        for row in text.splitlines():
            val = row.split(';')
            self.data[int(val[0])] = {
                'id': int(val[0]),
                'code': val[1],
                'name': val[2],
                'source': val[3],
            }

        self.data = dict(sorted(self.data.items(), key=lambda x: x[1]['code']))


class Brates(Common):
    def __init__(self, text):
        super().__init__()
        self.data = []
        for row in text.splitlines():
            val = row.split(';')
            self.data.append({
                'give_id': int(val[0]),
                'get_id': int(val[1]),
                'rate': float(val[2]),
            })
'''

if __name__ == '__main__':
    proxy = None  # {'http': '127.0.0.1', 'https': '127.0.0.1'}
    api = BestChange(cache_seconds=1, exchangers_reviews=True, split_reviews=True, ssl=True, proxy=proxy)
    print(api.is_error())

    currencies = api.currencies().get()
    top = api.top().get()

    for val in top:
        print(currencies[val['give_id']]['name'], '->', currencies[val['get_id']]['name'], ':', round(val['perc'], 2))

    exit()
    # print(api.exchangers().search_by_name('обмен'))
    # print(api.currencies().search_by_name('налич'))
    # exit()
    currencies = api.currencies().get()
    exchangers = api.exchangers().get()

    dir_from = 93
    dir_to = 42
    rows = api.rates().filter(dir_from, dir_to)
    title = 'Exchange rates in the direction (https://www.bestchange.ru/index.php?from={}&to={}) {} : {}'
    print(title.format(dir_from, dir_to, api.currencies().get_by_id(dir_from), api.currencies().get_by_id(dir_to)))
    for val in rows[:3]:
        print('{} {}'.format(exchangers[val['exchange_id']]['name'], val))
