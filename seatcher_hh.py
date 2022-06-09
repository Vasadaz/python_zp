import requests
import json


url = 'https://api.hh.ru/vacancies/'
payload_all = {'text': 'Программист',
           'area': '1',
           'currency': 'RUR',
           'only_with_salary': 'true'}

payload_one_month = {'text': 'Программист',
           'area': '1',
           'currency': 'RUR',
           'only_with_salary': 'true',
            'period': 30}

response_all = requests.get(url, params=payload_all)
response_all.raise_for_status()
all_data = response_all.json()

response_one_month = requests.get(url, params=payload_one_month)
response_one_month.raise_for_status()
one_month_data = response_one_month.json()

for vacant in all_data['items']:
    print(vacant['name'])
    print(vacant['area']['name'])
    print('ЗП от', vacant['salary']['from'], vacant['salary']['currency'])
    print(vacant['published_at'])
    print()


print('Вакансий за всё время:', all_data['found'])
print('Вакансий за последний месяц:', one_month_data['found'])
