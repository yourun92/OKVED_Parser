import requests

proxies_list = [
    {'http': 'socks5://09LRp2:7dRKbk@46.161.47.5:9441', 'https': 'socks5://09LRp2:7dRKbk@46.161.47.5:9441'},
    {'http': 'socks5://09LRp2:7dRKbk@188.119.125.31:9024', 'https': 'socks5://09LRp2:7dRKbk@188.119.125.31:9024'},
    {'http': 'socks5://09LRp2:7dRKbk@193.124.179.181:9905', 'https': 'socks5://09LRp2:7dRKbk@193.124.179.181:9905'},
    {'http': 'socks5://kASWKt:1AdeVe@186.65.117.110:9082', 'https': 'socks5://kASWKt:1AdeVe@186.65.117.110:9082'},
    {'http': 'socks5://WWrRtL:hd1mE2@138.219.122.152:9778', 'https': 'socks5://WWrRtL:hd1mE2@138.219.122.152:9778'},
    {'http': 'socks5://vJb3f1:jFvJoL@138.219.123.105:9006', 'https': 'socks5://vJb3f1:jFvJoL@138.219.123.105:9006'}
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
}


def check_proxy(proxy):
    """Проверяет работоспособность прокси для list-org.com."""
    try:
        response = requests.get('https://zachestnyibiznes.ru/', proxies=proxy, timeout=5, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        print(f"Прокси {proxy} работает. Код состояния: {response.status_code}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Прокси {proxy} не работает: {e}")
        return False


working_proxies = []
for proxy in proxies_list:
    if check_proxy(proxy):
        working_proxies.append(proxy)

if working_proxies:
    print("\nРабочие прокси:")
    for proxy in working_proxies:
        print(proxy)
else:
    print("\nВсе прокси не работают.")