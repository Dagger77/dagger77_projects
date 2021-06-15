#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import numpy as np
import pickle

from flask import Flask, request
app = Flask(__name__)

# десериализуем ранее сохраненную модель
with open('test_model.pkl', 'rb') as pkl_file:
    regressor = pickle.load(pkl_file)


# In[ ]:


### Функция обрабатывает переданное значение и возвращает предсказание модели
def model_predict(value):
    value_to_predict = np.array(value).reshape(-1, 1)
    return regressor.predict(value_to_predict)


# In[ ]:


@app.route('/predict')
def predict_func():
    value = request.args.get('value')
    try:
        prediction = model_predict(float(value)) #Приводим к типу float
    except ValueError: #обрабатываем ошибку, когда передан не числовой параметр
        return 'Необходимо ввести число'
    except TypeError: #обрабатываем ошибку, когда обращение к серверу не содержит параметра  
        return 'Не передан параметр'
    
    return f'the result is {prediction[0]}'

if __name__ == '__main__':
    app.run('localhost', 5000)

