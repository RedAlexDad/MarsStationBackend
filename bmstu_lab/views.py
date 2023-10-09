# views.py - обработчик приложения
from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect
from bmstu_lab.database import Database
from bmstu_lab.models import GeographicalObject

# Основная страница
def MainPage(request):
    return render(request, 'main.html')

# Список географических объектов
def GetGeographicalObjects(request):
    response = {'data': GeographicalObject.objects.filter(status=True)}
    return render(request, 'geographical_objects.html', response)

# Информация о географическом объекте
def GetGeographicalObject(request, id):
    response = {'data': GeographicalObject.objects.filter(id=id).first()}
    return render(request, 'geographical_object.html', response)

# Фильтрация
def Filter(request):
    # Преобразовать ключевое слово в строку для поиска в базе данных
    filter_keyword = request.GET.get('filter_keyword')

    # Выполним фильтрацию с использованием ORM
    filtered_objects = GeographicalObject.objects.filter(feature__icontains=filter_keyword)
    # Преобразуем QuerySet в список
    filtered_objects_list = list(filtered_objects)

    # Передадим отфильтрованные объекты в шаблон для отображения
    return render(request, 'geographical_objects.html', {'data': filtered_objects_list})

# Удаление объекта по ID, изменяя статус
def DeleteObjectByID(request):
    if request.method == 'POST':
        # Получаем значение object_id из POST-запроса
        object_id = int(request.POST.get('id'))
        if (object_id is not None):
            # Выполняем SQL запрос для редактирования статуса
            DB = Database()
            DB.connect()
            DB.update_status_delete_geografical_object(status=False, id_geografical_object=object_id)
            DB.close()
    # Перенаправим на предыдующую ссылку после успешного удаления
    return redirect('geographical_objects')
