# Job Salary Prediction
## Предсказание уровня зарплатных ожиданий сотрудника в зависимости от региона, пола, должности и стажа работы

### 1. Сбор данных для модели о зарплатных ожиданиях сотрудников на сайте HH.ru
Модули для сбора данных находятся в директории `parser`

### 2. Изучение исходных данных
Собранные неподготовленные данные, а также их визуализация, находятся в директории `data`

![](/data/report.png)

### 3. Подготовка данных и построение модели
Предобработка данных и построение модели реализовано в ноутбуке `JSP_Model.ipynb` в директории `model`

* Вид подготовленных данных:

 ```
    position                | gender    | city    | age   | salary  | experience 
    -----------------------------------------------------------------------------
    0 Менеджер по продажам  | Женщина   | Москва  | 31    | 70      | 8
    1 Клиентский менеджер   | Мужчина   | Липецк  | 40    | 90      | 15
    2 Супервайзер           | Мужчина   | Самара  | 34    | 50      | 7
 ```

* Гиперпараметры модели:

```
RANDOM_SEED = 42
VERSION = 11
VAL_SIZE = 0.2
N_FOLDS = 5
ITERATIONS = 2000
LR = 0.01
```

* Обучение модели:

```
  model = CatBoostRegressor(
      iterations=ITERATIONS, 
      learning_rate=LR, 
      random_seed=RANDOM_SEED,
      eval_metric='MAPE', 
      custom_metric=['R2', 'MAE']
      )
  
  model.fit(
      X_train, y_train, 
      cat_features=cat_features_ids,
      eval_set=(X_test, y_test), 
      verbose_eval=100, 
      use_best_model=True, 
      plot=True
      )
```

* Оценка модели (MAPE - Mean Absolute Percent Error):

```
bestTest = 0.222457398
bestIteration = 1861
```

* Сериализация модели:

Сериализация модели реализована с помощью модуля `pickle`, сериализованная модель `jsp_model.pkl` находится в директории `model` 

### 4. Развертка сервиса в продакшн на виртуальном сервере

Конфигурация развертки предобученной модели машинного обучения – Job Salary Prediction (CatBoostReg): nginx + uwsgi + Flask на виртуальном сервере под управлением Ubuntu 20.04. Файлы конфигурации в директории `service`

![](/service/jsp_service_pic.png)

### 5. Использование сервиса

`/positions` - GET. Возвращает список должностей:

['Супервайзер', 'Руководитель продаж', 'Менеджер по продажам', 'Администратор']

`/jsp` - GET. Возвращает предсказание зарплатных ожиданий сотрудника в зависимости от региона, пола, должности и стажа работы

* Пример запроса:

```
import requests
import json


r = requests.request("GET", "http://0.0.0.0:80/jsp",
                     data='''{
                     "position": "Супервайзер",
                     "gender": "Мужчина",
                     "city": "Воронеж",
                     "age": 40,
                     "experience": 5
                     }'''

response = json.loads(r.text.encode('utf8'))
print(response)
```

* Пример ответа:

```
{"JobSalaryPrediction, RUR": 50 000}
```
