# Django сервис друзей
_Сдлано на django-rest-framework_
## Установка и запуск
1. Клонируем проект `git clone https://github.com/savlagood/django-friend-service.git`
2. Собираем докер образ, а затем запускаем его:
```
docker build . vk-friends
docker run -d -p 8090:8000 --tag vk-friends
```
## Примеры использования
Подробная спецификация по использованию лежит в файле `openapi-schema.yml`. Здесь приведем лишь несколько примеров:
1. GET http://127.0.0.1:8090/api/socnet/users/ - получим список пользователей, например:
```
[
    {
        "id": 1,
        "username": "petr"
    },
    {
        "id": 2,
        "username": "vasiliy"
    },
    {
        "id": 5,
        "username": "boris"
    }
]
```
2. POST http://127.0.0.1:8090/api/socnet/users/ - отправив подобный запрос с телом:
```
{"username": "kate"}
```
получим следующий ответ (конечно, если такой пользователь еще не создан):
```
{
    "id": 6,
    "friends": [],
    "outgoing_requests": [],
    "incoming_requests": [],
    "username": "kate"
}
```

Остальные примеры есть в OpenAPI спецификации