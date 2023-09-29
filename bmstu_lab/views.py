# views.py - обработчик приложения
from django.shortcuts import render, redirect

from bmstu_lab.APIview.GeographicalObject import GeograficalObjectAPIView

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

# Удаление объекта по ID, изменяя статус
def DeleteObjectByID(request):
    # Вызов класса по API для отображения данных
    geografical_object_view = GeograficalObjectAPIView()
    # Получение данных
    geografical_object_view.delete_object_by_id(request=request, id=int(request.POST.get('id')))
    # Заполнение данных в веб-странице
    return redirect('geografic_objects')