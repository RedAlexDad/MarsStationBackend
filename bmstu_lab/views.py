from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

from django.contrib.auth import authenticate, login, logout
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated, BasePermission, IsAdminUser
from django.conf import settings

from bmstu_lab.serializers import UsersSerializer, UserRegisterSerializer, UserAuthorizationSerializer
from bmstu_lab.models import Users
import jwt, datetime
from cryptography.fernet import Fernet

# ==================================================================================
# СУБД хранение сессий
# ==================================================================================
import redis

# Подключение Redis
session_storage = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

# ==================================================================================
# АККАУНТЫ
# ==================================================================================
from rest_framework import status
from django.shortcuts import get_object_or_404


class UsersGET(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
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
    serializer_class = UsersSerializer

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
        return Response(status=status.HTTP_204_NO_CONTENT)


# ==================================================================================
# РЕГИСТРАЦИЯ, АУТЕНФИКАЦИЯ, АВТОРИЗАЦИЯ, ВЫХОД С УЧЕТНОЙ ЗАПИСИ
# ==================================================================================
class RegisterView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoginView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [AllowAny]

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
        # Хранение токена в REDIS
        session_storage.set(token, username)

        response = Response(status=status.HTTP_200_OK)
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'message': 'Successfully',
            'jwt': token
        }

        return response


class UserView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Получение токена из хранилища (Redis)
        token = request.COOKIES.get('jwt')

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

        response.delete_cookie('jwt')
        response.data = {
            'message': 'Successfully'
        }
        return response
