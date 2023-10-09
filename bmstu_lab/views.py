# views.py - обработчик приложения
from django.http import Http404
from django.shortcuts import render

database = [
    {
        'id': 1,
        'feature': 'Acidalia Planitia',
        'type': 'Planitia, planitiae',
        'size': 2300,
        'describe': 'обширная тёмная равнина на Марсе. Размер — около 3 тысяч км, координаты центра — 50° с. ш. 339°. Расположена между вулканическим регионом Тарсис и Землёй Аравия, к северо-востоку от долин Маринера. На севере переходит в Великую Северную равнину, на юге — в равнину Хриса; на восточном краю равнины находится регион Кидония. Диаметр около 3000 км.',
        'url_photo': 'http://themis.asu.edu/files/feature_thumbnails/002acidaliaTN1.jpg',
        'status': True
    },
    {
        'id': 2,
        'feature': 'Alba Patera',
        'type': 'Patera, paterae',
        'size': 530,
        'describe': 'Огромный низкий вулкан, расположенный в северной части региона Фарсида на планете Марс. Это самый большой по площади вулкан на Марсе: потоки извергнутой из него породы прослеживаются на расстоянии как минимум 1350 км от его пика.',
        'url_photo': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/22/Tharsis_-_Valles_Marineris_MOLA_shaded_colorized_zoom_32.jpg/1280px-Tharsis_-_Valles_Marineris_MOLA_shaded_colorized_zoom_32.jpg',
        'status': True
    },
    {
        'id': 3,
        'feature': 'Albor Tholus',
        'type': 'Tholus, tholi',
        'size': 170,
        'describe': 'Потухший вулкан нагорья Элизий, расположенный на Марсе. Находится к югу от соседних горы Элизий и купола Гекаты. Вулкан достигает 4,5 километров в высоту и 160 километров в диаметре основания.',
        'url_photo': 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/Albor_Tholus_THEMIS.jpg/800px-Albor_Tholus_THEMIS.jpg',
        'status': True
    },
    {
        'id': 4,
        'feature': 'Amazonis Planitia',
        'type': 'Planitia, planitiae',
        'size': 2800,
        'describe': 'Слабоокрашенная равнина в северной экваториальной области Марса. Довольно молода, породы имеют возраст 10-100 млн. лет. Часть этих пород представляют собой застывшую вулканическую лаву.',
        'url_photo': 'https://upload.wikimedia.org/wikipedia/commons/3/31/26552sharpridges.jpg',
        'status': True
    },
    {
        'id': 5,
        'feature': 'Arabia Terra',
        'type': 'Terra, terrae',
        'size': 5100,
        'describe': 'Большая возвышенная область на севере Марса, которая лежит в основном в четырехугольнике Аравия, но небольшая часть находится в четырехугольнике Маре Ацидалиум. Она густо изрыта кратерами и сильно разрушена.',
        'url_photo': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Eden_Patera_THEMIS_day_IR.jpg/1189px-Eden_Patera_THEMIS_day_IR.jpg',
        'status': True
    }
]


# Основная страница
def MainPage(request):
    return render(request, 'main.html')


# Список географических объектов
def GetGeographicalObjects(request):
    response = {'data': database}
    return render(request, 'geographical_objects.html', response)


# Информация о географическом объекте
def GetGeographicalObject(request, id):
    # Найдем объект в списке по 'id'
    geographical_object = None
    for obj in database:
        if obj['id'] == id:
            geographical_object = obj
            break

    if geographical_object is None:
        raise Http404("Объект не найден")

    response = {'data': geographical_object}

    return render(request, 'geographical_object.html', response)


# Фильтрация
def Filter(request):
    filter_keyword = str(request.GET.get('filter_keyword'))

    filtered_objects = [obj for obj in database if filter_keyword.lower() in obj['feature'].lower()] or None

    if filtered_objects is None:
        raise Http404("Объект не найден")

    response = {'data': filtered_objects[0]}

    return render(request, 'geographical_object.html', response)
