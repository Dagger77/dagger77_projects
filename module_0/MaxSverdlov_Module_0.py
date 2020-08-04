#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import numpy as np

def score_game(game_core):
    '''Запускаем игру 1000 раз, чтобы узнать, как быстро игра угадывает число'''
    
    count_ls = []
    np.random.seed(1)  # фиксируем RANDOM SEED, для воспроизводимости эксперимента
    random_array = np.random.randint(1,101, size=(1000))
    
    for number in random_array:
        count_ls.append(game_core(number))
    score = int(np.mean(count_ls))
    print(f"Ваш алгоритм угадывает число в среднем за {score} попыток")
    
    return(score)

def game_core_v3(number):
    '''Функция принимает загаданное число и возвращает число попыток.
       В качестве первой попытки берется случайное число, а затем уменьшаем или увеличиваем его в зависимости от того,
       больше оно или меньше загаданного.'''
    
    count = 1
    predict = np.random.randint(1,101) 
    predict_low = 0    # Начальная нижняя граница диапазона, которому принадлежит загаданное число.  
    predict_high = 101 # Начальная верхняя граница диапазона, которому принадлежит загаданное число.  
    
    while number != predict:
        count += 1
        # Eсли загаданное число больше текущего предсказания, сдвигаем вверх нижнюю границу диапазона предсказаний,
        # новое предсказание устанавливаем в середине диапазона.
        if number > predict: 
            predict_low = predict 
            predict += (predict_high - predict)//2 
        # Eсли загаданное число меньше текущего предсказания, сдвигаем вниз верхнюю границу диапазона предсказаний,
        # новое предсказание устанавливаем в середине диапазона
        elif number < predict:
            predict_high = predict 
            predict -= (predict - predict_low)//2 
    
    return(count) 

