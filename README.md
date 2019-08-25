# ybs_api_task
REST API для вступительного задания в ШБРЯ.

### Установка
Сперва установим и настроим docker:

`sudo apt  install docker.io`

`sudo apt  install docker-compose`

Нам нужно добавить себя в группу docker, чтобы не писать всё время sudo:

`sudo groupadd docker`

`sudo usermod -aG docker $USER`

Заранее скачаем нужные нам образы:

`docker pull postgres:alpine`

`docker pull python:3.6-slim-stretch`


### Запуск всего сервиса
