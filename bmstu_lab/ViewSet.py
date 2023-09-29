from rest_framework import viewsets

from bmstu_lab.serializers import UsersSerializer, StatusSerializer, EmployeeSerializer, LocationSerializer, TransportSerializer, GeographicalObjectSerializer, MarsStationSerializer
from bmstu_lab.models import GeographicalObject, Transport
from bmstu_lab.filters import GeographicalObjectFilter

class GeographicalObjectViewSet(viewsets.ModelViewSet):
    """ API endpoint, который позволяет просматривать и редактировать акции компаний """
    # queryset всех пользователей для фильтрации по дате последнего изменения
    queryset = GeographicalObject.objects.all()
    # Сериализатор для модели
    serializer_class = GeographicalObjectSerializer
    # Фильтрация объектов
    filterset_class = GeographicalObjectFilter
    # Можно еще добавить другие фильтры

# Для отображения на сайте в формате JSON
# @renderer_classes([JSONRenderer])
# Разрешение для чтения (GET) или аутентификации для остальных методов
# @permission_classes([IsAuthenticatedOrReadOnly])

class TransportViewSet(viewsets.ModelViewSet):
    # queryset всех пользователей для фильтрации по дате последнего изменения
    queryset = Transport.objects.all()
    # Сериализатор для модели
    serializer_class = TransportSerializer