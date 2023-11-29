import requests
from rest_framework.views import APIView
from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema

from django.core.cache import cache
from django.contrib.auth import authenticate, login, logout
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, BasePermission
from django.conf import settings
from bmstu_lab.permissions import IsModerator, IsAuthenticated, create_access_token, create_refresh_token, \
    get_jwt_payload, get_access_token, get_refresh_token, add_in_blacklist

from bmstu_lab.serializers import UsersSerializer, UserRegisterSerializer, UserAuthorizationSerializer, \
    EmployeeSerializer
from bmstu_lab.models import Users, Employee
import jwt, datetime

# ==================================================================================
# АККАУНТЫ
# ==================================================================================
from rest_framework import status
from django.shortcuts import get_object_or_404


class UsersGET(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsModerator]
    model_class = Users
    serializer_class = UsersSerializer

    def get(self, request, format=None):
        print('[INFO] API GET [UsersINFO]')
        users = self.model_class.objects.all()
        serializer = self.serializer_class(users, many=True)
        return Response(serializer.data)


class UsersPUT(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsModerator]
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
    permission_classes = [IsModerator]
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
# РЕГИСТРАЦИЯ, АУТЕНФИКАЦИЯ, ПОЛУЧЕНИЕ ТОКЕНА, ВЫХОД С УЧЕТНОЙ ЗАПИСИ
# ==================================================================================
# Регистрация
class RegisterView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = []

    @swagger_auto_schema(request_body=UserRegisterSerializer)
    def post(self, request):
        user_data = {
            "username": request.data['username'],
            "password": request.data['password'],
            "is_moderator": request.data.get('is_moderator', False),
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


# Аутентификация
class LoginView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=UserAuthorizationSerializer)
    def post(self, request):
        user_serializer = UserAuthorizationSerializer(data=request.data)

        if not user_serializer.is_valid():
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(**user_serializer.data)
        if user is None:
            return Response({'message': 'User not found! Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        error_message, access_token = create_access_token(user)
        employee = Employee.objects.get(id_user=user.id)

        response = Response(status=status.HTTP_200_OK)
        response.set_cookie(key='access_token', value=access_token, httponly=True)
        response.data = {
            'user': {
                'id': user.id,
                'username': user.username,
                'is_moderator': user.is_moderator
            },
            'employee': {
                'id': employee.id,
                'name': employee.full_name,
                'post': employee.post,
                'name_organization': employee.name_organization,
                'address': employee.address
            },
            'message': 'Successfully',
            'access_token': access_token,
        }

        # Добавляем error_message, если есть ошибка
        if error_message:
            response.data['error_message'] = error_message

        return response


# Получение токена
class GetToken(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = []

    def post(self, request):
        error_message, access_token = get_access_token(request)
        print('token:', access_token)

        payload = get_jwt_payload(access_token)
        user = Users.objects.filter(id=payload['id']).first()
        employee = Employee.objects.get(id_user=user.id)

        data = {
            'user_data': {
                'id': user.id,
                'username': user.username,
                'is_moderator': user.is_moderator
            },
            'employee': {
                'id': employee.id,
                'name': employee.full_name,
                'post': employee.post,
                'name_organization': employee.name_organization,
                'address': employee.address
            },
            'message': 'Successfully',
            'access_token': access_token,
        }
        # Добавляем error_message, если есть ошибка
        if error_message:
            data['error_message'] = error_message

        return Response(data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = []

    def post(self, request):
        access_token = request.COOKIES.get('access_token')

        # Проверка наличия токена
        if access_token is None:
            return Response({'error': 'No access_token token found. Token is not found in cookie. You are already logged out'},
                            status=status.HTTP_401_UNAUTHORIZED)

        # Добавление токена в черный список в Redis
        error_message, token_exists = add_in_blacklist(access_token)
        response = Response(status=status.HTTP_200_OK)

        # Удаление куки с токеном
        response.delete_cookie('access_token')
        response.data = {
            'message': 'Successfully',
            'is_token_in_blacklist': bool(token_exists)
        }

        # Добавляем error_message, если есть ошибка
        if error_message:
            response.data['error_message'] = error_message

        return response
