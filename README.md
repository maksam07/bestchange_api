# BestChange API

Библиотека для работы с "api" сервиса bestchange.ru предоставит Вам возможность получить:

* курсы со всех направлений;
* валюты;
* обменные пункты;
* города;
* а так же кеширование всех этих данных.

Установка:

```console
pip install bestchange-api
```

Пример использования:

```python
from bestchange_api import BestChange

api = BestChange()
exchangers = api.exchangers().get()

dir_from = 93
dir_to = 42
rows = api.rates().filter(dir_from, dir_to)
title = 'Exchange rates in the direction (https://www.bestchange.ru/index.php?from={}&to={}) {} : {}'
print(title.format(dir_from, dir_to, api.currencies().get_by_id(dir_from), api.currencies().get_by_id(dir_to)))
for val in rows[:3]:
    print('{} {}'.format(exchangers[val['exchange_id']]['name'], val))

```

Для обменных пунктов есть возможность сразу получить количество отзывов о них (работает, только если у обменника есть
хоть одно направление на BestChange):

```python
from bestchange_api import BestChange

api = BestChange(exchangers_reviews=True)
```

Все методы, реализованные на данный момент:

```python
from bestchange_api import BestChange

api = BestChange(cache=True, cache_seconds=300, cache_path='/home/user/tmp/')
api.is_error()  # Возвращает False, если данные успешно загружены, иначе текст ошибки

api.currencies().get()  # Получить список всех валют
api.currencies().get_by_id(1)  # Получить название или словарь определенной валюты
api.currencies().search_by_name('text')  # Поиск валют по подстроке

api.exchangers().get()  # Получить список всех обменных пунктов
api.exchangers().get_by_id(1)  # Получить название или словарь обменного пункта
api.exchangers().search_by_name('text')  # Поиск обменных пунктов по подстроке

api.cities().get()  # Получить список всех городов
api.cities().get_by_id(1)  # Получить название или словарь города
api.cities().search_by_name('text')  # Поиск городов по подстроке

api.rates().filter(1, 2)  # Возвращает курсы, отфильтрованный и отсортированных по направлению 

# Раздел "Популярное"
currencies = api.currencies().get()
for val in api.top().get():
    print(currencies[val['give_id']]['name'], '->', currencies[val['get_id']]['name'], ':', round(val['perc'], 2))
```

Работа с прокси:

```python
from bestchange_api import BestChange

proxy = {'http': '127.0.0.1', 'https': '127.0.0.1'}
api = BestChange(proxy=proxy)
```