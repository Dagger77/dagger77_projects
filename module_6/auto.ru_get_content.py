#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# Парсер ссылок на объявления на auto.ru
# Взят у https://github.com/vorontsovdg/autoru_parser и исправлен под текущую структуру страницы с объявлением
# Запускается из консоли с ключом -f и указанием файла со ссылками

import requests
from bs4 import BeautifulSoup
import re
import json
import csv
from multiprocessing import Pool
import argparse

fieldNames = ['url', 'bodyType', 'brand', 'color', 'fuelType', 'modelDate', 'modelName', 'name', 'model_attr',
              'numberOfDoors', 'model_razgon', 'model_consumption', 'model_class', 'productionDate',
              'vehicleTransmission', 'engineDisplacement', 'enginePower', 'description', 'mileage', 'Комплектация',
              'Привод', 'Руль', 'Состояние', 'Владельцы', 'ПТС', 'Таможня', 'Владение', 'Price']


def findModelCard(soup):
    data = soup.find_all(
        'a', class_='Link SpoilerLink CardCatalogLink SpoilerLink_type_default')
    for item in data:
        if item.text.strip() == 'Характеристики модели в каталоге':
            return BeautifulSoup(requests.get(item.attrs['href']).content, 'html.parser')
    return None


def findBodyType(soup):
    try:
        bodyType = soup.find('li', class_='CardInfoRow CardInfoRow_bodytype').find(
            'a', class_='Link Link_color_black').text
    except:
        bodyType = None
    return bodyType


def findBrand(soup):
    try:
        brand = soup.find('div', class_='InfoPopup InfoPopup_theme_plain InfoPopup_withChildren BreadcrumbsPopup-module__BreadcrumbsPopup').find(
            'a', class_='Link Link_color_gray CardBreadcrumbs__itemText').text.strip()
    except:
        brand = None
    return brand


def findColor(soup):
    try:
        color = soup.find('li', class_='CardInfoRow CardInfoRow_color').find(
            'a', class_='Link Link_color_black').text
    except:
        color = None
    return color


def findFuelType(soup):
    try:
        fuelType = soup.find('li', class_='CardInfoRow CardInfoRow_engine').find(
            'a', class_='Link Link_color_black').text
    except:
        fuelType = None
    return fuelType


def findModelName(soup):
    try:
        ModelName = soup.find_all('a', class_='Link Link_color_gray CardBreadcrumbs__itemText')[1].text.strip(
        ) + ' ' + soup.find_all('a', class_='Link Link_color_gray CardBreadcrumbs__itemText')[2].text.strip()
    except:
        ModelName = None
    return ModelName


def findModel_attr(soup):
    try:
        Model_attr = soup.find('div', id="sale-data-attributes")['data-bem']
    except:
        Model_attr = None
    return Model_attr


def findName(soup):
    try:
        name = soup.find_all(
            'a', class_='Link Link_color_gray CardBreadcrumbs__itemText')[-1].text.strip()
    except:
        name = None
    return name


def findNumberOfDoors(soup):
    check = False
    if soup is None:
        return None
    else:
        try:
            info = soup.find('div', class_='content__page search-form-v2-controller__content').find(
                'div', class_='catalog__section catalog__section_package clearfix').find(
                'div', class_='catalog__content').find('dl', class_='list-values clearfix')
            names = info.find_all('dt')
            for i in range(0, len(names)+1):
                if names[i].text == 'Количество дверей':
                    check = True
                    break
            if check:
                numDoors = info.find_all('dd')[i].text
                return numDoors
            else:
                return None
        except:
            return None
        return None


def findModelRazgon(soup):
    check = False
    if soup is None:
        return None
    else:
        try:
            info = soup.find('div', class_='content__page search-form-v2-controller__content').find(
                'div', class_='catalog__section catalog__section_package clearfix').find(
                'div', class_='catalog__content').find_all('dl', class_='list-values list-values_view_ext clearfix')[-1]
            names = info.find_all('dt')
            for i in range(0, len(names)+1):
                if names[i].text == 'Разгон':
                    check = True
                    break
            if check:
                modelRazgon = info.find_all('dd')[i].text
                return modelRazgon
            else:
                return None
        except:
            return None
        return None
        
def findModelConsumption(soup):
    check = False
    if soup is None:
        return None
    else:
        try:
            info = soup.find('div', class_='content__page search-form-v2-controller__content').find(
                'div', class_='catalog__section catalog__section_package clearfix').find(
                'div', class_='catalog__content').find_all('dl', class_='list-values list-values_view_ext clearfix')[-1]
            names = info.find_all('dt')
            for i in range(0, len(names)+1):
                if names[i].text == 'Расход':
                    check = True
                    break
            if check:
                modelRazgon = info.find_all('dd')[i].text
                return modelRazgon
            else:
                return None
        except:
            return None
        return None


def findModelClass(soup):
    check = False
    if soup is None:
        return None
    else:
        try:
            info = soup.find('div', class_='content__page search-form-v2-controller__content').find(
                'div', class_='catalog__section catalog__section_package clearfix').find('div', class_='catalog__content').find('dl', class_='list-values clearfix')
            names = info.find_all('dt')
            for i in range(0, len(names)+1):
                if names[i].text == 'Класс автомобиля':
                    check = True
                    break
            if check:
                model_class = info.find_all('dd')[i].text
                return model_class
            else:
                return None
        except:
            return None
        return None


def findProductionYear(soup):
    try:
        year = soup.find(
            'li', class_='CardInfoRow CardInfoRow_year').find(
            'a', class_='Link Link_color_black').text
        return year
    except:
        return None


def findTransmission(soup):
    try:
        transmission = soup.find(
            'li', class_='CardInfoRow CardInfoRow_transmission').find_all('span')[-1].text
        return transmission
    except:
        return None


def findEngineDisplacement(soup):
    try:
        displacement = soup.find('li', class_='CardInfoRow CardInfoRow_engine').find_all(
            'span')[1].text.split('/')[0]
        return displacement
    except:
        return None


def findEnginePower(soup):
    try:
        power = soup.find('li', class_='CardInfoRow CardInfoRow_engine').find_all(
            'span')[1].text.split('/')[1].strip()
        return power
    except:
        return None


def find_description(soup):
    try:
        description = soup.find('div', class_='CardDescription CardOfferBody__contentIsland').find(
            class_='CardDescription__textInner').get_text("|", strip=True)
        return description
    except:
        return None


def find_mileage(soup):
    try:
        mileage = ''.join([i for i in soup.find(
            'li', class_='CardInfoRow CardInfoRow_kmAge').find_all('span')[-1].text if i.isdigit()])
        return mileage
    except:
        return None


def findWheelDrive(soup):
    try:
        wheelDrive = soup.find(
            'li', class_='CardInfoRow CardInfoRow_drive').find_all('span')[-1].text
        return wheelDrive
    except:
        return None


def findSteeringWheel(soup):
    try:
        steeringWheel = soup.find(
            'li', class_='CardInfoRow CardInfoRow_wheel').find_all('span')[-1].text
        return steeringWheel
    except:
        return None


def findCondition(soup):
    try:
        condition = soup.find(
            'li', class_='CardInfoRow CardInfoRow_state').find_all('span')[-1].text
        return condition
    except:
        return None


def findOwner(soup):
    try:
        owner = soup.find(
            'li', class_='CardInfoRow CardInfoRow_ownersCount').find_all('span')[-1].text
        return owner
    except:
        return None


def findPTS(soup):
    try:
        pts = soup.find('li', class_='CardInfoRow CardInfoRow_pts').find_all(
            'span')[-1].text
        return pts
    except:
        return None


def findCustoms(soup):
    try:
        customs = soup.find(
            'li', class_='CardInfoRow CardInfoRow_customs').find_all('span')[-1].text
        return customs
    except:
        return None


def findTenure(soup):
    try:
        tenure = soup.find(
            'li', class_='CardInfoRow CardInfoRow_owningTime').find_all('span')[-1].text
        return tenure
    except:
        return None


def findModelProductionDate(soup):
    if soup is None:
        return None
    try:
        modelProductionDate = re.findall(r'\d{4}', soup.find(
            'div', class_='search-form-v2-mmm__breadcrumbs search-accordion__header').find_all('a')[-2].text)[0]
        return modelProductionDate
    except:
        return None


def find_equipment(soup):
    equipment = {}
    try:
        for i in soup.find('div', class_='ComplectationGroups').children:
            equipment_group = i.find('div', class_='ComplectationGroups__item').find(
                'span', class_='ComplectationGroups__itemName').text
            options = i.find_all(
                'li', class_='ComplectationGroups__itemContentEl')
            content = [el.text for el in options]
            equipment[equipment_group] = content
        return json.dumps(equipment, ensure_ascii=False)
    except:
        return None


def findPrice(soup):
    try:
        price = soup.find(
            'div', class_='PriceUsedOffer-module__container').find('span', class_='OfferPriceCaption__price').text.strip()
        return price
    except:
        return None


def parse():
    parser = argparse.ArgumentParser(description="""""")
    parser.add_argument('-f', type=str, help='Source file with phone numbers')
    parser.add_argument('--threads', type=int, default=4,
                        help='Number of threads to request page\nDefault value = 4')
    args = parser.parse_args()
    return args


def main(url):
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    modelSoup = findModelCard(soup)
    bodyType = findBodyType(soup)
    brand = findBrand(soup)
    color = findColor(soup)
    fuelType = findFuelType(soup)
    modelDate = findModelProductionDate(modelSoup)
    modelName = findModelName(soup)
    name = findName(soup)
    model_attr = findModel_attr(soup)
    numberOfDoors = findNumberOfDoors(modelSoup)
    model_razgon = findModelRazgon(modelSoup)
    model_consumption = findModelConsumption(modelSoup)
    model_class = findModelClass(modelSoup)
    productionDate = findProductionYear(soup)
    venicleTransmission = findTransmission(soup)
    engineDisplacement = findEngineDisplacement(soup)
    enginePower = findEnginePower(soup)
    description = find_description(soup)
    mileage = find_mileage(soup)
    equipment = find_equipment(soup)
    wheelDrive = findWheelDrive(soup)
    steeringWhell = findSteeringWheel(soup)
    condition = findCondition(soup)
    owner = findOwner(soup)
    pts = findPTS(soup)
    customs = findCustoms(soup)
    tenure = findTenure(soup)
    price = findPrice(soup)

    with open('./results.csv', 'a', encoding='utf-8-sig') as f:
        csvWriter = csv.DictWriter(f, fieldnames=fieldNames)
        csvWriter.writerow({
            'url': url,
            'bodyType': bodyType,
            'brand': brand,
            'color': color,
            'fuelType': fuelType,
            'modelDate': modelDate,
            'modelName': modelName,
            'name': name,
            'model_attr': model_attr,
            'numberOfDoors': numberOfDoors,
            'model_razgon': model_razgon,
            'model_consumption': model_consumption,
            'model_class': model_class,
            'productionDate': productionDate,
            'vehicleTransmission': venicleTransmission,
            'engineDisplacement': engineDisplacement,
            'enginePower': enginePower,
            'description': description,
            'mileage': mileage,
            'Комплектация': equipment,
            'Привод': wheelDrive,
            'Руль': steeringWhell,
            'Состояние': condition,
            'Владельцы': owner,
            'ПТС': pts,
            'Таможня': customs,
            'Владение': tenure,
            'Price': price
        })


if __name__ == '__main__':
    args = parse()
    with open(args.f, 'r') as f:
        urls = [url.rstrip() for url in f.readlines()]
    with Pool(args.threads) as p:
        p.map(main, urls)

