#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import statistics as stat
from itertools import count

import requests
from dotenv import load_dotenv
from terminaltables import AsciiTable

PROG_LANGS = ['JavaScript', 'Java', 'Python', 'Ruby', 'PHP', 'C++', 'C', 'C#',
              'Go', 'Shell', 'Objective-C', 'Scala', 'Swift', 'TypeScript']

TABLE_TITLES = ['Язык программирования', 'Вакансий найдено',
                'Вакансий обработано', 'Средняя зарплата']

HH_SALARIES_TABLE = [TABLE_TITLES]
SJ_SALARIES_TABLE = [TABLE_TITLES]


def search_hh_vacancies(language: str, page_number: int) -> list:
    vacansies_min_num = 100
    cities = {'Moscow': 1}

    url = 'https://api.hh.ru/vacancies/'
    payload = {'text': f'Программист {language}',
               'area': cities['Moscow'],
               'page': page_number,
               'per_page': 100,
               'currency': 'RUR',
               'only_with_salary': 'true'}

    page_response = requests.get(url, params=payload)
    page_response.raise_for_status()
    page_resources = page_response.json()
    vacancies_found = int(page_resources['found'])

    if vacancies_found > vacansies_min_num:
        return page_resources['items']


def search_sj_vacancies(language: str, page_number: int, token: str) -> list:
    vacansies_min_num = 100
    cities = {'Moscow': 4}

    url = 'https://api.superjob.ru/2.0/vacancies/'
    head = {'X-Api-App-Id': token}
    payload = {'keyword': f'Программист {language}',
               't': cities['Moscow'],
               'currency': 'rub',
               'page': page_number,
               'count': 100}
    page_response = requests.get(url, headers=head, params=payload)
    page_response.raise_for_status()
    page_resources = page_response.json()
    vacancies_found = int(page_resources['total'])

    if vacancies_found > vacansies_min_num:
        return page_resources['objects']


def predict_rub_salary(min_salary: int, max_salary: int):
    if not min_salary:
        avg_salary = max_salary * 0.8
    elif not max_salary:
        avg_salary = min_salary * 1.2
    else:
        avg_salary = stat.mean([min_salary, max_salary])
    return int(avg_salary)


def make_table(title: str, table_data: list) -> str:
    title = f' {title} '
    table_instance = AsciiTable(table_data, title)
    return table_instance.table


def prepare_statistics(static_tab: list, vacancies: list, avg_salaries: list):
    average_salary = int(stat.mean(avg_salaries))
    vacancies_found = len(vacancies)
    vacancies_processed = len(avg_salaries)

    static_tab.append([lang, vacancies_found, vacancies_processed, average_salary])


if __name__ == '__main__':
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    sj_token = os.environ["SJ_TOKEN"]

    for lang in PROG_LANGS:
        hh_avg_salaries = []
        hh_vacancies = []
        sj_avg_salaries = []
        sj_vacancies = []

        for hh_page_num in count(0):
            page_hh_vacancies = search_hh_vacancies(lang, hh_page_num)

            if page_hh_vacancies:
                hh_vacancies.extend(page_hh_vacancies)
            else:
                break

        for sj_page_num in count(0):
            page_sj_vacancies = search_sj_vacancies(lang, sj_page_num, sj_token)

            if page_sj_vacancies:
                sj_vacancies.extend(page_sj_vacancies)
            else:
                break

        for vacancy in hh_vacancies:
            salary_from = vacancy['salary']['from']
            salary_to = vacancy['salary']['to']

            if salary_from or salary_to:
                vacancy_avg_salary = predict_rub_salary(salary_from, salary_to)
                hh_avg_salaries.append(vacancy_avg_salary)

        for vacancy in sj_vacancies:
            salary_from = vacancy['payment_from']
            salary_to = vacancy['payment_to']

            if salary_from or salary_to:
                vacancy_avg_salary = predict_rub_salary(salary_from, salary_to)
                sj_avg_salaries.append(vacancy_avg_salary)

        if hh_vacancies:
            prepare_statistics(HH_SALARIES_TABLE, hh_vacancies, hh_avg_salaries)

        if sj_vacancies:
            prepare_statistics(SJ_SALARIES_TABLE, sj_vacancies, sj_avg_salaries)

    if len(HH_SALARIES_TABLE) > 1:
        hh_table = make_table('Head Hunter', HH_SALARIES_TABLE)
        print(f'{hh_table}', end='\n\n')

    if len(SJ_SALARIES_TABLE) > 1:
        sj_table = make_table('SuperJob', SJ_SALARIES_TABLE)
        print(f'{sj_table}', end='\n\n')
