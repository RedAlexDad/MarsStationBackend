from bmstu_lab.models import MarsStation, Employee, Location, GeographicalObject, Users, Transport
from rest_framework import serializers

class GeographicalObjectSerializer(serializers.ModelSerializer):
    class Meta:
        # Модель, которую мы сериализуем
        model = GeographicalObject
        # Либо весь поля записываем
        fields = '__all__'

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'

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

class MarsStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarsStation
        # fields = ['id', 'type_status', 'data_create', 'data_from', 'data_close', 'id_scientist', 'id_transport', 'id_status']
        # Либо весь поля записываем
        fields = '__all__'

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'


class GeograficalObjectAndTransports(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'