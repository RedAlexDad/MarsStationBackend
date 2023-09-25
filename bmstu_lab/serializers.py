from bmstu_lab.models import GeographicalObject, Transport, MarsStation
from rest_framework import serializers


class GeographicalObjectSerializer(serializers.ModelSerializer):
    class Meta:
        # Модель, которую мы сериализуем
        model = GeographicalObject

        # Поля, которые мы сериализуем
        fields = ['id', 'feature', 'type', 'size', 'describe', 'url_photo', 'status']

class TransportSerializer(serializers.ModelSerializer):
    class Meta:
        # Модель, которую мы сериализуем
        model = Transport

        # Поля, которые мы сериализуем
        fields = ['id', 'name', 'type', 'describe', 'url_photo']

class MarsStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarsStation
        fields = ['id', 'type_status', 'data_create', 'data_from', 'data_close', 'id_scientist', 'id_transport', 'id_status']
