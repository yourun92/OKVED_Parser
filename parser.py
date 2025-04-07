import requests
import pandas as pd
import os
import time
from bs4 import BeautifulSoup
from itertools import cycle


def get_okved(link_part, session, headers):
    link = 'https://www.list-org.com' + link_part
    response = session.get(link, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    
    okved = None  # Значение по умолчанию
    
    try:
        # Получаем все карточки с информацией
        cards = soup.select('.card.w-100.p-1.p-lg-3.mt-2')
        
        if 'man' in link_part:
            # Обработка для физических лиц (если 'man' в ссылке)
            for i in range(len(cards)):
                try:
                    if cards[i].select('.fa.fas.fa-eye.fa-fw'):
                        type_of_activity = cards[i].select_one('p')
                        if type_of_activity:
                            okved = type_of_activity.text.split('\n')[-2]
                            if okved:  # Если нашли не пустое значение
                                break
                except:
                    continue
        else:
            # Обработка для юридических лиц
            for i in range(len(cards)):
                try:
                    if cards[i].select('.fa.fa-tags.fa-fw'):
                        type_of_activity = cards[i].select_one('p')
                        if type_of_activity:
                            okved = type_of_activity.text
                            if okved:  # Если нашли не пустое значение
                                break
                except:
                    continue
    
    except Exception as e:
        print(f"Ошибка при парсинге OKVED: {e}")
    
    return okved


def get_okved_by_inn(url, inn):
    ind = 1

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Connection': 'keep-alive'
    }

    proxies_list = [
        {'http': 'socks5://09LRp2:7dRKbk@46.161.47.5:9441', 'https': 'socks5://09LRp2:7dRKbk@46.161.47.5:9441'},
        {'http': 'socks5://09LRp2:7dRKbk@188.119.125.31:9024', 'https': 'socks5://09LRp2:7dRKbk@188.119.125.31:9024'},
        {'http': 'socks5://09LRp2:7dRKbk@193.124.179.181:9905', 'https': 'socks5://09LRp2:7dRKbk@193.124.179.181:9905'}]
    
    proxy_pool = cycle(proxies_list)
    session = requests.Session()

    url += inn
    try:
        proxy = next(proxy_pool)
        session.proxies.update(proxy)
        
        response = session.get(url, headers=headers, timeout=5)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'lxml')
        link_part = soup.select_one('.org_list').select_one('a')['href']
        time.sleep(5)
        okved = get_okved(link_part, session, headers)
        time.sleep(5)

        ind += 1
        if ind % 50 == 0:
            print(f'Обработано {ind} записей')

        return okved
    
    except Exception as e:
        print(f"Ошибка для ИНН {inn}: {e}")
        
        ind += 1
        if ind % 50 == 0:
            print(f'Обработано {ind} записей')
        
        return None

def main():
    df = pd.read_excel('Продажи по контрагентам обработаный.xlsx', sheet_name='Sheet1')
    df['OKVED'] = df['ИНН'].apply(lambda x: get_okved_by_inn('https://www.list-org.com/search?val=', str(x)))
    
    df.to_excel('Результат_с_OKVED.xlsx', index=False)
if __name__ == '__main__':
    main()
        
        