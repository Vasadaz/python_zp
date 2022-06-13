import statistics as stat
from itertools import count

import requests


PROG_LANGS = ['JavaScript', 'Java', 'Python', 'Ruby', 'PHP', 'C++', 'C', 'C#',
              'Go', 'Shell', 'Objective-C', 'Scala', 'Swift', 'TypeScript']


def search_vacancies(languages: list) -> dict:
    popular_prog_langs = {}
    vacancies_found = None

    for lang in languages:
        all_vacansies = {}

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
            vacancies_processed, average_salary = predict_rub_salary(all_vacansies)

            popular_prog_langs[lang] = {'vacancies_found': vacancies_found,
                                        'vacancies_processed': vacancies_processed,
                                        'average_salary': average_salary}
    return popular_prog_langs


def predict_rub_salary(vacansies: dict) -> list:
    salaries_avg = []

    for page in vacansies:
        for vacancy in vacansies[page]:
            salary_from = vacancy['salary']['from']
            salary_to = vacancy['salary']['to']

            if salary_from is None and salary_to is None:
                continue
            elif salary_from is None:
                salaries_avg.append(salary_to * 0.8)
            elif salary_to is None:
                salaries_avg.append(salary_from * 1.2)
            else:
                salaries_avg.append(stat.mean([salary_from, salary_to]))

    salaries_avg_number = len(salaries_avg)
    salary_avg = int(stat.mean(salaries_avg))

    return [salaries_avg_number, salary_avg]


if __name__ == '__main__':
    popular_langs = search_vacancies(PROG_LANGS)

    for i in popular_langs:
        print(i)
        for j in popular_langs[i].items():
            print(f'\t{j}')
