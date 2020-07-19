# Job Salary Prediction
## Предсказание уровня зарплатных ожиданий сотрудника в зависимости от региона, пола, должности и стажа работы

<b>Практическая применимость:</b> в HR-отделах крупных компаний, использующих данные мониторинга рынка труда для принятия управленческих решений о приёме сотрудника на ту, или иную позицию.

## Бизнес-идея

![](/presentation/asis.png)

Зачастую, даже в крупных компаниях, перед размещением объявления о поиске сотрудника на "хантинговых" сервисах, рекрутеры по-старинке проводят мониторинг зарплатных ожиданий кандидатов на тех же самых ресурсах. Мониторинг сводится к просмотру существующих вакансий и резюме, переносу данных об ожидаемых зарплатах в таблицу excel, после чего данные усредняются. При этом, далеко не всегда учитываются даже базовые параметры кандидатов, такие как регион проживания, возраст, опыт работы и др. Как результат столь трудоемкой работы - не всегда корректные выводы об уровне ожидаемого дохода кандидатов, и как следствие, - их низкий поток на этапе отбора.

![](/presentation/tobe.png)

Для оптимизации работы рекрутеров, а также для ускорения принятия управленческих решений, предлагается создать web-сервис, который в ответ на запрос с указанием региона, пола, должности и стажа работы сотрудника будет возвращать предсказание о его зарплатных ожиданиях.

Внутри сервиса будет размещена обученная на данных портала HH.ru модель, "усредняющая" ожидания кандидатов со схожими характеристиками. После обучения модели на актуальных данных, она сможет выдавать актуальные предсказания, облегчая работу рекрутера.

## Техническая реализация

### 1. Сбор и предобработка данных с сайта HH.ru

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

Предобработка данных и построение модели реализовано в ноутбуке `JSP_Model.ipynb` в директории `/model`. Рассмотрим подробнее этот этап по ссылке.

https://github.com/DmitriyKhodykin/JobSalaryPrediction/blob/master/model/JSP_Model.ipynb

### 4. Развертка сервиса в продакшн на виртуальном сервере

Конфигурация развертки предобученной модели машинного обучения – Job Salary Prediction (CatBoostReg): nginx + uwsgi + Flask на виртуальном сервере под управлением Ubuntu 20.04. Файлы конфигурации в директории `/service` и `/etc`.

![](/service/jsp_service_pic.png)

`/service`

- `jsp.py` - модуль для "обвязки" модели декоратором Flask
- `wsgi.py` - точка входа в приложение
- `jsp.ini` - файл конфигурации uwsgi
- `requirements.txt` - перечень требуемых библиотек с указанием версий для установки внутри виртуального энвайронмента `venv`

`/etc`

- `systemd/system/jsp.service` - конфигурация для запуска сервиса jsp через systemd
- `nginx/sites-available/jsp` - конфигурация nginx

После конфигурирования `nginx` необходимо активировать конфигурацию `sudo ln -s /etc/nginx/sites-available/jsp /etc/nginx/sites-enabled/`

### 5. Использование сервиса

`/positions` - GET. Возвращает список должностей:

['Супервайзер', 'Руководитель продаж', 'Менеджер по продажам', 'Администратор']

`/jsp` - GET. Возвращает предсказание зарплатных ожиданий сотрудника в зависимости от региона, пола, должности и стажа работы.

#### Пример запроса:

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

    r_positions = requests.request("GET", "http://0.0.0.0:81/positions")

    r_predict = requests.request("GET", "http://0.0.0.0:81/jsp",
                                 headers=headers,
                                 data='''{
                                 "position": "Супервайзер",
                                 "gender": "Мужчина",
                                 "city": "Воронеж",
                                 "age": 40,
                                 "experience": 10
                                 }'''.encode('utf-8'))

    positions = json.loads(r_positions.text.encode('utf8'))
    predict = json.loads(r_predict.text.encode('utf8'))

    return positions, predict


if __name__ == '__main__':
    print(get_predict_salary()[0],
          '\n', '\n',
          get_predict_salary()[1])

```

#### Пример ответа:

```
{'Positions:': ['Администратор', 'Коммерческий директор', 'Курьер', 'Менеджер по закупкам', 
'Менеджер по продажам', 'Региональный менеджер', 'Руководитель продаж', 'Супервайзер']} 

{"JobSalaryPrediction, RUR": 50 000}
```

<b>
 Результат: сервис развернут на сервере и запускается вместе с ним. При отказах и падениях, - перезапускается автоматически. Сервис "слушает" запросы на 81-м порту и готов к оперативной выдаче предсказаний о вероятном уровне желаемого дохода сотрудника в ответ на стандартный http-запрос. Конфигурация сервиса с применением nginx и uwsgi делает сервис экономичным (потребляет от 25 до 100 МБ ОЗУ в режиме ответа на запрос) и пригодным для промышленной эксплуатации в корпоративной среде.
</b>
