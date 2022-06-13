import statistics as stat

import requests


PROG_LANGS = ['JavaScript', 'Java', 'Python', 'Ruby', 'PHP', 'C++', 'C', 'C#',
              'Go', 'Shell', 'Objective-C', 'Scala', 'Swift', 'TypeScript']


def searh_vacancies(languages: list) -> dict:
    popular_prog_langs = {}

    for lang in languages:

        url = 'https://api.hh.ru/vacancies/'
        payload_all = {'text': f'Программист {lang}',
                       'area': '1',
                       "per_page": 100,
                       'currency': 'RUR',
                       'only_with_salary': 'true'}

        response = requests.get(url, params=payload_all)
        response.raise_for_status()
        response_data = response.json()
        vacancies_found = int(response_data['found'])
        vacancies_processed, average_salary = predict_rub_salary(response_data['items'])

        if vacancies_found > 100:
            popular_prog_langs[lang] = {'vacancies_found': vacancies_found,
                                        'vacancies_processed': vacancies_processed,
                                        'average_salary': average_salary}
    return popular_prog_langs


def predict_rub_salary(vacansies: dict) -> list:
    salaries_avg = []

    for vacancy in vacansies:
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
    popular_langs = searh_vacancies(PROG_LANGS)
    for i in popular_langs:
        print(i)
        for j in popular_langs[i].items():
            print(f'\t{j}')
