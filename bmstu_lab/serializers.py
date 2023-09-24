from bmstu_lab.models import GeographicalObject
from rest_framework import serializers


class GeographicalObjectSerializer(serializers.ModelSerializer):
    class Meta:
        # Модель, которую мы сериализуем
        model = GeographicalObject

        # Поля, которые мы сериализуем
        fields = ['feature', 'type', 'size', 'describe', 'url_photo', 'status']
