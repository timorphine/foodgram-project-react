# FOODGRAM

Foodgram - это сервис для публикации рецептов. Пользователи могут создавать рецепты, добавлять понравившиеся в избранное, подписываться на их авторов, а так же удобно скачивать список ингредиентов в PDF.

## Шаблон наполнения ENV-файла
DB_ENGINE=django.db.backends.postgresql \
DB_NAME=postgres \
POSTGRES_USER=Имя-пользователя-БД \
POSTGRES_PASSWORD=Пароль-БД \
DB_HOST=db \
DB_PORT=5432 \
SECRET_KEY = Секретный ключ Django

## Запуск приложения в контейнерах
Параметры запуска описаны в файлах docker-compose.yml и nginx.conf которые находятся в директории infra/.
При необходимости добавьте/измените адреса проекта в файле nginx.conf

Из директории с файлом docker-compose.yaml выполните команду: \
```docker-compose up -d --build```

## Наполнение БД
Выполните миграции:
```docker-compose exec infra-backend-1 python manage.py migrate```

Загрузите ингредиенты:
```docker-compose exec infra-backend-1 python manage.py load_data```

Загрузите теги:
```docker-compose exec infra-backend-1 python manage.py load_tags```

Соберите статику:
```docker-compose exec infra-backend-1 python manage.py collectstatic --noinput```

Создайте администратора:
```docker-compose exec infra-backend-1 python manage.py createsuperuser```

## Документация к API

Документация к API создана с помощью redoc и доступна по адресу ```/api/redoc```

