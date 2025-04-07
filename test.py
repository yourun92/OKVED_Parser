import requests
import pandas as pd


response = requests.get('https://www.list-org.com/')
print(response.status_code)