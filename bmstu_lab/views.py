# views.py - обработчик приложения
from django.http import HttpResponse, Http404, HttpResponseBadRequest
from django.shortcuts import render, redirect
from datetime import date
from django.contrib import messages
from django.shortcuts import get_object_or_404
import json
from .database import Database

from rest_framework import viewsets

from bmstu_lab.serializers import UsersSerializer, StatusSerializer, EmployeeSerializer, LocationSerializer, TransportSerializer, GeographicalObjectSerializer, MarsStationSerializer
from bmstu_lab.models import GeographicalObject, Transport

from bmstu_lab.APIview import GeograficalObjectAPIView

class GeographicalObjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint, который позволяет просматривать и редактировать акции компаний
    """
    # queryset всех пользователей для фильтрации по дате последнего изменения
    queryset = GeographicalObject.objects.all()
    # Сериализатор для модели
    serializer_class = GeographicalObjectSerializer

# Для отображения на сайте в формате JSON
# @renderer_classes([JSONRenderer])
# Разрешение для чтения (GET) или аутентификации для остальных методов
# @permission_classes([IsAuthenticatedOrReadOnly])

class TransportViewSet(viewsets.ModelViewSet):
    # queryset всех пользователей для фильтрации по дате последнего изменения
    queryset = Transport.objects.all()
    # Сериализатор для модели
    serializer_class = TransportSerializer

def MainPage(request):
    return render(request, 'main.html')

def SelectGeograficObject(request):
    return render(request, 'select_geografic_object.html')

def GetGeograficObjects(request):
    # Вызов класса по API для отображения данных
    geografical_object_view = GeograficalObjectAPIView()
    # Получение данных
    response = geografical_object_view.get(request=request)
    # Преобразование в JSON типа
    database = response.data
    # Заполнение данных в веб-странице
    return render(request, 'GeograficObjects.html',  database)


def GetGeograficObject(request, id):
    DB = Database()
    DB.connect()
    DB_transports = DB.get_geografical_object_and_transports_by_id(GeographicalObject.objects.filter(id=id).first().id)
    DB.close()
    return render(request, 'GeograficObject.html', {'data': {
        'current_date': date.today(),
        'GeograficObject': GeographicalObject.objects.filter(id=id)[0],
        'Transports': DB_transports
    }})

def Filter(request):
    filter_keyword = request.GET.get('filter_keyword')
    filter_field = request.GET.get('filter_field')

    if not filter_keyword or not filter_field:
        return HttpResponseBadRequest("Необходимо указать ключевое слово и поле для фильтрации")

    # if not filter_keyword or not filter_field:
        # messages.error(request, 'Необходимо указать ключевое слово и поле для фильтрации')
        # return redirect('filter')  # Ссылка на URL, на который мы хотим перенаправить пользователя

    # Преобразовать ключевое слово в строку для поиска в базе данных
    filter_keyword = str(filter_keyword)

    # Получить список услуг из базы данных
    filtered_services = []

    DB = GeographicalObject.objects.all()

    # Пройти по каждому объекту и создать словарь с необходимыми значениями
    keys = ['id', 'type', 'feature', 'size', 'describe', 'url_photo']
    database = [dict(zip(keys, obj)) for obj in DB]

    if filter_field == 'type':
        filtered_services = [service for service in database if filter_keyword.lower() in service['type'].lower()]
    if filter_field == 'feature':
        filtered_services = [service for service in database if filter_keyword.lower() in service['feature'].lower()]
    elif filter_field == 'size':
        filtered_services = [service for service in database if service['size'] == int(filter_keyword)]
    elif filter_field == 'describe':
        filtered_services = [service for service in database if filter_keyword.lower() in service['describe'].lower()]
    else:
        pass

    return render(request, 'services.html', {'database': filtered_services})

# Удаление объекта по ID, изменяя статус
def DeleteObjectByID(request):
    if request.method == 'POST':
        # Получаем значение object_id из POST-запроса
        object_id = int(request.POST.get('object_id'))
        if (object_id is not None):
            # Выполняем SQL запрос для редактирования статуса
            DB = Database()
            DB.connect()
            DB.update_status_delete_geografical_object(status_task=False, id_geografical_object=object_id)
            DB.close()
    # Перенаправим на предыдующую ссылку после успешного удаления
    return redirect('geografic_objects')
