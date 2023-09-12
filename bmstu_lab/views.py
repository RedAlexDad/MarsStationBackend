# views.py - обработчик приложения
from django.http import HttpResponse, Http404, HttpResponseBadRequest
from django.shortcuts import render, redirect
from datetime import date
from django.contrib import messages
from django.shortcuts import get_object_or_404
import json

from .models import geografic_object

def GetGeograficObjects(request):
    return render(request, 'GeograficObjects.html', {'data' : {
        'current_date': date.today(),
        'GeograficObject': geografic_object.objects.all()
    }})

def GetGeograficObject(request, id):
    return render(request, 'GeograficObject.html', {'data': {
        'current_date': date.today(),
        'GeograficObject': geografic_object.objects.filter(id=id)[0]
    }})

def filter(request):
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

    DB = geografic_object.objects.all().values('id', 'name', 'type_locality', 'describe')

    database = []
    # Пройти по каждому объекту и создать словарь с необходимыми значениями
    for obj in DB:
        data = {
            'id': obj['id'],
            'name': obj['name'],
            'type_locality': obj['type_locality'],
            'describe': obj['describe'],
        }
        database.append(data)

    if filter_field == 'name':
        filtered_services = [service for service in database if filter_keyword.lower() in service['name'].lower()]
    elif filter_field == 'landing_risk':
        filtered_services = [service for service in database if service['landing_risk'] == int(filter_keyword)]
    elif filter_field == 'research_status':
        filtered_services = [service for service in database if filter_keyword.lower() in service['research_status']]
    elif filter_field == 'ID_astronaut':
        filtered_services = [service for service in database if service['ID_astronaut'] == int(filter_keyword)]
    elif filter_field == 'ID_spaceship':
        filtered_services = [service for service in database if service['ID_spaceship'] == int(filter_keyword)]

    else:
        pass

    return render(request, 'services.html', {'database': filtered_services})

