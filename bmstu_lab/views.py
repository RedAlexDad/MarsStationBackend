# views.py - обработчик приложения
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.shortcuts import get_object_or_404

from bmstu_lab.serializers import GeographicalObjectSerializer, MarsStationSerializer, LocationSerializer
from bmstu_lab.models import GeographicalObject, MarsStation, Location

from bmstu_lab.DB_Minio import DB_Minio


# ==================================================================================
# УСЛУГА
# ==================================================================================

# Возвращает список географические объекты
@api_view(['GET'])
def GET_GeographicalObjectsList(request, format=None):
    print('[INFO] API GET [GET_GeographicalObjectsList]')
    # Получение данные после запроса с БД (через ORM)
    geographical_object = GeographicalObject.objects.all()

    # Получение данные с MINIO и обновление ссылок на него (фотография) и измением данные
    try:
        try:
            for obj in geographical_object:
                DB = DB_Minio()
                url_photo = DB.get_presigned_url(
                    method='GET', bucket_name='mars',
                    object_name=obj.feature + '.jpg'
                )

                obj.url_photo = url_photo
                # Сохраняем обновленный объект в БД
                obj.save()
        except Exception as ex:
            print(f"Ошибка при обработке объекта {obj.feature}: {str(ex)}")
    except Exception as ex:
        print('Ошибка соединения с БД Minio', ex)

    # Сериализиуем его, чтобы получить в формате JSON
    serializer = GeographicalObjectSerializer(geographical_object, many=True)

    return Response(serializer.data)

# Возвращает данные о географическом объекте
@api_view(['GET'])
def GET_GeographicalObject(request, pk, format=None):
    print('[INFO] API GET [GET_GeographicalObject]')
    geographical_object = get_object_or_404(GeographicalObject, pk=pk)
    # Возвращает информацию об акции
    if request.method == 'GET':
        try:
            DB = DB_Minio()
            url_photo = DB.get_presigned_url(
                method='GET', bucket_name='mars',
                object_name=geographical_object.feature + '.jpg'
            )
            geographical_object.url_photo = url_photo
            # Сохраняем обновленный в БД
            geographical_object.save()
        except Exception as ex:
            print(f"Ошибка при обработке объекта {geographical_object.feature}: {str(ex)}")

        geographical_object_serializer = GeographicalObjectSerializer(geographical_object)

        return Response(geographical_object_serializer.data)


# Возвращает данные о марсианской станции по фильтрации
@api_view(['GET'])
def GET_GeographicalObjectFiltration(request, format=None):
    print('[INFO] API GET [GET_GeographicalObjectFiltration]')
    if request.method == 'GET':
        # Получим параметры запроса из URL
        feature = request.GET.get('feature')
        type = request.GET.get('type')
        size = request.GET.get('size')
        describe = request.GET.get('describe')
        status = request.GET.get('status')

        # Создадим пустой queryset
        geographical_object = GeographicalObject.objects.all()

        # Применим фильтры на основе параметров запроса, если они предоставлены
        if feature:
            geographical_object = geographical_object.filter(feature=feature)
        if type:
            geographical_object = geographical_object.filter(type__icontains=type)
        if size:
            geographical_object = geographical_object.filter(size=size)
        if describe:
            geographical_object = geographical_object.filter(describe__icontains=describe)
        if status:
            geographical_object = geographical_object.filter(status=status)

        # Сериализуем результаты запроса
        geographical_object_serializer = GeographicalObjectSerializer(geographical_object, many=True)

        return Response(geographical_object_serializer.data)

# Добавляет новую запись
@api_view(['POST'])
def POST_GeograficObject(request, format=None):
    print('[INFO] API POST [POST_GeograficObjects]')
    serializer = GeographicalObjectSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Обновляет информацию о географическом объекте по ID
@api_view(['PUT'])
def PUT_GeograficObject(request, pk, format=None):
    print('[INFO] API PUT [PUT_GeograficObject]')
    geographical_object = get_object_or_404(GeographicalObject, pk=pk)
    serializer = GeographicalObjectSerializer(geographical_object, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Удаляет географический объект по ID
@api_view(['DELETE'])
def DELETE_GeograficObject(request, pk, format=None):
    if not GeographicalObject.objects.filter(pk=pk).exists():
        return Response(f"ERROR! There is no such object!")

    print('[INFO] API DELETE [DELETE_GeograficObjects]')
    geographical_object = get_object_or_404(GeographicalObject, pk=pk)
    geographical_object.delete()
    return Response('Successfully deleted', status=status.HTTP_204_NO_CONTENT)


# Добавляет новую запись в заявку
@api_view(['POST'])
def POST_GeograficObject_IN_MarsStation(request, pk, format=None):
    print('[INFO] API POST [POST_GeograficObject_IN_MarsStation]')
    # Проверим на наличие объекта с заданным pk
    try:
        geographical_object = GeographicalObject.objects.get(pk=pk)
    except GeographicalObject.DoesNotExist:
        return Response(f"ERROR! Object There is no such object by ID!", status=status.HTTP_404_NOT_FOUND)

    # status_task
    # 1: Введен: Заявка только что создана и ожидает обработки.
    # 2: В работе: Заявка была принята и находится в процессе выполнения.
    # 3: Завершена: Заявка успешно выполнена.
    # 4: Отменена: Заявка была отменена по каким-либо причинам.
    # 5: Удалена: Заявка была удалена из системы.
    # status_mission
    # 1: Успех
    # 2: Потеря
    # 3: Работает

    # Получаем последнюю заявку со статусом
    mars_station = MarsStation.objects.filter(id_status__status_task=1, id_status__status_mission=3).last()

    # Создание записи в таблице Location для связи между MarsStation и GeographicalObject
    Location.objects.create(
        id_geographical_object=geographical_object,
        id_mars_station=mars_station,
        sequence_number=1
    )
    return Response('Successfully created', status=status.HTTP_201_CREATED)


# ==================================================================================
# ЗАЯВКА
# ==================================================================================

# Возвращает список марсианских станций
@api_view(['GET'])
def GET_MarsStationList(request, format=None):
    print('[INFO] API GET [GET_MarsStation]')
    mars_station = MarsStation.objects.all()
    # Сериализиуем его, чтобы получить в формате JSON
    mars_station_serializer = MarsStationSerializer(mars_station, many=True)
    return Response(mars_station_serializer.data)


# Возвращает данные о марсианской станции
@api_view(['GET'])
def GET_MarsStation(request, pk, format=None):
    print('[INFO] API GET [GET_MarsStation]')
    mars_station = get_object_or_404(MarsStation, pk=pk)
    if request.method == 'GET':
        mars_station_serializer = MarsStationSerializer(mars_station)

        return Response(mars_station_serializer.data)


# Возвращает данные о марсианской станции по фильтрации
@api_view(['GET'])
def GET_MarsStationFiltration(request, format=None):
    print('[INFO] API GET [GET_MarsStationFiltration]')
    if request.method == 'GET':
        # Получим параметры запроса из URL
        type_status = request.GET.get('type_status')
        status_task = request.GET.get('status_task')
        status_mission = request.GET.get('status_mission')

        # Создадим пустой queryset
        mars_station = MarsStation.objects.all()

        # Применим фильтры на основе параметров запроса, если они предоставлены
        if type_status:
            mars_station = mars_station.filter(type_status=type_status)
        if status_task:
            mars_station = mars_station.filter(status_task=status_task)
        if status_mission:
            mars_station = mars_station.filter(status_mission=status_mission)

        # Сериализуем результаты запроса
        mars_station_serializer = MarsStationSerializer(mars_station, many=True)

        return Response(mars_station_serializer.data)

# Добавляет новую запись
@api_view(['POST'])
def POST_MarsStation(request, format=None):
    print('[INFO] API POST [POST_MarsStation]')
    mars_station_serializer = MarsStationSerializer(data=request.data)
    mars_station_serializer.is_valid(raise_exception=True)
    if mars_station_serializer.is_valid():
        mars_station_serializer.save()
        return Response(mars_station_serializer.data, status=status.HTTP_201_CREATED)

    return Response(mars_station_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Обновляет информацию о марсианской станции по ID
@api_view(['PUT'])
def PUT_MarsStation(request, pk, format=None):
    print('[INFO] API PUT [PUT_MarsStation]')
    mars_station = get_object_or_404(MarsStation, pk=pk)
    mars_station_serializer = MarsStationSerializer(mars_station, data=request.data)
    if mars_station_serializer.is_valid():
        mars_station_serializer.save()
        return Response(mars_station_serializer.data)
    return Response(mars_station_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Обновляет информацию о марсианской станции по ID создателя
@api_view(['PUT'])
def PUT_MarsStation_BY_USER(request, pk, format=None):
    print('[INFO] API PUT [PUT_MarsStation]')
    mars_station = get_object_or_404(MarsStation, pk=pk)
    mars_station_serializer = MarsStationSerializer(mars_station, data=request.data)
    if mars_station_serializer.is_valid():
        mars_station_serializer.save()
        return Response(mars_station_serializer.data)
    return Response(mars_station_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Обновляет информацию о марсианской станции по ID создателя
@api_view(['PUT'])
def PUT_MarsStation_BY_ADMIN(request, pk, format=None):
    print('[INFO] API PUT [PUT_MarsStation]')
    mars_station = get_object_or_404(MarsStation, pk=pk)
    mars_station_serializer = MarsStationSerializer(mars_station, data=request.data)
    if mars_station_serializer.is_valid():
        mars_station_serializer.save()
        return Response(mars_station_serializer.data)
    return Response(mars_station_serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# Удаляет марсианскую станцию по ID
@api_view(['DELETE'])
def DELETE_MarsStation(request, pk, format=None):
    if not MarsStation.objects.filter(pk=pk).exists():
        return Response(f"ERROR! There is no such object!")

    print('[INFO] API DELETE [DELETE_MarsStation]')
    mars_station = get_object_or_404(MarsStation, pk=pk)
    mars_station.delete()
    return Response('Successfully deleted', status=status.HTTP_204_NO_CONTENT)

# ==================================================================================
# М-М
# ==================================================================================

# Обновляет информацию о марсианской станции по ID
@api_view(['PUT'])
def PUT_Location(request, pk, format=None):
    print('[INFO] API PUT [PUT_Location]')
    location = get_object_or_404(Location, pk=pk)

    # Изменяем значение sequence_number
    try:
        try:
            location.sequence_number = int(request.data['sequence_number'])
            # Сохраняем объект Location
            location.save()
            location_serializer = LocationSerializer(location)
            return Response(location_serializer.data)
        except ValueError:
            return Response('Invalid sequence number format', status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response('Sequence number not provided in the request', status=status.HTTP_400_BAD_REQUEST)


# Удаляет марсианскую станцию по ID
@api_view(['DELETE'])
def DELETE_Location(request, pk, format=None):
    print('[INFO] API DELETE [DELETE_Location]')
    location = get_object_or_404(Location, pk=pk)

    # Удаляет связанную марсианскую станцию
    location.id_mars_station.delete()
    # Затем удалим сам объект Location
    location.delete()

    return Response('Successfully deleted', status=status.HTTP_204_NO_CONTENT)
