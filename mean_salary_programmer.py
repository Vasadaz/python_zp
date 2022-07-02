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

HH_MIN_NUM_VACANSIES = 100
HH_SALARIES_TABLE = [['Язык программирования', 'Вакансий найдено',
                      'Вакансий обработано', 'Средняя зарплата']]

SJ_MIN_NUM_VACANSIES = 10
SJ_SALARIES_TABLE = [['Язык программирования', 'Вакансий найдено',
                      'Вакансий обработано', 'Средняя зарплата']]


def search_vacancies_hh(language: str, page_number: int) -> list:
    global HH_MIN_NUM_VACANSIES, hh_end_page, hh_vacancies_found

    url = 'https://api.hh.ru/vacancies/'
    payload = {'text': f'Программист {language}',
               'area': '1',
               'page': page_number,
               'per_page': 100,
               'currency': 'RUR',
               'only_with_salary': 'true'}

    page_response = requests.get(url, params=payload)
    page_response.raise_for_status()
    page_data = page_response.json()

    end_page = int(page_data['pages']) - 1
    hh_vacancies_found = int(page_data['found'])
    vacancies = page_data['items']

    if hh_vacancies_found < HH_MIN_NUM_VACANSIES:
        hh_end_page = True
        return []

    if page_number == end_page:
        hh_end_page = True

    return vacancies


def search_vacancies_sj(language: str, page_number: int, token: str) -> list:
    global SJ_MIN_NUM_VACANSIES, sj_end_page, sj_vacancies_found

    url = 'https://api.superjob.ru/2.0/vacancies/'
    head = {'X-Api-App-Id': token}
    payload = {'keyword': f'Программист {language}',
               't': 4,
               'currency': 'rub',
               'page': page_number,
               'count': 10}
    page_response = requests.get(url, headers=head, params=payload)
    page_response.raise_for_status()
    page_data = page_response.json()

    end_page = 4
    sj_vacancies_found = int(page_data['total'])
    vacancies = (page_data['objects'])

    if sj_vacancies_found < SJ_MIN_NUM_VACANSIES:
        sj_end_page = True
        return []

    if page_number == end_page:
        sj_end_page = True

    return vacancies


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


if __name__ == '__main__':
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    sj_token = os.environ["SJ_TOKEN"]

    for lang in PROG_LANGS:
        hh_end_page = False
        hh_avg_salaries = []
        hh_vacancies = []
        hh_vacancies_found = 0

        for hh_page_num in count(0):
            page_hh_vacancies = search_vacancies_hh(lang, hh_page_num)
            hh_vacancies.extend(page_hh_vacancies)

            if hh_end_page:
                break

        if hh_vacancies:
            for vacancy in hh_vacancies:
                salary_from = vacancy['salary']['from']
                salary_to = vacancy['salary']['to']

                if salary_from or salary_to:
                    vacancy_avg_salary = predict_rub_salary(salary_from, salary_to)
                    hh_avg_salaries.append(vacancy_avg_salary)

            hh_vacancies_processed = len(hh_avg_salaries)
            hh_average_salary = int(stat.mean(hh_avg_salaries))

            HH_SALARIES_TABLE.append([lang,
                                      hh_vacancies_found,
                                      hh_vacancies_processed,
                                      hh_average_salary])

        sj_end_page = False
        sj_avg_salaries = []
        sj_vacancies = []
        sj_vacancies_found = 0

        for sj_page_num in count(0):
            page_sj_vacancies = search_vacancies_sj(lang, sj_page_num, sj_token)
            sj_vacancies.extend(page_sj_vacancies)

            if sj_end_page:
                break

        if sj_vacancies:
            for vacancy in sj_vacancies:
                salary_from = vacancy['payment_from']
                salary_to = vacancy['payment_to']

                if salary_from or salary_to:
                    vacancy_avg_salary = predict_rub_salary(salary_from, salary_to)
                    sj_avg_salaries.append(vacancy_avg_salary)

            sj_vacancies_processed = len(sj_avg_salaries)
            sj_average_salary = int(stat.mean(sj_avg_salaries))

            SJ_SALARIES_TABLE.append([lang,
                                      sj_vacancies_found,
                                      sj_vacancies_processed,
                                      sj_average_salary])

    hh_table = make_table('Head Hunter', HH_SALARIES_TABLE)
    sj_table = make_table('SuperJob', SJ_SALARIES_TABLE)
    print(f'{hh_table}\n\n{sj_table}')
