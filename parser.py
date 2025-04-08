import requests
import pandas as pd
import time
from bs4 import BeautifulSoup
from itertools import cycle
import csv
import random
from fake_useragent import UserAgent
import os

# Инициализация UserAgent
ua = UserAgent()

def get_okved_by_inn(url, inn, session, proxy_pool):
    try:
        okved = None
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
        cards = soup.select('.background-grey-blue-light.p-15.b-radius-5.m-b-20')

        if not cards:
            print(f"Для ИНН {inn} не найдено карточек компаний")
            return None
        
        for card in cards:
            inn_element = card.select_one('.copy-string.cursor.c-black')
            if inn_element and inn_element.text == str(inn):
                okved_element = card.select_one('.no-indent.m-b-5.c-black.position-rel.b-radius-5.p-5')
                
                if okved_element:
                    okved = okved_element.text.strip().replace("\t", "").replace("\n", " ")
                    time.sleep(random.uniform(30, 90))
                    return okved
            
        print(f"Для ИНН {inn} не найдено совпадений в карточках")
        time.sleep(random.uniform(30, 90))
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса для ИНН {inn}: {e}")
        return None
    except Exception as e:
        print(f"Неожиданная ошибка для ИНН {inn}: {e}")
        return None



def main():
    try:
        df = pd.read_excel('Продажи по контрагентам обработаный.xlsx', sheet_name='Sheet1')
        df['OKVED'] = None
        proxies_list = [
            {'http': 'socks5://09LRp2:7dRKbk@188.119.125.31:9024', 'https': 'socks5://09LRp2:7dRKbk@188.119.125.31:9024'},
            {'http': 'socks5://09LRp2:7dRKbk@193.124.179.181:9905', 'https': 'socks5://09LRp2:7dRKbk@193.124.179.181:9905'},
            {'http': 'socks5://kASWKt:1AdeVe@186.65.117.110:9082', 'https': 'socks5://kASWKt:1AdeVe@186.65.117.110:9082'},
            {'http': 'socks5://WWrRtL:hd1mE2@138.219.122.152:9778', 'https': 'socks5://WWrRtL:hd1mE2@138.219.122.152:9778'},
            {'http': 'socks5://vJb3f1:jFvJoL@138.219.123.105:9006', 'https': 'socks5://vJb3f1:jFvJoL@138.219.123.105:9006'}
        ]
        
        proxy_pool = cycle(proxies_list)
        session = requests.Session()
        base_url = 'https://zachestnyibiznes.ru/search?query='
        processed_inns = {}
        
        file_exists = os.path.isfile('Результат.csv')
        with open('Результат.csv', 'a', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            if not file_exists:
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
                
                if (index + 1) % 100 == 0:
                    print(f'Обработано {index + 1} записей')
                    df.to_excel('Результат_промежуточный.xlsx', index=False)  # Промежуточное сохранение
        
        df.to_excel('Результат.xlsx', index=False)

    except Exception as e:
        print(f"Критическая ошибка: {e}")
        if 'df' in locals():
            df.to_excel('Результат_аварийный.xlsx', index=False)

if __name__ == '__main__':
    main()