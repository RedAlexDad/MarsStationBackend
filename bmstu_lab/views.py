# views.py - обработчик приложения
from django.http import HttpResponse, Http404, HttpResponseBadRequest
from django.shortcuts import render, redirect
from datetime import date
from django.contrib import messages
from django.shortcuts import get_object_or_404
import json

from .models import GeographicalObject

def MainPage(request):
    return render(request, 'main.html')

def SelectGeograficObject(request):
    return render(request, 'select_geografic_object.html')

def GetGeograficObjects(request):
    return render(request, 'GeograficObjects.html', {'data' : {
        'current_date': date.today(),
        'GeograficObject': GeographicalObject.objects.all()
    }})

def GetGeograficObject(request, id):
    return render(request, 'GeograficObject.html', {'data': {
        'current_date': date.today(),
        'GeograficObject': GeographicalObject.objects.filter(id=id)[0]
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
            'feature': obj.feature,
            'type': obj.type,
            'size': obj.size,
            'named_in_year': obj.named_in_year,
            'named_for': obj.named_for,
        }
        database.append(data)

    if filter_field == 'feature':
        filtered_services = [service for service in database if filter_keyword.lower() in service['feature'].lower()]
    if filter_field == 'type':
        filtered_services = [service for service in database if filter_keyword.lower() in service['type'].lower()]
    elif filter_field == 'size':
        filtered_services = [service for service in database if service['size'] == int(filter_keyword)]
    elif filter_field == 'named_in_year':
        filtered_services = [service for service in database if service['named_in_year'] == int(filter_keyword)]
    elif filter_field == 'named_for':
        filtered_services = [service for service in database if filter_keyword.lower() in service['named_for'].lower()]
    else:
        pass

    return render(request, 'services.html', {'database': filtered_services})

# Удаление объекта по ID
# def DeleteObjectByID(request):
