#!/usr/bin/env python
# coding: utf-8

# In[4]:


### Граббер ссылок из поисковой выдачи auto.ru по названию марки автомобиля.
### К сожалению выдача ограничена 99-ю страницами. Выгружаются скорее всего не все объявления.


import requests
from bs4 import BeautifulSoup

brands = ['SKODA', 'AUDI', 'HONDA', 'VOLVO', 'BMW', 'NISSAN',
          'INFINITI', 'MERCEDES', 'TOYOTA', 'LEXUS', 'VOLKSWAGEN', 'MITSUBISHI']
links = []
url = 'https://auto.ru/cars/'
for car_brand in brands:
    brand_url = url + car_brand + '/used/?page='
    print(car_brand)
    for number in range(1, 100):
        response = requests.get(brand_url+str(number),
                                headers={'User-Agent': 'Mozilla/5.0'})
        page = BeautifulSoup(response.text, 'html.parser')
        link_list = page.find_all(
            'a', class_='Link ListingItemTitle-module__link')
        if len(link_list) != 0:
            links.extend(link_list)
        else:
            break
with open('./links_br.csv', 'a') as f:
    for link in links:
        f.write(link.attrs['href'] + '\n')

