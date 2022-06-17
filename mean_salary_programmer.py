import os
import statistics as stat
from itertools import count

import requests

from dotenv import load_dotenv
from terminaltables import AsciiTable


HH_MIN_LIMIT = 100
HH_POPULAR_PROG_LANGS = [['Язык программирования', 'Вакансий найдено',
                          'Вакансий обработано', 'Средняя зарплата']]
HH_VACANCIES_FOUND = 0

PROG_LANGS = ['JavaScript', 'Java', 'Python', 'Ruby', 'PHP', 'C++', 'C', 'C#',
              'Go', 'Shell', 'Objective-C', 'Scala', 'Swift', 'TypeScript']

SJ_MIN_LIMIT = 20
SJ_POPULAR_PROG_LANGS = [['Язык программирования', 'Вакансий найдено',
                          'Вакансий обработано', 'Средняя зарплата']]
SJ_VACANCIES_FOUND = 0


def search_vacancies_hh(language: str) -> dict:
    global HH_MIN_LIMIT, HH_VACANCIES_FOUND

    vacansies = {}

    for page in count(0):
        url = 'https://api.hh.ru/vacancies/'
        payload_all = {'text': f'Программист {language}',
                       'area': '2',
                       'page': page,
                       'per_page': 100,
                       'currency': 'RUR',
                       'only_with_salary': 'true'}

        page_response = requests.get(url, params=payload_all)
        page_response.raise_for_status()
        page_data = page_response.json()
        HH_VACANCIES_FOUND = int(page_data['found'])
        num_pages = page_data['pages']

        if page == num_pages or HH_VACANCIES_FOUND < HH_MIN_LIMIT:
            break
        else:
            vacansies[page] = (page_data['items'])

    return vacansies


def search_vacancies_sj(language: str, token: str) -> dict:
    global SJ_MIN_LIMIT, SJ_VACANCIES_FOUND

    vacansies = {}

    for page in count(0):
        url = '	https://api.superjob.ru/2.0/vacancies/'
        head = {'X-Api-App-Id': token}
        payload = {'keyword': f'Программист {language}',
                   't': 14,
                   'currency': 'rub',
                   'page': page,
                   'count': 100}
        page_response = requests.get(url, headers=head, params=payload)
        page_response.raise_for_status()
        page_data = page_response.json()
        SJ_VACANCIES_FOUND = int(page_data['total'])

        if page == 5 or SJ_VACANCIES_FOUND < SJ_MIN_LIMIT:
            break
        else:
            vacansies[page] = (page_data['objects'])

    return vacansies


def predict_rub_salary(vacansies: dict,
                       keyword_salary=None,
                       keyword_from=None,
                       keyword_to=None) -> list:
    salaries_avg = []

    for page in vacansies:
        for vacancy in vacansies[page]:
            if keyword_salary:
                salary_from = vacancy[keyword_salary][keyword_from]
                salary_to = vacancy[keyword_salary][keyword_to]
            else:
                salary_from = vacancy[keyword_from]
                salary_to = vacancy[keyword_to]

            if not salary_from and not salary_to:
                continue
            elif not salary_from:
                salaries_avg.append(salary_to * 0.8)
            elif not salary_to:
                salaries_avg.append(salary_from * 1.2)
            else:
                salaries_avg.append(stat.mean([salary_from, salary_to]))

    salaries_avg_number = len(salaries_avg)
    salary_avg = int(stat.mean(salaries_avg))

    return [salaries_avg_number, salary_avg]


def make_table(title: str, table_data: list) -> str:
    title = f' {title} '
    table_instance = AsciiTable(table_data, title)
    return table_instance.table


if __name__ == '__main__':
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    sj_token = os.environ["SJ_TOKEN"]

    for lang in PROG_LANGS:
        hh_vacansies = search_vacancies_hh(lang)
        sj_vacansies = search_vacancies_sj(lang, sj_token)

        if hh_vacansies:
            hh_avg_salary = predict_rub_salary(hh_vacansies,
                                               keyword_salary='salary',
                                               keyword_from='from',
                                               keyword_to='to')
            hh_vacancies_processed = hh_avg_salary[0]
            hh_average_salary = hh_avg_salary[1]
            HH_POPULAR_PROG_LANGS.append([lang,
                                          HH_VACANCIES_FOUND,
                                          hh_vacancies_processed,
                                          hh_average_salary])

        if sj_vacansies:
            sj_avg_salary = predict_rub_salary(hh_vacansies,
                                               keyword_salary='salary',
                                               keyword_from='payment_from',
                                               keyword_to='payment_to')
            sj_vacancies_processed = sj_avg_salary[0]
            sj_average_salary = sj_avg_salary[1]
            SJ_POPULAR_PROG_LANGS.append([lang,
                                          SJ_VACANCIES_FOUND,
                                          sj_vacancies_processed,
                                          sj_average_salary])

    hh_table = make_table('Head Hunter', HH_POPULAR_PROG_LANGS)
    sj_table = make_table('SuperJob', SJ_POPULAR_PROG_LANGS)
    print(f'{hh_table}\n\n{sj_table}')
