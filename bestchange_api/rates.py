class Rates:
    __data: list[dict]

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
                # Иногда бывает курс N:0 и появляется ошибка деления на 0.
                pass

    def get(self):
        """Возвращает данные"""
        return self.__data

    def filter(self, give_id: int, get_id: int):
        data = []
        for val in self.__data:
            if val['give_id'] == give_id and val['get_id'] == get_id:
                val['give'] = 1 if val['rate'] < 1 else val['rate']
                val['get'] = 1 / val['rate'] if val['rate'] < 1 else 1
                data.append(val)

        return sorted(data, key=lambda x: x['rate'])
