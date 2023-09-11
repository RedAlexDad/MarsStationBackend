# views.py - обработчик приложения
from django.http import HttpResponse, Http404, HttpResponseBadRequest
from django.shortcuts import render, redirect
from datetime import date
from django.contrib import messages
from django.shortcuts import get_object_or_404

from .models import GeograficObject

database = [
    {'id': 1, 'name': 'Копрат',  'landing_risk': 10, 'research_status': 'Не изучено', 'ID_astronaut': 0, 'ID_spaceship': 0},
    {'id': 2, 'name': 'Титона',  'landing_risk': 80, 'research_status': 'Изучено', 'ID_astronaut': 2, 'ID_spaceship': 0},
    {'id': 3, 'name': 'Фарсида', 'landing_risk': 50, 'research_status': 'Не изучено', 'ID_astronaut': 1, 'ID_spaceship': 1},
    {'id': 4, 'name': 'Ксанфа',  'landing_risk': 75, 'research_status': 'Не изучено', 'ID_astronaut': 4, 'ID_spaceship': 1},
    {'id': 5, 'name': 'Мелас',   'landing_risk': 25, 'research_status': 'Изучено', 'ID_astronaut': 3, 'ID_spaceship': 1}
]

def GetGeograficObjects(request):
    return render(request, 'GeograficObjects.html', {'data' : {
        'current_date': date.today(),
        'GeograficObject': database
    }})

def GetGeograficObject(request, id):
    # Найдем объект в списке по 'id'
    GeograficObject = None
    for obj in database:
        if obj['id'] == id:
            GeograficObject = obj
            break

    if GeograficObject is None:
        raise Http404("Объект не найден")

    return render(request, 'GeograficObject.html', {'data': {
        'current_date': date.today(),
        'GeograficObject': GeograficObject
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

