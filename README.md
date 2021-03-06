# Job Salary Prediction
## Предсказание уровня зарплатных ожиданий сотрудника в зависимости от региона, пола, должности и стажа работы

<b>Практическая применимость:</b> в HR-отделах крупных компаний, использующих данные мониторинга рынка труда для принятия управленческих решений о приёме сотрудника на ту, или иную позицию.

## Бизнес-идея

[![Open In Sheets](https://playit.sg/sites/default/files/pictures/google-slides.png)](https://docs.google.com/presentation/d/15DaUDmSKWrMrL1AhAlCBIXSLYfat2_Pm5mlxdejNhtc/edit?usp=sharing)

## Техническая реализация

### 1. Сбор и предобработка данных с сайта HH.ru для POC

Для продакшн решения потребуется подключение API.

Модули для сбора данных находятся в директории `parser`. Результатом работы парсера является файл `*.csv`, который далее будет использоваться для обучения модели `CatBoostRegressor`, которая способна работать как с данными типа `int`, так и с данными типа `object(str)` и теоретически показывает неплохие результаты на высокоуровневых данных.

https://github.com/DmitriyKhodykin/JobSalaryPrediction/blob/master/parser/hh_parser.py

```
class Parser:
    """Парсинг данных из резюме HH.ru"""
    
        def get_refs(self):
        """Возвращает ссылки на резюме кандидатов"""
        
        def get_features(self, ref):
        """Возвращает нужные признаки из каждого резюме кандидата
        с предварительной обработкой признаков"""
        
        def csv_creator():
        """Создает файл csv c данными"""
```

### 2. Изучение исходных данных

Собранные парсером данные, а также их визуализация, находятся в директории `data`.

https://github.com/DmitriyKhodykin/JobSalaryPrediction/tree/master/data

```
RangeIndex: 3178 entries, 0 to 3177
Data columns (total 12 columns):
 #   Column      Non-Null Count  Dtype         
---  ------      --------------  -----         
 0   Unnamed: 0  3178 non-null   int64         
 1   entrydate   3178 non-null   datetime64[ns]
 2   title       3178 non-null   object        
 3   position    3178 non-null   object        
 4   gender      3178 non-null   object        
 5   city        3178 non-null   object        
 6   age         3178 non-null   int64         
 7   salary      3178 non-null   int64         
 8   experience  2522 non-null   float64       
 9   last_job    3178 non-null   object        
 10  updated     3178 non-null   datetime64[ns]
 11  link        3178 non-null   object        
dtypes: datetime64[ns](2), float64(1), int64(3), object(6)
```

Данные требуют дополнительной обработки, т.к. содержат пропуски в столбце `experience`, а также неподходящий для модели тип данных `float`. Но это не помешает подробнее взглянуть на данные "по сути".

![](/data/report.png)

Как видно, наибольшее количество позиций из г.Москвы и г.Санкт-Петербурга. Наиболее часто встречающиеся должности - Торговый представитель, Менеджер по продажам, Региональный менеджер (РМ). Среднее значение по желаемому уровню оплаты труда - 64 790 р. (net). Образ наиболее часто встречающегося на рынке кандидата: Мужчина до 40 лет, с опытом работы ок. 20 лет. При этом, сильной корреляции между высокими зарплатными ожиданиями и опытом работы - на среднем нижнем графике - не наблюдается.

Интересной выглядит информация о предыдущем месте работы кандидата, т.к. в крупных компаниях уровень оплаты труда обычно выше. Также выше уровень в международных компаниях в сравнении с национальными бизнесами. Однако наименования работодателей не типизированы, отсутствуют однозначные признаки, например ИНН. В связи с этим высок риск ошибки при использованнии не однозначно трактуемых, мусорных данных. Поэтому ограничимся в модели данными о регионе проживания кандидата, желаемой должности, а также данными о гендерных и возрастных особенностях кандидата.

### 3. Подготовка данных и построение модели

Предобработка данных и построение модели реализовано в ноутбуке `JSP_Model.ipynb` в директории `/model`. Рассмотрим подробнее этот этап по ссылке 
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DmitriyKhodykin/JobSalaryPrediction/blob/master/model/JSP_Model.ipynb)

### 4. Развертка сервиса в продакшн на виртуальном сервере

Конфигурация развертки предобученной модели машинного обучения – Job Salary Prediction: nginx + uwsgi + Flask + Docker Compose на виртуальном сервере под управлением Ubuntu 20.04. Файлы конфигурации в директории `/service` и `/etc`.

![](/service/jsp_srv_pic.png)

https://github.com/DmitriyKhodykin/JobSalaryPrediction/tree/master/service

`/service`

- `/docker` - файлы Docdker и docker-compose
- `jsp.py` - модуль для "обвязки" модели декоратором Flask
- `wsgi.py` - точка входа в приложение
- `jsp.ini` - файл конфигурации uwsgi
- `requirements.txt` - перечень требуемых библиотек с указанием версий для установки внутри виртуального энвайронмента `venv`

`/etc`

https://github.com/DmitriyKhodykin/JobSalaryPrediction/tree/master/etc

- `systemd/system/jsp.service` - конфигурация для запуска сервиса jsp через systemd
- `nginx/sites-available/jsp` - конфигурация nginx

После конфигурирования `nginx` необходимо активировать конфигурацию `sudo ln -s /etc/nginx/sites-available/jsp /etc/nginx/sites-enabled/`

### 5. Использование сервиса

#### WEB UI

Web-интерфейс приложения находится по адресу `http://0.0.0.0:80/`

![](/service/web_ui.png)

https://github.com/DmitriyKhodykin/JobSalaryPrediction/tree/master/service/templates

#### Запросы к API

`/jsp` - GET. Возвращает предсказание зарплатных ожиданий сотрудника в зависимости от региона, пола, должности и стажа работы.

Пример запроса через API:

```
import requests
import json


def get_predict_salary():
    """Отправка GET-запроса на сервер для предсказания
    ожидаемого сотрудником уровня дохода.

    position - наименование должности (из endpoint /positions);
    gender - пол (Мужчина; Женщина);
    city - город проживания;
    age - возраст, лет;
    experience - опыт работы, лет"""

    headers = {'Content-Type': 'application/json; charset=utf-8'}

    r_predict = requests.request("GET", "http://0.0.0.0:80/jsp",
                                 headers=headers,
                                 data='''{
                                 "position": "Супервайзер",
                                 "gender": "Мужчина",
                                 "city": "Воронеж",
                                 "age": 40,
                                 "experience": 10
                                 }'''.encode('utf-8'))
    predict = json.loads(r_predict.text.encode('utf8'))

    return predict


if __name__ == '__main__':
    print(get_predict_salary())

```

#### Пример ответа:

```
{"JobSalaryPrediction, RUR": 50 000}
```

### Результат

1) Подготовлена модель, предсказывающая уровень зарплатных ожиданий сотрудника в зависимости от ряда входных параметров, `MAPE = 4%`. 

2) Модель "упакована" в сервис  путем обвзязки декоратором Flask, с последующей контейнеризацией при помощи Doccker и docker-compose на сервере. Точкой входа в приложение является сервер приожений uwsgi, который позволяет распараллелить запросы к модели. Сервис "слушает" запросы на 80-м порту через сервер nginx и готов к оперативной выдаче предсказаний о вероятном уровне желаемого дохода сотрудника в ответ на стандартный http-запрос. <i>Конфигурация сервиса с применением nginx, uwsgi, docker  делает сервис воспроизводимым и пригодным для промышленной эксплуатации в корпоративной среде в соответствии с актуальными деловыми практиками отрасли Data Science</i>.
