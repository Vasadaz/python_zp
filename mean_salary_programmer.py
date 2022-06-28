#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import statistics as stat
from itertools import count

import requests
from dotenv import load_dotenv
from terminaltables import AsciiTable

HH_MIN_LIMIT = 100
HH_POPULAR_PROG_LANGS = [['Язык программирования', 'Вакансий найдено',
                          'Вакансий обработано', 'Средняя зарплата']]

PROG_LANGS = ['JavaScript', 'Java', 'Python', 'Ruby', 'PHP', 'C++', 'C', 'C#',
              'Go', 'Shell', 'Objective-C', 'Scala', 'Swift', 'TypeScript']

SJ_MIN_LIMIT = 10
SJ_POPULAR_PROG_LANGS = [['Язык программирования', 'Вакансий найдено',
                          'Вакансий обработано', 'Средняя зарплата']]


def search_vacancies_hh(language: str, page_number: int) -> list:
    global HH_MIN_LIMIT, hh_end_page, hh_vacancies_found

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

    if hh_vacancies_found < HH_MIN_LIMIT:
        hh_end_page = True
        return []

    if page_number == end_page:
        hh_end_page = True

    return vacancies


def search_vacancies_sj(language: str, page_number: int, token: str) -> list:
    global SJ_MIN_LIMIT, sj_end_page, sj_vacancies_found

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

    if sj_vacancies_found < SJ_MIN_LIMIT:
        sj_end_page = True
        return []

    if page_number == end_page:
        sj_end_page = True

    return vacancies


def predict_rub_salary(vacancies: list,
                       keyword_salary=None,
                       keyword_from=None,
                       keyword_to=None) -> list:
    avg_salaries = []

    for vacancy in vacancies:
        if keyword_salary:
            if not vacancy[keyword_salary]:
                continue
            salary_from = vacancy[keyword_salary][keyword_from]
            salary_to = vacancy[keyword_salary][keyword_to]
        else:
            salary_from = vacancy[keyword_from]
            salary_to = vacancy[keyword_to]

        if not salary_from and not salary_to:
            continue
        elif not salary_from:
            avg_salaries.append(salary_to * 0.8)
        elif not salary_to:
            avg_salaries.append(salary_from * 1.2)
        else:
            avg_salaries.append(stat.mean([salary_from, salary_to]))

    avg_salaries_number = len(avg_salaries)
    avg_salary = int(stat.mean(avg_salaries))

    return [avg_salaries_number, avg_salary]


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
        hh_vacancies = []
        hh_vacancies_found = 0
        
        for hh_page_num in count(0):
            page_hh_vacancies = search_vacancies_hh(lang, hh_page_num)
            hh_vacancies.extend(page_hh_vacancies)

            if hh_end_page:
                break
        
        if hh_vacancies:
            hh_avg_salary = predict_rub_salary(hh_vacancies,
                                               keyword_salary='salary',
                                               keyword_from='from',
                                               keyword_to='to')
            hh_vacancies_processed = hh_avg_salary[0]
            hh_average_salary = hh_avg_salary[1]
            HH_POPULAR_PROG_LANGS.append([lang,
                                          hh_vacancies_found,
                                          hh_vacancies_processed,
                                          hh_average_salary])

        sj_end_page = False
        sj_vacancies = []
        sj_vacancies_found = 0

        for sj_page_num in count(0):
            page_sj_vacancies = search_vacancies_sj(lang, sj_page_num, sj_token)
            sj_vacancies.extend(page_sj_vacancies)

            if sj_end_page:
                break

        if sj_vacancies:
            sj_avg_salary = predict_rub_salary(sj_vacancies,
                                               keyword_from='payment_from',
                                               keyword_to='payment_to')
            sj_vacancies_processed = sj_avg_salary[0]
            sj_average_salary = sj_avg_salary[1]
            SJ_POPULAR_PROG_LANGS.append([lang,
                                          sj_vacancies_found,
                                          sj_vacancies_processed,
                                          sj_average_salary])

    hh_table = make_table('Head Hunter', HH_POPULAR_PROG_LANGS)
    sj_table = make_table('SuperJob', SJ_POPULAR_PROG_LANGS)
    print(f'{hh_table}\n\n{sj_table}')
