import requests
from bs4 import BeautifulSoup
from fake_headers import Headers
import re
import json

HH = "https://spb.hh.ru/search/vacancy"
HH_ARTICLES = f'{HH}?text=python&area=1&area=2'
vacancies_dicts = {}


def get_headers():
    return Headers(browser="chrome", os="win").generate()


def check_usd(usd, job_vacancy):
    if not usd:
        return True
    salary = job_vacancy.find('span', class_="bloko-header-section-3")
    if salary != None:
        salary = salary.text
    else:
        salary = ""
    if re.match(r'.*?USD.*?', salary) == None:
        return False
    return True


def parse_data(job_vacancy):
    data = {}
    url = job_vacancy.find('a', class_="serp-item__title")['href']
    salary = job_vacancy.find('span', class_="bloko-header-section-3")
    if salary != None:
        salary = salary.text
    city = job_vacancy.find('div', attrs= \
        {
            'class': 'bloko-text',
            'data-qa': 'vacancy-serp__vacancy-address'
        })
    city = re.sub(r'\s*?(\S)[,].?.*', r'\1', city.text)
    company = job_vacancy.find('a' \
                               , class_="bloko-link bloko-link_kind-tertiary").text

    dict_format = {
        'Cсылка': url,
        'Вилка ЗП': salary,
        'Название компании': company,
        'Город': city,
    }
    return dict_format


def create_json(usd=False):
    main_html = requests.get(HH_ARTICLES, headers=get_headers()).text
    soup = BeautifulSoup(main_html, features='lxml')
    vacancies = soup.find_all("div", class_='serp-item')
    count = 1
    for job_vacancy in vacancies:
        div_descriptions = job_vacancy.find('div', class_="g-user-content")
        bloko_descriptions = div_descriptions.find_all('div', class_="bloko-text")
        descriptions = list(map(lambda x: x.text, bloko_descriptions))
        description = ' '.join(descriptions).lower()
        django = re.match(r'.*?django.*?', description)
        flask = re.match(r'.*?flask.*?', description)
        if django != None and flask != None:
            if check_usd(usd, job_vacancy):
                vacancies_dicts[count] = parse_data(job_vacancy)
                count += 1
        with open('vacancies.json', 'w', encoding='utf8') as json_file:
            json.dump(vacancies_dicts, json_file, ensure_ascii=False)


create_json(usd=False)