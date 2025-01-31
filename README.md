
# Проект Foodgram

«Фудграм» — сайт, на котором пользователи будут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

Адрес: https://foodgramik.hopto.org/

## Технологии:


![Python](https://img.shields.io/badge/Python-3.9.13-blue)
![Django](https://img.shields.io/badge/Django-3.2.16-green)
![DjangoRestFramework](https://img.shields.io/badge/DjangoRestFramework-3.12.4-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13.10-green)
![Docker](https://img.shields.io/badge/Docker-24.0.5-blue)

![Docker](https://img.shields.io/badge/lang-ru-red)

## Особенности реализации
- Проект запускается в четырёх контейнерах — gateway, db, backend и frontend;
- Образы foodgram_frontend, foodgram_backend и foodgram_gateway запушены на DockerHub;
- Реализован workflow c автодеплоем на удаленный сервер и отправкой сообщения в Telegram;

## Развертывание на локальном сервере

- Создать .env на основе указанного ниже примера. Указав валидные данные для подключения.
```python
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
POSTGRES_DB=foodgram
DB_HOST=db
DB_PORT=5432
SECRET_KEY='your_secret_key
ALLOWED_HOSTS=11.111.111.11,some.domain.org,127.0.0.1,localhost
DEBUG=True
```
- Установите Docker и docker-compose.
- Запустите docker compose, выполнив команду: `docker compose -f docker-compose.yml up --build -d`.
- Выполните миграции: `docker compose -f docker-compose.yml exec backend python manage.py migrate`.
- Создайте суперюзера: `docker compose -f docker-compose.yml exec backend python manage.py createsuperuser`.
- Соберите статику: `docker compose -f docker-compose.yml exec backend python manage.py collectstatic`.
- Заполните базу ингредиентами: `docker compose -f docker-compose.yml exec backend python manage.py load_ingredients`.
- Зайдите в админку и создайте теги для рецептов.
  
## Автор
backend: <span style="color: green;">*Покуц Александра*</span> (tashka.zzz@yandex.ru)
