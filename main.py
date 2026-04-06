import requests
from dotenv import load_dotenv
import os
from terminaltables import AsciiTable


def predict_salary(salary_from=None, salary_to=None):
    if salary_from and salary_to:
        expected_salary = int((salary_to + salary_from) / 2)
    elif salary_to:
        expected_salary = int(salary_to * 1.2)
    elif salary_from:
        expected_salary = int(salary_from * 0.8)
    else:
        expected_salary = None
    return expected_salary


def get_language_stats(languages):
    results = {}
    for lang in languages:
        page = 0
        area = 1
        per_page = 100
        url = "https://api.hh.ru/vacancies"
        
        total_found = 0
        all_salaries = []
        while True:
            params = {
                "text": f"{lang} разработчик",
                "area": area,
                "per_page": per_page,
                "page": page
            }
            
            response = requests.get(url, params=params)
            vacancies = response.json()
            
            if page == 0:
                total_found = vacancies.get("found", 0)

            for vacancy in vacancies.get("items", []):
                salary = vacancy.get("salary")
                if salary and salary.get("currency") in ["RUR"]:
                    salary_from, salary_to = salary.get("from"), salary.get("to")
                    predicted = predict_salary(salary_from, salary_to)
                    if predicted:
                        all_salaries.append(predicted)
            page += 1
            if page >= vacancies.get("pages", 0):
                break
        
        if all_salaries:
            average_salary = round(sum(all_salaries) / len(all_salaries))
        else:
            average_salary = 0
        
        results[lang] = {
            "vacancies_found": total_found,
            "vacancies_processed": len(all_salaries),
            "average_salary": average_salary
        }
    
    return results


def get_language_stats_superjob(languages, api_key):
    results = {}
    for lang in languages:
        page = 0
        count = 20
        url = "https://api.superjob.ru/2.0/vacancies/"
        
        headers = {
            "X-Api-App-Id": api_key
        }
        
        total_found = 0
        all_salaries = []
        
        while True:
            params = {
                "keyword": f"{lang} разработчик",
                "town": "Москва",
                "count": count, 
                "page": page
            }
            
            response = requests.get(url, headers=headers, params=params)
            vacancies = response.json()
            
            if page == 0:
                total_found = vacancies.get("total", 0)
            
            for vacancy in vacancies.get("objects", []):
                salary_from = vacancy.get("payment_from")
                salary_to = vacancy.get("payment_to")
                predicted = predict_salary(salary_from, salary_to)
                if predicted:
                    all_salaries.append(predicted)
            if not vacancies.get("more"):
                break
            page += 1

        average_salary = 0
        if all_salaries:
            average_salary = round(sum(all_salaries) / len(all_salaries))

        results[lang] = {
            "vacancies_found": total_found,
            "vacancies_processed": len(all_salaries),
            "average_salary": average_salary
        }

    return results


def get_table(full_stats, languages, site_name):
    print(f"{site_name} статистика:")
    table = [['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]
    for lang in languages:
        stats = full_stats[lang]
        table.append([
            lang,
            stats['vacancies_found'],
            stats['vacancies_processed'],
            stats['average_salary']
        ])
    table = AsciiTable(table)
    print(table.table)


def main():
    load_dotenv()
    api_key = os.getenv("SUPERJOB_SECRET_KEY")
    
    languages = ["Python", "Java", "JavaScript", "C++", "C#", "PHP", "Go", "Ruby"]

    superjob_stats = get_language_stats_superjob(languages, api_key)
    get_table(superjob_stats, languages, "SuperJob")

    hh_stats = get_language_stats(languages)
    get_table(hh_stats, languages, "HeadHunter")


if __name__ == "__main__":
    main()