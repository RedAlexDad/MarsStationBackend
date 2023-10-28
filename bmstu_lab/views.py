from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from bmstu_lab.serializers import UsersSerializer, UserRegisterSerializer, UserAuthorizationSerializer
from bmstu_lab.models import Users
import jwt, datetime

# ==================================================================================
# АККАУНТЫ
# ==================================================================================
from rest_framework import status
from django.shortcuts import get_object_or_404

class UsersINFO(APIView):
    model_class = Users
    serializer_class = UsersSerializer

    def get(self, request, format=None):
        """Возвращает список о аккаунтах"""
        print('[INFO] API GET [UsersINFO]')
        users = self.model_class.objects.all()
        serializer = self.serializer_class(users, many=True)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        """Обновляет аккаунт (для модератора)"""
        print('[INFO] API PUT [UsersINFO]')
        users = get_object_or_404(self.model_class, pk=pk)
        serializer = self.serializer_class(users, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        """Удаляет аккаунт"""
        print('[INFO] API DELETE [UsersINFO]')
        users = get_object_or_404(self.model_class, pk=pk)
        users.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ==================================================================================
# АУТЕНФИКАЦИЯ
# ==================================================================================
class RegisterView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoginView(APIView):
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

        response = Response()

        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'jwt': token
        }
        return response


class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        user = Users.objects.filter(id=payload['id']).first()
        serializer = UserAuthorizationSerializer(user)
        return Response(serializer.data)


class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'Success'
        }
        return response
