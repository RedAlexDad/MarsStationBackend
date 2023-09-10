# views.py - обработчик приложения
from django.http import HttpResponse, Http404, HttpResponseBadRequest
from django.shortcuts import render, redirect
from datetime import date
from django.contrib import messages
from django.shortcuts import get_object_or_404


def hello(request):
    # Возврат функции без вложенных полей
    # return render(request, 'index.html', {
    #     'current_date': date.today()
    # })
    # С вложенным полями
    # return render(request, 'index.html', {'data': {'current_date': date.today()}})
    return render(request, 'index.html', {'data': {
        'current_date': date.today(),
        'list': ['python', 'django', 'html']
    }})

# def GetOrders(request):
#     return render(request, 'orders.html', {'data' : {
#         'current_date': date.today(),
#         'orders': [
#             {'title': 'Книга с картинками', 'id': 1},
#             {'title': 'Бутылка с водой', 'id': 2},
#             {'title': 'Коврик для мышки', 'id': 3},
#         ]
#     }})

# Географические объекты Марса
# Каньоны : Копрат, Титона, Эос, Капри и Ганг
# Равнины : Утопия, Эллада, Фарсида, Элизий, Амазония, Хриса
# Моря : Большой Сирт, Ацидалийское
# Расщелины : Офир, Ио, Кандор, Мелас
# Горы : Фарсида, Олимп (в 3 раза выше Эвереста)
# Вулканы - горы : Аскрийская, Арсия, Павлина
# Вулканы - купола : Альбор, Гекаты
# Земля : Ксанфа
# Кратеры : Оудеманс, Эберсвальд
# Плато : Тарсис с гигантскими вулканами
# Полярные шапки : северная и южная
# Долина : Маринера (в несколько раз превышает Большой Каньон в Америке)
# Световые люки : черные отверстия ведущие в подземные лавовые трубы Марса; люди в будущем смогут их использовать для укрытия
# Лабиринт ночи : Над которым постоянно висит странный кристаллический туман копирующий очертания этого региона

database = [
    {'id': 1, 'name': 'Копрат',  'landing_risk': 10, 'research_status': 'Не изучено', 'ID_astronaut': 0, 'ID_spaceship': 0},
    {'id': 2, 'name': 'Титона',  'landing_risk': 80, 'research_status': 'Изучено', 'ID_astronaut': 2, 'ID_spaceship': 0},
    {'id': 3, 'name': 'Фарсида', 'landing_risk': 50, 'research_status': 'Не изучено', 'ID_astronaut': 1, 'ID_spaceship': 1},
    {'id': 4, 'name': 'Ксанфа',  'landing_risk': 75, 'research_status': 'Не изучено', 'ID_astronaut': 4, 'ID_spaceship': 1},
    {'id': 5, 'name': 'Мелас',   'landing_risk': 25, 'research_status': 'Изучено', 'ID_astronaut': 3, 'ID_spaceship': 1}
]

def GetOrders(request):
    return render(request, 'orders.html', {'data' : {
        'current_date': date.today(),
        'orders': database
    }})


# Для маршрутизации, переключает страницу по ID карточек
# def GetOrder(request, id):
#     return render(request, 'order.html', {'data' : {
#         'current_date': date.today(),
#         'id': id,
#         # 'name': name,
#         # 'landing_risk': landing_risk,
#         # 'research_status': research_status,
#         # 'ID_astronaut': ID_astronaut,
#         # 'ID_spaceship': ID_spaceship
#     }})

def GetOrder(request, id):
    # Найдем объект в списке по 'id'
    order = None
    for obj in database:
        if obj['id'] == id:
            order = obj
            break

    if order is None:
        raise Http404("Объект не найден")

    return render(request, 'order.html', {'data': {
        'current_date': date.today(),
        'order': order
    }})


def sendText(request):
    if request.method == 'POST':
        # Получить значение передаваемого параметра 'text' из POST-запроса
        input_text = request.POST.get('text', '')

        # Выполнить нужные действия с полученными данными
        # Например, можно сохранить их в базу данных или выполнить какую-то логику
        # В данном случае, мы просто вернем полученный текст в ответе
        response_text = f"Вы ввели: {input_text}"

        # Вернуть ответ с результатом
        return HttpResponse(response_text)
    else:
        # Если это не POST-запрос, можно выполнить другую логику, если это необходимо
        # Например, можно вернуть страницу с формой для ввода текста
        return render(request, 'base.html')

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

