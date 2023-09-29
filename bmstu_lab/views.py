# views.py - обработчик приложения
from django.http import HttpResponse, Http404, HttpResponseBadRequest
from django.shortcuts import render, redirect
from datetime import date
from django.contrib import messages
from django.shortcuts import get_object_or_404
import json
from .database import Database

from bmstu_lab.models import GeographicalObject, Transport

from bmstu_lab.APIview.GeographicalObject import GeograficalObjectAPIView

# Для фильтрации данных
from bmstu_lab.filters import GeographicalObjectFilter

from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from bmstu_lab.serializers import GeographicalObjectSerializer


class FilteredGeographicalObjectList(generics.ListAPIView):
    serializer_class = GeographicalObjectSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = GeographicalObjectFilter
    queryset = GeographicalObject.objects.all()

def MainPage(request):
    return render(request, 'main.html')

def SelectGeograficObject(request):
    return render(request, 'select_geografic_object.html')

def GetGeograficObjects(request):
    # Вызов класса по API для отображения данных
    geografical_object_view = GeograficalObjectAPIView()
    # Получение данных
    response = geografical_object_view.get_object_with_status(request=request)
    # Преобразование в JSON типа
    database = response.data
    # Заполнение данных в веб-странице
    return render(request, 'GeograficObjects.html',  database)


def GetGeograficObject(request, id):
    # Вызов класса по API для отображения данных
    geografical_object_view = GeograficalObjectAPIView()
    # Получение данных
    response = geografical_object_view.get_geografical_object_and_transports_by_id(request=request, id=id)
    # Преобразование в JSON типа
    database = response.data
    # Заполнение данных в веб-странице
    return render(request, 'GeograficObject.html', database)

def Filter(request):
    # Вызов класса по API для отображения данных
    geografical_object_view = GeograficalObjectAPIView()
    # Получение данных
    response = geografical_object_view.filter_geographical_objects(request=request)
    # Преобразование в JSON типа
    database = response.data
    # Заполнение данных в веб-странице
    return render(request, 'GeograficObject.html', database)



# def Filter(request):
#     # Получите параметры фильтрации из запроса
#     filter_keyword = request.GET.get('filter_keyword')
#     filter_field = request.GET.get('filter_field')
#
#     # Получите начальный queryset
#     queryset = GeographicalObject.objects.all()
#
#     # Если есть параметры фильтрации, примените фильтр
#     if filter_keyword and filter_field:
#         filters = {f'{filter_field}__icontains': filter_keyword}
#         queryset = queryset.filter(**filters)
#
#     # Преобразуйте отфильтрованные объекты в JSON
#     data = serializers.serialize('json', queryset)
#
#     # Отправьте JSON в ответе
#     return JsonResponse({'data': data}, safe=False)



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
