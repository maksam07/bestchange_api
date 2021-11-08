# BestChange API

Эта библиотека для работы с "api" сервиса bestchange.ru предоставит Вам возможность получить:
* курсы со всех направления;
* валюты;
* обменные пункты;
* города;
* а так же кеширование всех этих данных.

Установка:
```python
pip install bestchange-api
```

Пример использования:  
```python
    from bestchange_api import BestChange


    api = BestChange()
    exchangers = api.exchangers().get()
    cities = api.cities().get()
    
    dir_from = 93
    dir_to = 42
    rows = api.rates().filter(dir_from, dir_to)
    title = 'Exchange rates in the direction (https://www.bestchange.ru/index.php?from={}&to={}) {} : {}'
    print(title.format(dir_from, dir_to, api.currencies().get_by_id(dir_from), api.currencies().get_by_id(dir_to)))
    for val in rows[:3]:
        print('{} ({}) {}'.format(exchangers[val['exchange_id']]['name'], cities[val['city_id']]['name'], val))
```

Все методы, реализованные на данный момент:
```python
    from bestchange_api import BestChange


    api = BestChange(cache=True, cache_seconds=300, cache_path='/home/user/tmp/')
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
```

Спасибо за внимание.