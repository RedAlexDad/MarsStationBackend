from rest_framework.views import APIView
from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema

from django.contrib.auth import authenticate
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import AllowAny
from bmstu_lab.permissions import IsModerator, IsAuthenticated, create_access_token, \
    get_jwt_payload, get_access_token, add_in_blacklist

from bmstu_lab.serializers import UsersSerializer, UserRegisterSerializer, UserAuthorizationSerializer, \
    EmployeeSerializer, UsersSerializerInfo
from bmstu_lab.models import Users, Employee

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
        return Response(serializer.data, status=status.HTTP_200_OK)


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
        return Response(data={'message': 'Успешно'}, status=status.HTTP_204_NO_CONTENT)


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
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=serializer_class)
    def post(self, request, format=None):
        print('[INFO] API GET [Employee POST]')
        # Проверим на наличие объекта с заданным pk
        try:
            user = Users.objects.get(pk=request.data['id_user'])
        except Users.DoesNotExist:
            return Response(f"Пользователи объекта по {request.data['id_user']} нет",
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
            return Response(serializer.data, status=status.HTTP_200_OK)
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
        try:
            try:
                user_serializer = UserRegisterSerializer(data=request.data['user'])
                user_serializer.is_valid(raise_exception=True)
                user_instance = user_serializer.save()
                id_user = user_instance.id
            except AssertionError as error:
                return Response(data={"message": str(error)}, status=status.HTTP_400_BAD_REQUEST)
            try:
                employee_data = request.data['employee']
                employee_data['id_user'] = id_user
                employee_serializer = EmployeeSerializer(data=request.data['employee'])
                employee_serializer.is_valid(raise_exception=True)
                employee_serializer.save()
                return Response(data={"user": user_serializer.data, "employee": employee_serializer.data},
                                status=status.HTTP_200_OK)
            except AssertionError as error:
                return Response(data={"message": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return Response(data={"message": str(error)}, status=status.HTTP_404_NOT_FOUND)


# Аутентификация
class LoginView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=UserAuthorizationSerializer)
    def post(self, request):
        try:
            user_serializer = UserAuthorizationSerializer(data=request.data)
            if not user_serializer.is_valid():
                return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except AssertionError as error:
            return Response(data={"message": str(error)}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(**user_serializer.data)
        if user is None:
            return Response({'message': 'Такого аккаунта не найдены. Вы неверно ввели свои учетные данные'}, status=status.HTTP_401_UNAUTHORIZED)

        error_message, access_token = create_access_token(user)
        employee = Employee.objects.get(id_user=user.id)
        employee_serializer = EmployeeSerializer(employee, many=False)

        response = Response(status=status.HTTP_200_OK)
        response.set_cookie(key='access_token', value=access_token, httponly=True)
        response.data = {
            'user': user_serializer.data,
            'employee': employee_serializer.data,
            'message': 'Успешно',
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

        if access_token is None:
            return Response(error_message, status=status.HTTP_401_UNAUTHORIZED)
        payload = get_jwt_payload(access_token)
        user = Users.objects.filter(id=payload['id']).first()
        employee = Employee.objects.get(id_user=user.id)

        data = {
            'user': UsersSerializerInfo(user, many=False).data,
            'employee': EmployeeSerializer(employee, many=False).data,
            'message': 'Успешно',
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
            return Response({'message': 'Токен в access_token и cookie не найден. Скорее всего вы уже вышли из системы?'},
                            status=status.HTTP_401_UNAUTHORIZED)

        # Добавление токена в черный список в Redis
        error_message, token_exists = add_in_blacklist(access_token)
        response = Response(status=status.HTTP_200_OK)

        # Удаление куки с токеном
        response.delete_cookie('access_token')
        response.data = {
            'message': 'Успешно',
            'is_token_in_blacklist': bool(token_exists)
        }

        # Добавляем error_message, если есть ошибка
        if error_message:
            response.data['error_message'] = error_message

        return response
