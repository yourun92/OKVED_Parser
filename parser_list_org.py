import requests
import pandas as pd
import time
from bs4 import BeautifulSoup
from itertools import cycle
import csv
import random
from fake_useragent import UserAgent  # Исправленный импорт

# Инициализация UserAgent
ua = UserAgent()

def get_okved(link_part, session, headers):
    link = 'https://www.list-org.com' + link_part
    try:
        response = session.get(link, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        okved = None
        
        cards = soup.select('.card.w-100.p-1.p-lg-3.mt-2')
        if 'man' in link_part:
            for card in cards:
                if card.select('.fa.fas.fa-eye.fa-fw'):
                    type_of_activity = card.select_one('p')
                    if type_of_activity:
                        okved = type_of_activity.text.split('\n')[-2].strip()
                        if okved:
                            break
        else:
            for card in cards:
                if card.select('.fa.fa-tags.fa-fw'):
                    type_of_activity = card.select_one('p')
                    if type_of_activity:
                        okved = type_of_activity.text.strip()
                        if okved:
                            break
        return okved
    except Exception as e:
        print(f"Ошибка при парсинге OKVED: {e}")
        return None

def get_okved_by_inn(url, inn, session, proxy_pool):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            proxy = next(proxy_pool)
            headers = {
                'User-Agent': ua.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8',
                'Connection': 'keep-alive'
            }
            session.proxies.update(proxy)
            
            response = session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            link_part = soup.select_one('.org_list a')['href']
            
            time.sleep(random.uniform(30, 90))
            okved = get_okved(link_part, session, headers)
            time.sleep(random.uniform(30, 90))
            
            return okved
        except Exception as e:
            print(f"Ошибка для ИНН {inn} (попытка {attempt + 1}): {e}")
            time.sleep(random.uniform(60, 120))  # Увеличенная задержка при ошибке
    return None

def main():
    df = pd.read_excel('Продажи по контрагентам обработаный.xlsx', sheet_name='Sheet1')
    df['OKVED'] = None

    proxies_list = [
        {'http': 'socks5://kASWKt:1AdeVe@186.65.117.110:9082', 'https': 'socks5://kASWKt:1AdeVe@186.65.117.110:9082'}
    ]
    
    proxy_pool = cycle(proxies_list)
    session = requests.Session()
    base_url = 'https://www.list-org.com/search?val='
    processed_inns = {}
    
    with open('Результат.csv', 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Name', 'INN', 'Email', 'OKVED'])
        
        for index, row in df.iterrows():
            name = row['Name']
            inn = str(row['INN'])
            email = row['Email']
            
            if inn in processed_inns:
                okved = processed_inns[inn]
            else:
                okved = get_okved_by_inn(base_url + inn, inn, session, proxy_pool)
                processed_inns[inn] = okved
            
            df.loc[index, 'OKVED'] = okved
            csv_writer.writerow([name, inn, email, okved])
            
            if (index + 1) % 50 == 0:
                print(f'Обработано {index + 1} записей')
                df.to_excel('Результат_промежуточный.xlsx', index=False)  # Промежуточное сохранение
    
    df.to_excel('Результат.xlsx', index=False)

if __name__ == '__main__':
    main()