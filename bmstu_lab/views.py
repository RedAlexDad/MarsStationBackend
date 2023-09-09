# views.py - обработчик приложения
# from django.http import HttpResponse
from django.shortcuts import render
from datetime import date


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

def GetOrders(request):
    return render(request, 'orders.html', {'data' : {
        'current_date': date.today(),
        'orders': [
            {'title': 'Книга с картинками', 'id': 1},
            {'title': 'Бутылка с водой', 'id': 2},
            {'title': 'Коврик для мышки', 'id': 3},
        ]
    }})

def GetOrder(request, id):
    return render(request, 'order.html', {'data' : {
        'current_date': date.today(),
        'id': id
    }})

def sendText(request):
    input_text = request.POST['text']
    print(input_text)