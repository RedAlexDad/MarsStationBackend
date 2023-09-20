# views.py - обработчик приложения
from django.http import HttpResponse, Http404, HttpResponseBadRequest
from django.shortcuts import render, redirect
from datetime import date
from django.contrib import messages
from django.shortcuts import get_object_or_404
import json
from .database import Database

from .models import GeographicalObject

def MainPage(request):
    return render(request, 'main.html')

def SelectGeograficObject(request):
    return render(request, 'select_geografic_object.html')

def GetGeograficObjects(request):
    DB = Database()
    DB.connect()
    DB_geografical_object_with_status = DB.get_geografical_object_with_status()
    DB.close()
    return render(request, 'GeograficObjects.html', {'data' : {
        'current_date': date.today(),
        'GeograficObject': DB_geografical_object_with_status
    }})

def GetGeograficObject(request, id):
    DB = Database()
    DB.connect()
    DB_locations = DB.get_locations_by_id(GeographicalObject.objects.filter(id=id).first().id)
    DB.close()
    return render(request, 'GeograficObject.html', {'data': {
        'current_date': date.today(),
        'GeograficObject': GeographicalObject.objects.filter(id=id)[0],
        'Locations': DB_locations
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

    database = []
    # Пройти по каждому объекту и создать словарь с необходимыми значениями
    for obj in DB:
        data = {
            'id': obj.id,
            'type': obj.type,
            'feature': obj.feature,
            'size': obj.size,
            'describe': obj.describe,
            'url_photo': obj.url_photo,
        }
        database.append(data)

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
            DB.update_status_delete_geografical_object(status_task='Удален', id_geografical_object=object_id)
            DB.close()
    # Перенаправим на предыдующую ссылку после успешного удаления
    return redirect('geografic_objects')
