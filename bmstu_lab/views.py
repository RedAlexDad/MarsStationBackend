import requests
from rest_framework.views import APIView
from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema

from django.contrib.auth import authenticate, login, logout
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated, BasePermission, IsAdminUser
from django.conf import settings

from bmstu_lab.serializers import UsersSerializer, UserRegisterSerializer, UserAuthorizationSerializer, \
    EmployeeSerializer
from bmstu_lab.models import Users, Employee
import jwt, datetime

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

# ==================================================================================
# АККАУНТЫ
# ==================================================================================
from rest_framework import status
from django.shortcuts import get_object_or_404


class UsersGET(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAdminUser]
    model_class = Users
    serializer_class = UsersSerializer

    def get(self, request, format=None):
        print('[INFO] API GET [UsersINFO]')
        users = self.model_class.objects.all()
        serializer = self.serializer_class(users, many=True)
        return Response(serializer.data)


class UsersPUT(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAdminUser]
    model_class = Users
    serializer_class = UserRegisterSerializer

    @swagger_auto_schema(request_body=serializer_class)
    def put(self, request, pk, format=None):
        print('[INFO] API PUT [UsersINFO]')
        users = get_object_or_404(self.model_class, pk=pk)
        serializer = self.serializer_class(users, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsersDELETE(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAdminUser]
    model_class = Users

    def delete(self, request, pk, format=None):
        print('[INFO] API DELETE [UsersINFO]')
        users = get_object_or_404(self.model_class, pk=pk)
        users.delete()
        return Response(data={'message': 'Successfully'}, status=status.HTTP_204_NO_CONTENT)


# ==================================================================================
# СОТРУДНИКИ
# ==================================================================================

class EmployeeClass(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    model_class = Employee
    serializer_class = EmployeeSerializer

    def get(self, request, format=None):
        print('[INFO] API GET [Employee GET]')
        employees = self.model_class.objects.all()
        serializer = self.serializer_class(employees, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=serializer_class)
    def post(self, request, format=None):
        print('[INFO] API GET [Employee POST]')
        # Проверим на наличие объекта с заданным pk
        try:
            user = Users.objects.get(pk=request.data['id_user'])
        except Users.DoesNotExist:
            return Response(f"ERROR! Object Users there is no such object by ID!",
                            status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            request.data.pop('id_user', None)
            Employee.objects.create(id_user_id=user.id, **request.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=serializer_class)
    def put(self, request, pk, format=None):
        print('[INFO] API PUT [Employee PUT]')
        users = get_object_or_404(self.model_class, pk=pk)
        serializer = self.serializer_class(users, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==================================================================================
# РЕГИСТРАЦИЯ, АУТЕНФИКАЦИЯ, АВТОРИЗАЦИЯ, ВЫХОД С УЧЕТНОЙ ЗАПИСИ
# ==================================================================================
class RegisterView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=UserRegisterSerializer)
    def post(self, request):
        user_data = {
            "username": request.data['username'],
            "password": request.data['password'],
            "is_superuser": request.data['is_superuser'],
            "is_staff": request.data['is_staff']
        }
        try:
            user_serializer = UserRegisterSerializer(data=user_data)
            user_serializer.is_valid(raise_exception=True)
            user_instance = user_serializer.save()
            id_user = user_instance.id

            employee_data = {
                "full_name": request.data['full_name'],
                "post": request.data['post'],
                "name_organization": request.data['name_organization'],
                "address": request.data['address'],
                "id_user": id_user
            }
            try:
                employee_serializer = EmployeeSerializer(data=employee_data)
                employee_serializer.is_valid(raise_exception=True)
                employee_serializer.save()

                return Response(data={"user": user_serializer.data, "employee": employee_serializer.data})
            except AssertionError as error:
                return Response(data={"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return Response(data={"error": str(error)}, status=status.HTTP_404_NOT_FOUND)


class LoginView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=UserAuthorizationSerializer)
    def post(self, request):
        username = request.data['username']
        password = request.data['password']

        user = Users.objects.filter(username=username).first()

        if user is None:
            raise AuthenticationFailed('User not found!')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password!')

        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')
        try:
            # Хранение токена в REDIS
            session_storage.set(token, username)
            error_message = {}
        except Exception as error:
            error_message = {'redis_status': False, 'error': str(error)}
            print('Ошибка соединения с Redis. \nLOG:', error)

        response = Response(status=status.HTTP_200_OK)
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'message': 'Successfully',
            'jwt': token,
        }

        # Добавляем error_message, если есть ошибка
        if error_message:
            response.data['error_message'] = error_message

        return response


class UserView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    # permission_classes = [IsAuthenticated]
    permission_classes = []

    def post(self, request):
        # Получение токена из хранилища (Redis)
        token = request.COOKIES.get('jwt')

        # token = request.headers.get('Authorization', None).replace('Bearer ', '')

        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        # Получение имени пользователя из Redis по токену
        stored_username = session_storage.get(token)

        if not stored_username:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        user = Users.objects.filter(id=payload['id']).first()
        serializer = UserAuthorizationSerializer(user)
        return Response(serializer.data)


class LogoutView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = Response()

        # Проверка наличия токена
        if 'jwt' not in request.COOKIES:
            raise ValidationError({'error': 'No JWT token found. You are already logged out'})

        # Получение токена из куки
        jwt_token = request.COOKIES['jwt']

        # Добавление токена в черный список в Redis
        blacklist_key = 'jwt_blacklist'
        session_storage.set(blacklist_key, jwt_token)

        # Удаление куки с токеном
        response.delete_cookie('jwt')

        # Проверка токена в ЧС
        token_exists = session_storage.exists(blacklist_key, jwt_token)

        response.data = {
            'message': 'Successfully',
            'is_token_in_blacklist': bool(token_exists)
        }
        return response
