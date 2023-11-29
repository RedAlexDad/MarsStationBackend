from rest_framework.permissions import BasePermission
from bmstu_lab.models import Users

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response

import jwt
from datetime import datetime, timezone

KEY = settings.JWT["SIGNING_KEY"]
ALGORITHM = settings.JWT["ALGORITHM"]
ACCESS_TOKEN_LIFETIME = settings.JWT["ACCESS_TOKEN_LIFETIME"]
REFRESH_TOKEN_LIFETIME = settings.JWT["REFRESH_TOKEN_LIFETIME"]

# ==================================================================================
# СУБД хранение сессий
# ==================================================================================
import redis

# Подключение Redis
# sudo service redis-server start
session_storage = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)


# Просмотр конфигурации
# redis-server
# Просмотр статус
# sudo service redis-server status
# Остановка сервера Redis:
# redis-cli shutdown
# Если бесполезно, то
# sudo service redis-server stop
# Либо убить его
# ps aux | grep redis
# sudo kill <PID>

# Удаление файла данных Redis:
# По умолчанию файл данных Redis называется dump.rdb и находится в рабочем каталоге сервера. Удалите этот файл, чтобы удалить данные:
# rm /path/to/your/redis/dump.rdb
# Перезагрузка сервера
# sudo service redis-server restart
# https://redis.io/docs/connect/clients/python/

# Просмотр созданных токенов
# keys *
def add_in_blacklist(access_token):
    error_message = None
    token_exists = None
    # Получение имени пользователя из Redis по токену
    try:
        # Добавление токена в черный список в Redis
        blacklist_key = 'jwt_blacklist'
        session_storage.set(blacklist_key, access_token)
        # Проверка токена в ЧС
        token_exists = session_storage.exists(blacklist_key, access_token)
    except Exception as error:
        error_message = {'redis_status': False, 'error': str(error)}
        print('Ошибка соединения с Redis. \nLOG:', error)

    return error_message, token_exists

def create_access_token(user):
    # Create initial payload
    payload = {
        "token_type": "access",
        "exp": datetime.now(tz=timezone.utc) + ACCESS_TOKEN_LIFETIME,
        "iat": datetime.now(tz=timezone.utc),
    }
    # Add given arguments to payload
    payload["id"] = user.id
    # Create Token
    access_token = jwt.encode(payload, KEY, algorithm=ALGORITHM)

    try:
        # Хранение токена в REDIS
        session_storage.set(access_token, user.id)
        error_message = {}
    except Exception as error:
        error_message = {'redis_status': False, 'error': str(error)}
        print('Ошибка соединения с Redis. \nLOG:', error)

    return error_message, access_token


def create_refresh_token(user):
    # Create initial payload
    payload = {
        "token_type": "refresh",
        "exp": datetime.now(tz=timezone.utc) + REFRESH_TOKEN_LIFETIME,
        "iat": datetime.now(tz=timezone.utc),
    }
    # Add given arguments to payload
    payload["id"] = user.id
    # Create token
    token = jwt.encode(payload, KEY, ALGORITHM)
    return token


def get_jwt_payload(access_token):
    payload = jwt.decode(access_token, KEY, algorithms=[ALGORITHM])
    return payload


def get_access_token(request):
    error_message = None
    access_token = request.COOKIES.get('access_token')

    if access_token is None:
        access_token = request.data.get('access_token')

    if access_token is None:
        access_token = request.headers.get("authorization")

    # Получение имени пользователя из Redis по токену
    try:
        stored_username = session_storage.get(access_token)
        if not stored_username:
            return Response({'message': 'Token is not valid'}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as error:
        error_message = {'redis_status': False, 'error': str(error)}
        print('Ошибка соединения с Redis. \nLOG:', error)

    return error_message, access_token


def get_refresh_token(request):
    refresh_token = request.COOKIES.get('refresh_token')

    if refresh_token is None:
        refresh_token = request.data.get('refresh_token')

    return refresh_token


class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        access_token = get_access_token(request)

        if access_token is None:
            return False
        else:
            if isinstance(access_token, tuple):
                access_token = access_token[1]

        try:
            payload = get_jwt_payload(access_token)
        except Exception as error:
            print(error)
            return False

        try:
            user = Users.objects.get(pk=payload["id"])
        except Exception as error:
            print(error)
            return False

        return user.is_active


class IsModerator(BasePermission):
    def has_permission(self, request, view):
        access_token = get_access_token(request)

        if access_token is None:
            return False
        else:
            if isinstance(access_token, tuple):
                access_token = access_token[1]

        try:
            payload = get_jwt_payload(access_token)
        except Exception as error:
            print(error)
            return False

        try:
            user = Users.objects.get(pk=payload["id"])
        except Exception as error:
            print(error)
            return False

        return user.is_moderator
