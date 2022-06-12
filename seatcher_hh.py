import requests


PROG_LANGS = ['JavaScript', 'Java', 'Python', 'Ruby', 'PHP', 'C++', 'C', 'C#',
              'Go', 'Shell', 'Objective-C', 'Scala', 'Swift', 'TypeScript']


def searh_vacancies(languages: list) -> dict:
    popular_prog_langs = {}

    for lang in languages:
        url = 'https://api.hh.ru/vacancies/'
        payload_all = {'text': f'Программист {lang}',
                       'area': '1',
                       'currency': 'RUR',
                       'only_with_salary': 'true'}

        response = requests.get(url, params=payload_all)
        response.raise_for_status()
        response_data = response.json()
        vacancies_quantity = int(response_data['found'])

        if vacancies_quantity > 100:
            popular_prog_langs[lang] = vacancies_quantity

    return popular_prog_langs


if __name__ == '__main__':
    popular_langs = searh_vacancies(PROG_LANGS)
    print(popular_langs)
