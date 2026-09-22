import requests

from pprint import pprint

TOKEN = 'y0__wgBEIz34MsEGJG5GCD9lu6PGTC3l--WCPiJonvdNjgYLRSVaE6-xIP0FluC'

url = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
headers = {'Authorization': f'OAuth {TOKEN}'}
payload = {'from_date': 0}

# Делаем GET-запрос к эндпоинту url с заголовком headers и параметрами params
homework_statuses = requests.get(url, headers=headers, params=payload)

# Печатаем ответ API в формате JSON
# print(homework_statuses.text)

# А можно ответ в формате JSON привести к типам данных Python и напечатать и его
pprint(homework_statuses.json())