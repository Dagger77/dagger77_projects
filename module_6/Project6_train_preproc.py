#!/usr/bin/env python
# coding: utf-8

# In[449]:


import requests
from bs4 import BeautifulSoup
import re
import json
import csv
import pandas as pd
import numpy as np
from pprint import pprint


# In[450]:


pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


# In[451]:


columns = ['url', 'bodyType', 'brand', 'color', 'fuelType', 'modelDate', 'modelName', 'name', 'numberOfDoors', 'productionDate',
              'vehicleTransmission', 'engineDisplacement', 'enginePower', 'description', 'mileage', 'Комплектация',
              'Привод', 'Руль', 'Состояние', 'Владельцы', 'ПТС', 'Таможня', 'Владение', 'Price']


# In[452]:


data=pd.read_csv('results.csv', header=None, error_bad_lines=False)


# In[453]:


data.columns=columns


# In[454]:


# Выкинем строки, которые неправильно загрузились из-за спецсимволов
data.drop(data.index[[450, 25192, 28786, 39098]], inplace = True)


# In[455]:


data.info()


# In[456]:


# В числовой вид
data.modelDate = pd.to_numeric(data.modelDate)


# In[457]:


# Очистим столбец
data.productionDate = data.productionDate.str.strip()


# In[458]:


# Очистим столбец и исправим написание мерседеса
data.brand=data.brand.str.upper()
data.loc[data.brand=='MERCEDES-BENZ', 'brand'] = 'MERCEDES'


# In[459]:


# Уберем безымянные
data.dropna(subset=['name'], inplace=True)


# In[460]:


# Уберем 2шт без типа кузова
data.dropna(subset=['bodyType'], inplace=True)


# In[461]:


# В числовой вид
data.numberOfDoors=pd.to_numeric(data.numberOfDoors)


# In[462]:


# Обработка для электроавтомобилей
data.loc[data.name.str.contains("Electro"), 'fuelType']='электро'
data.loc[data.name.str.contains("Electro"), 'enginePower']=data[data.name.str.contains("Electro")].engineDisplacement
data.loc[data.name.str.contains("Electro"), 'engineDisplacement']='0 л'


# In[463]:


# Приводим виды топлива к test
data.fuelType= data.fuelType.str.replace(', газобаллонное оборудование', '')
data.fuelType= data.fuelType.str.lower()


# In[464]:


# Очистим столбец с объемом двигателя
data.engineDisplacement=pd.to_numeric(data.engineDisplacement.str.strip(' л'))


# In[465]:


# Очистим столбец с мощностью двигателя
data.enginePower=data.enginePower.str.strip()
data.enginePower=data.enginePower.str.strip('\xa0л.с.')
data.enginePower=pd.to_numeric(data.enginePower).astype(int)


# In[466]:


# В числовой вид
data.mileage = pd.to_numeric(data.mileage.str.strip())


# In[467]:


# В числовой вид
data.Владельцы = pd.to_numeric(data.Владельцы.str[0])


# In[468]:


# Очищаем столбец Владение, выделяем годы и месяцы и переводим в месяцы
def ownership_fix(record):
    if record == None:
        return(None)
    digits = re.findall(r'\d+', record)
    letters = re.findall(r'\D+', record)
    if len(digits) == 2:
        return (int(digits[0])*12 + int(digits[1]))
    elif len(digits) == 1:
        if 'го' in letters[0] or 'ле' in letters[0]:
            return(int(digits[0])*12)
        if 'ме' in letters[0]:
            return(int(digits[0]))


# In[469]:


data.Владение.fillna('', inplace=True)
data.Владение = data.Владение.apply(ownership_fix)
#data.Владение = data.Владение.astype(int)


# In[470]:


# Очистим столбец с ценой
data.Price = data.Price.str.replace(u'\xa0', u'')
data.Price = pd.to_numeric(data.Price.str.strip('₽'))


# In[471]:


# Уберем записи без целевой переменной
data.dropna(subset=['Price'], inplace=True)
data.Price = data.Price.astype(int)


# In[472]:


# Мелкие исправления у одного авто
data.loc[data.modelDate.isna(), 'modelDate'] = 2013
data.modelDate = data.modelDate.astype(int)
data.loc[data.numberOfDoors.isna(), 'numberOfDoors'] = 5
data.numberOfDoors=data.numberOfDoors.astype(int)


# In[473]:


# Пропуски в году выпуска автомобиля заполним датой выхода модели на рынок
data.loc[data.productionDate.isna(
), 'productionDate'] = data[data.productionDate.isna()].modelDate
data.productionDate = data.productionDate.astype(int)


# In[474]:


data.Состояние.fillna('Не требует ремонта', inplace=True)
data.Владельцы.fillna(3, inplace=True)
data.Владельцы=data.Владельцы.astype(int)


# In[475]:


data[data.Владельцы.isna()]


# In[476]:


data.brand.unique()


# In[477]:


# Обработка названий модели
def bmw_fix(record):
    if record[1] == 'серии':
        return(record[0]+'ER')
    elif record[1] == 'M':
        return(record[0]+'_M')
    else:
        return(record[0])


data.loc[data.brand == 'BMW', 'modelName'] = data[data.brand ==
                                                  'BMW'].modelName.str.split()
data.loc[data.brand == 'BMW', 'modelName'] = data[data.brand ==
                                                  'BMW'].modelName.apply(bmw_fix)


# In[478]:


def honda_fix(record):
    if record[1] == 'Type':
        return('CIVIC_TYPE_R')
    elif record[1] == 'Ferio':
        return('CIVIC_FERIO')
    elif record[1] == '(North':
        return('ODYSSEY_NA')
    elif record[1] == 'Spike':
        return('MOBILIO_SPIKE')
    else:
        return(record[0].replace('-', '_')).upper()


data.loc[data.brand == 'HONDA', 'modelName'] = data[data.brand ==
                                                    'HONDA'].modelName.str.split()
data.loc[data.brand == 'HONDA', 'modelName'] = data[data.brand ==
                                                    'HONDA'].modelName.apply(honda_fix)


# In[479]:


def skoda_fix(record):
    if record[1] == 'RS':
        return((record[0]+'_RS').upper())
    else:
        return(record[0].upper())


data.loc[data.brand == 'SKODA', 'modelName'] = data[data.brand ==
                                                    'SKODA'].modelName.str.split()
data.loc[data.brand == 'SKODA', 'modelName'] = data[data.brand ==
                                                    'SKODA'].modelName.apply(skoda_fix)


# In[480]:


def audi_fix(record):
    if record[1] == 'RS':
        return((record[0]+'_RS').upper())
    elif record[0] == 'A6' and record[1] == 'allroad':
        return('ALLROAD')
    elif record[1] == 'allroad':
        return(record[0]+'_ALLROAD')
    else:
        return(record[0].replace('-', '_')).upper()


data.loc[data.brand == 'AUDI', 'modelName'] = data[data.brand ==
                                                   'AUDI'].modelName.str.split()
data.loc[data.brand == 'AUDI', 'modelName'] = data[data.brand ==
                                                   'AUDI'].modelName.apply(audi_fix)


# In[481]:


def volvo_fix(record):
    if record[0] == '240':
        return('240_SERIES')
    elif record[0] == 'V40' and record[1] == 'Cross':
        return('V40_CC')
    elif record[1] == 'Cross':
        return(record[0]+'_CROSS_COUNTRY')
    else:
        return(record[0].replace('-', '_')).upper()


data.loc[data.brand == 'VOLVO', 'modelName'] = data[data.brand ==
                                                    'VOLVO'].modelName.str.split()
data.loc[data.brand == 'VOLVO', 'modelName'] = data[data.brand ==
                                                    'VOLVO'].modelName.apply(volvo_fix)


# In[482]:


def nissan_fix(record):
    suffix_list = ['Classic', 'Tino', 'Sylphy',
                   'Coach', 'Z', 'Nismo', 'Regulus']
    if record[1] in suffix_list:
        return(record[0].upper() + '_' + record[1].upper())
    elif record[0] == 'Qashqai+2':
        return('QASHQAI_PLUS_2')
    else:
        return(record[0].replace('-', '_')).upper()


data.loc[data.brand == 'NISSAN', 'modelName'] = data[data.brand ==
                                                     'NISSAN'].modelName.str.split()
data.loc[data.brand == 'NISSAN', 'modelName'] = data[data.brand ==
                                                     'NISSAN'].modelName.apply(nissan_fix)


# In[483]:


def infinity_fix(record):
    return(record[0].upper())


data.loc[data.brand == 'INFINITI', 'modelName'] = data[data.brand ==
                                                    'INFINITI'].modelName.str.split()
data.loc[data.brand == 'INFINITI', 'modelName'] = data[data.brand ==
                                                    'INFINITI'].modelName.apply(infinity_fix)


# In[484]:


old = ['CLA', 'Maybach S-Класс', 'A-Класс', 'B-Класс', 'C-Класс', 'CL-Класс',  'CLK-Класс', 'CLS', 'E-Класс', 'G-Класс', 'GL-Класс', 'GLA', 'GLC',
       'GLE', 'GLK-Класс', 'GLS', 'M-Класс', 'R-Класс', 'S-Класс', 'SL-Класс', 'SLC', 'SLK-Класс', 'SLR', 'V-Класс', 'X-Класс',
       'Maybach GLS']
new = ['CLA_KLASSE', 'S_CLASS_MAYBACH', 'A_KLASSE', 'B_KLASSE', 'C_KLASSE', 'CL_KLASSE',  'CLK_KLASSE', 'CLS_KLASSE', 'E_KLASSE', 'G_KLASSE',
       'GL_KLASSE', 'GLA_CLASS', 'GLC_KLASSE', 'GLE_KLASSE', 'GLK_KLASSE', 'GLS_KLASSE', 'M_KLASSE', 'R_KLASSE',
       'S_KLASSE', 'SL_KLASSE', 'SLC_KLASSE', 'SLK_KLASSE', 'SLR_KLASSE', 'V_KLASSE', 'X_KLASSE',  'MAYBACH_GLS']

for i in range(len(old)):
    data.loc[data.brand == 'MERCEDES', 'modelName'] = data[data.brand ==
                                                           'MERCEDES'].modelName.str.replace(old[i], new[i])


# In[485]:


def mercedes_fix(record):
    if record[1] == 'AMG':
        return(record[0]+'_AMG')
    elif record[1] == 'GT':
        return(record[0]+'_GT')
    elif record[0] == 'GLE_KLASSE' and record[1] == 'Coupe' and record[2] == 'AMG':
        return('GLE_KLASSE_COUPE_AMG')
    elif record[0] == 'GLC_KLASSE' and record[1] == 'Coupe' and record[2] == 'AMG':
        return('AMG_GLC_COUPE')
    elif record[1] == 'Coupe':
        return('GLC_COUPE')
    else:
        return(record[0].upper())


data.loc[data.brand == 'MERCEDES', 'modelName'] = data[data.brand ==
                                                       'MERCEDES'].modelName.str.split()
data.loc[data.brand == 'MERCEDES', 'modelName'] = data[data.brand ==
                                                       'MERCEDES'].modelName.apply(mercedes_fix)


# In[486]:


def toyota_fix(record):
    suffix_list = ['Verso', 'Solara', 'E', 'ED', 'Levin', 'Rumion', 'Spacio', 'Verso',
                   'Exiv', 'Majesta', 'Surf', 'Ace' 'Alpha', 'Sedan', 'Carib', 'Marino', 'Trueno', 'Cypha']
    if record[1] in suffix_list:
        return(record[0].upper() + '_' + record[1].upper())
    elif record[1] == 'Cruiser':
        if record[2] == 'Prado':
            return (record[0].upper() + '_' + record[1].upper() + '_' + record[2].upper())
        return(record[0].upper() + '_' + record[1].upper())
    elif record[0] == 'Corolla' and record[1] == 'II':
        return(record[0].upper() + '_' + record[1].upper())
    elif record[0] == 'Mark' and record[1] in ['II', 'X']:
        if record[2] == 'ZiO':
            return (record[0].upper() + '_' + record[1].upper() + '_' + record[2].upper())
        else:
            return(record[0].upper() + '_' + record[1].upper())
    elif record[0] == 'Rav4':
        return('RAV_4')
    else:
        return(record[0].replace('-', '_')).upper()


data.loc[data.brand == 'TOYOTA', 'modelName'] = data[data.brand ==
                                                     'TOYOTA'].modelName.str.split()
data.loc[data.brand == 'TOYOTA', 'modelName'] = data[data.brand ==
                                                     'TOYOTA'].modelName.apply(toyota_fix)


# In[487]:


def lexus_fix(record):
    return(record[0].upper())


data.loc[data.brand == 'LEXUS', 'modelName'] = data[data.brand ==
                                                    'LEXUS'].modelName.str.split()
data.loc[data.brand == 'LEXUS', 'modelName'] = data[data.brand ==
                                                    'LEXUS'].modelName.apply(lexus_fix)


# In[488]:


def vw_fix(record):
    suffix_list = ['Plus', 'GTI', 'R', 'R32', 'CC']
    if record[1] in suffix_list:
        return(record[0].upper() + '_' + record[1].upper())
    else:
        return(record[0].replace('-', '_')).upper()


data.loc[data.brand == 'VOLKSWAGEN', 'modelName'] = data[data.brand ==
                                                         'VOLKSWAGEN'].modelName.str.split()
data.loc[data.brand == 'VOLKSWAGEN', 'modelName'] = data[data.brand ==
                                                         'VOLKSWAGEN'].modelName.apply(vw_fix)


# In[489]:


def mitsubishi_fix(record):
    suffix_list = ['Cross', 'Evolution', 'Ralliart',
                   'Sport', 'Mini', 'Pinin', 'Gear', 'Runner', 'Star', 'Wagon']
    if record[1] in suffix_list:
        return(record[0].upper() + '_' + record[1].upper())
    elif record[1] == 'D:2':
        return(record[0].upper() + '_D2')
    elif record[1] == 'D:5':
        return(record[0].upper() + '_D_5')
    else:
        return(record[0].replace('-', '_')).upper()


data.loc[data.brand == 'MITSUBISHI', 'modelName'] = data[data.brand ==
                                                         'MITSUBISHI'].modelName.str.split()
data.loc[data.brand == 'MITSUBISHI', 'modelName'] = data[data.brand ==
                                                         'MITSUBISHI'].modelName.apply(mitsubishi_fix)


# In[490]:


# Создаем столбец VENDOR аналогичный test
def vendor_create(record):
    eur = ['SKODA', 'AUDI', 'VOLVO', 'BMW', 'MERCEDES', 'VOLKSWAGEN']
    jap = ['HONDA', 'NISSAN', 'INFINITI', 'TOYOTA', 'LEXUS', 'MITSUBISHI']
    if record in eur:
        return ('EUROPEAN')
    elif record in jap:
        return ('JAPANESE')
    else:
        return(None)
    
data['vendor'] = data.brand.apply(vendor_create)


# In[491]:


#list(data[data.brand == 'MITSUBISHI'].modelName)
#sorted(list(data[data.brand == 'TOYOTA'].modelName.unique()))


# In[492]:


# Заменим опции в data на аналогичные названия в test
options_subst = pd.read_excel('options_subst1.xls')
data.Комплектация = data.Комплектация.str.replace('(','')
data.Комплектация = data.Комплектация.str.replace(')','')

data_option = list(options_subst['data option'])
new_option = list(options_subst['subst'])

for i in range(len(data_option)):
    data.Комплектация = data.Комплектация.str.replace(data_option[i], new_option[i])


# In[493]:


# Конвертируем "строковые" словари с опциями автомобилей в data в простые списки опций
def data_option_fix(record):
    options = []
    if type(record)==str:
        options_dict = json.loads(record)
        for key in options_dict:
            options.extend(options_dict[key])
    return(options)


# In[494]:


#Получаем список уникальных опций в data
#b = []
#for i in range(1, len(data.Комплектация.unique())):
#    a = json.loads(data.Комплектация.unique()[i])
#    for key in a:
#        for el in a[key]:
#            if el not in b:
#                b.append(el)


# In[495]:


# sorted(b)


# In[496]:


data.Комплектация = data.Комплектация.apply(data_option_fix)


# In[497]:


data


# In[511]:


data[data.mileage.isna()]


# In[500]:


# Заполним отсутствующий пробег средним значением для марки автомобиля и года выпуска
avg_mileage = pd.DataFrame(data.dropna(subset=['mileage']).groupby(
    by=['productionDate', 'modelName']).mean()['mileage']).reset_index()
avg_mileage.columns = ['productionDate','modelName', 'avg_mileage' ]

data = data.merge(avg_mileage, on=['productionDate', 'modelName'], how='left')
data.loc[data.mileage.isna(), 'mileage'] = data[data.mileage.isna()].avg_mileage


# In[510]:


# Заполним отсутствующий пробег средним значением для года выпуска
avg_mileage_by_year = pd.DataFrame(data.dropna(subset=['mileage']).groupby(
    by='productionDate').mean()['mileage']).reset_index()
avg_mileage_by_year.columns = ['productionDate','avg_mileage_by_year']

data = data.merge(avg_mileage_by_year, on=['productionDate'], how='left')
data.loc[data.mileage.isna(), 'mileage'] = data[data.mileage.isna()].avg_mileage_by_year


# In[512]:


# То что не заполнилось 
data.dropna(subset=['mileage'], inplace = True)


# In[516]:


# Убираем промежуточные колонки
data.drop(['avg_mileage', 'avg_mileage_by_year'], axis=1, inplace=True)


# In[533]:


columns_new = ['car_url', 'bodyType', 'brand', 'color', 'fuelType', 'modelDate', 'model_name', 'name', 'numberOfDoors', 'productionDate', 'vehicleTransmission',
               'engineDisplacement', 'enginePower', 'description', 'mileage', 'equipment_dict', 'Привод', 'Руль', 'Состояние', 'Владельцы', 'ПТС', 'Таможня', 'Владение', 'Price', 'vendor']


# In[534]:


data.columns=columns_new


# In[535]:


columns_new = [
    'bodyType',
    'brand',
    'car_url',
    'color',
    'description',
    'engineDisplacement',
    'enginePower',
    'equipment_dict',
    'fuelType',
    'mileage',
    'modelDate',
    'model_name',
    'name',
    'numberOfDoors',
    'productionDate',
    'vehicleTransmission',
    'vendor',
    'Владельцы',
    'Владение',
    'ПТС',
    'Привод',
    'Руль',
    'Состояние', 
    'Таможня',
    'Price'
]


# In[536]:


data = data[columns_new] 


# In[537]:


data.info()


# In[552]:


# Сохраняем датасет

data.to_csv('cars_data.csv', index=False)

