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
        # Поля, которые мы сериализуем
        # fields = ['id', 'name', 'type', 'describe', 'url_photo']
        # Либо весь поля записываем
        fields = '__all__'


class TypeTransportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transport
        fields = ['id', 'type']


class MarsStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarsStation
        # fields = ['id', 'type_status', 'data_create', 'data_from', 'data_close', 'id_scientist', 'id_transport', 'id_status']
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
        fields = ['id', 'username', 'password', 'is_staff', 'is_superuser']


# Для аутенфикации, авторизации и регистрации
class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', 'username', 'password', 'is_staff', 'is_superuser']
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


class UserAuthorizationSerializer(serializers.Serializer):
    username = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)
