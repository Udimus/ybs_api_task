# ybs_api_task
REST API для вступительного задания в ШБРЯ.

### Установка
Подразумевается, что в месте установки нет проблем с доступом в интернет. В противном случае в соотвествующие места вызова докера понадобится добавить информацию о прокси.

Сперва установим и настроим docker:

```bash
sudo apt  install docker.io
sudo apt  install docker-compose
```

Нам нужно добавить себя в группу docker, чтобы не писать всё время sudo:

```bash
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker
```

Заранее скачаем нужные нам образы:

```bash
docker pull postgres:alpine
docker pull python:3.6-slim-stretch
```


### Запуск всего сервиса

В директории проекта:

```bash
docker-compose up -d
```

Первый раз это займёт некоторое время на сборку build'а для сервиса.


### Тесты

#### Unittests

Юниттесты имеются для той части, где проверяются входные данные. Эмулировать базу данных для юниттестов функций, общающихся с ней, я не стал.
Для них сперва установим зависимости

```bash
pip install -r test/test_requirements.txt
```

Затем запустим командой `pytest`

Результаты можно пронаблюдать, набрав 

```bash
pycobertura show coverage.xml
```

#### Load testing

Установим Apache Benchmark

```bash
sudo apt-get install apache2-utils
```


Протестируем GET-запросы из большой (10000 жителей) таблицы.

```bash
python test/load_testing/api_load_testing.py -a 'http://0.0.0.0:8080'
```

Вместо локального адреса подставляем тот, где расположен наш сервис.

Также можно настроить размер импорта, количество родственных связей, количество городов, а также количество запросов, которыми мы будем простукивать сервис и то, насколько они будут параллельны.

```bash
python test/load_testing/api_load_testing.py --help
usage: api_load_testing.py [-h]
                           [-v {CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET}]
                           [-n CITIZENS] [-p PAIRS] [-t TOWNS]
                           [-c CONCURRENCY] [-r REQUESTS] -a ADDRESS

Load testing of our service.

optional arguments:
  -h, --help            show this help message and exit
  -v {CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET}, --verbose {CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET}
                        Set output verbosity level.
  -n CITIZENS, --citizens CITIZENS
  -p PAIRS, --pairs PAIRS
                        Relationships number.
  -t TOWNS, --towns TOWNS
  -c CONCURRENCY, --concurrency CONCURRENCY
                        Number of multiple requests to make at a time
  -r REQUESTS, --requests REQUESTS
                        Number of requests to perform
  -a ADDRESS, --address ADDRESS
                        Address to test.
```


### Что можно сделать лучше

* Разобраться с SQLAlchemy и её связкой с Flask -- возможно, держать всё время соединение с БД лучше;
* Больше узнать, как устроено логирование с Flask (и вообще, что это за сущность -- app);
* Каждый раз считать максимальный номер таблицы, чтобы присвоить очередной таблице итерируемый номер -- так себе затея. Но альтернативные варианты (просто считать число таблиц... хранить на диске (в контейнере?) файл с этим числом итератором... назначать номер из текущего таймстемпа...) выглядят ещё более сомнительными;
* Есть ещё такая тема, как SQL-инъекции. По идее, как раз средства psycopg2 должны от них защищать, а на деле -- не понятно. Вообще, очень интересно, где человеческие базы данных, которым можно передать сразу файл...
* Заодно надо бы разобраться, что такое схемы -- и нужно ли в такой задаче ограничивать доступ;
* Обновление родственных отношений можно было бы переложить на SQL-часть;
* Тестирование стоило бы автоматизировать и агрегировать результат;
* Для расширения пропускной способности, во-первых, можно поменять конфиг-файл в Postgres (нужно ли пересобирать образ?), во-вторых, разобраться, что вообще при этом происходит и как и чем (Flask?) это можно обрабатывать.