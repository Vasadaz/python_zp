import os
import statistics as stat
from itertools import count

import requests

from dotenv import load_dotenv
from terminaltables import AsciiTable

PROG_LANGS = ['JavaScript', 'Java', 'Python', 'Ruby', 'PHP', 'C++', 'C', 'C#',
              'Go', 'Shell', 'Objective-C', 'Scala', 'Swift', 'TypeScript']


def search_vacancies(hr, languages: list, token=None) -> list:
    popular_prog_langs = [['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]
    vacancies_found = None

    for lang in languages:
        all_vacansies = {}

        if hr == 'Head Hunter':
            for page in count(0):
                url = 'https://api.hh.ru/vacancies/'
                payload_all = {'text': f'Программист {lang}',
                               'area': '2',
                               'page': page,
                               'per_page': 100,
                               'currency': 'RUR',
                               'only_with_salary': 'true'}

                page_response = requests.get(url, params=payload_all)
                page_response.raise_for_status()
                page_data = page_response.json()
                vacancies_found = int(page_data['found'])
                num_pages = page_data['pages']

                if page == num_pages or vacancies_found < 100:
                    break
                else:
                    all_vacansies[page] = (page_data['items'])

            if all_vacansies:
                vacancies_processed, average_salary = predict_rub_salary(all_vacansies,
                                                                         keyword_salary='salary',
                                                                         keyword_from='from',
                                                                         keyword_to='to')
                popular_prog_langs.append([lang, vacancies_found, vacancies_processed, average_salary])

        elif hr == 'SuperJob':
            for page in count(0):
                url = '	https://api.superjob.ru/2.0/vacancies/'
                head = {'X-Api-App-Id': token}
                payload = {'keyword': f'Программист {lang}',
                           't': 14,
                           'currency': 'rub',
                           'page': page,
                           'count': 100}
                page_response = requests.get(url, headers=head, params=payload)
                page_response.raise_for_status()
                page_data = page_response.json()
                vacancies_found = int(page_data['total'])

                if page == 5 or vacancies_found < 10:
                    break
                else:
                    all_vacansies[page] = (page_data['objects'])

            if all_vacansies:
                vacancies_processed, average_salary = predict_rub_salary(all_vacansies,
                                                                         keyword_from='payment_from',
                                                                         keyword_to='payment_to',
                                                                         null=0)
                popular_prog_langs.append([lang, vacancies_found, vacancies_processed, average_salary])

    return make_table(hr, popular_prog_langs)


def predict_rub_salary(vacansies: dict, keyword_salary=None, keyword_from=None, keyword_to=None, null=None) -> list:
    salaries_avg = []

    for page in vacansies:
        for vacancy in vacansies[page]:
            if keyword_salary is not None:
                salary_from = vacancy[keyword_salary][keyword_from]
                salary_to = vacancy[keyword_salary][keyword_to]
            else:
                salary_from = vacancy[keyword_from]
                salary_to = vacancy[keyword_to]

            if salary_from == null and salary_to == null:
                continue
            elif salary_from == null:
                salaries_avg.append(salary_to * 0.8)
            elif salary_to == null:
                salaries_avg.append(salary_from * 1.2)
            else:
                salaries_avg.append(stat.mean([salary_from, salary_to]))

    salaries_avg_number = len(salaries_avg)
    salary_avg = int(stat.mean(salaries_avg))

    return [salaries_avg_number, salary_avg]


def make_table(title: str, table_data: list):
    table_instance = AsciiTable(table_data, title)
    return table_instance.table


if __name__ == '__main__':
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    sj_token = os.environ["SJ_TOKEN"]

    hh = search_vacancies('Head Hunter', PROG_LANGS)
    sj = search_vacancies('SuperJob', PROG_LANGS, sj_token)
    print(f'{hh}\n\n{sj}')
