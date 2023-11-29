from bmstu_lab.models import MarsStation, Employee, Location, GeographicalObject, Users, Transport
from rest_framework import serializers

from bmstu_lab.models import MarsStation, Employee, Location, GeographicalObject, Users, Transport
from rest_framework import serializers


class GeographicalObjectSerializer(serializers.ModelSerializer):
    class Meta:
        # Модель, которую мы сериализуем
        model = GeographicalObject
        # Либо весь поля записываем
        fields = '__all__'


class GeographicalObjectPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        # Модель, которую мы сериализуем
        model = GeographicalObject
        # Либо весь поля записываем
        fields = ('id', 'photo')


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'


class TransportSerializer(serializers.ModelSerializer):
    class Meta:
        # Модель, которую мы сериализуем
        model = Transport
        # Либо весь поля записываем
        fields = '__all__'


class TypeTransportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transport
        fields = ['id', 'type']


class MarsStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarsStation
        # Либо весь поля записываем
        fields = '__all__'


class GeograficalObjectAndTransports(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'


# ==================================================================================
# АККАУНТЫ
# ==================================================================================

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', 'username', 'password', 'is_moderator']


# Для аутенфикации, авторизации и регистрации
class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', 'username', 'password', 'is_moderator']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        password = validated_data.get('password', None)
        if password is not None:
            instance.set_password(password)
        else:
            # Если пароль не предоставлен в запросе, сохраняем текущий пароль
            validated_data['password'] = instance.password

        instance.is_moderator = validated_data.get('is_moderator', instance.is_moderator)
        instance.save()
        return instance

class UserAuthorizationSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
