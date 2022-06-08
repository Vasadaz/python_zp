import requests


url = 'https://api.hh.ru/vacancies/'
payload = {'text': 'Программист'}

response = requests.get(url, params=payload)
response.raise_for_status()

imgs = response.json()

print(imgs)
