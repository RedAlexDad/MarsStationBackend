# views.py - обработчик приложения
from rest_framework.response import Response
from rest_framework.decorators import api_view, parser_classes
from rest_framework import status, generics
from django.shortcuts import get_object_or_404

from bmstu_lab.serializers import GeographicalObjectSerializer, MarsStationSerializer, LocationSerializer, \
    TransportSerializer, EmployeeSerializer, UsersSerializer, TypeTransportSerializer, GeographicalObjectPhotoSerializer
from bmstu_lab.models import GeographicalObject, MarsStation, Location, Transport, Employee, Users

from bmstu_lab.DB_Minio import DB_Minio
from datetime import datetime
from rest_framework.parsers import MultiPartParser, FormParser
from PIL import Image
import io
import requests
# Возвращает список географические объекты
from rest_framework.pagination import PageNumberPagination
# Время прогрузки и получение данных
import threading
import tempfile

# ==================================================================================
# УСЛУГА
# ==================================================================================
class CustomPageNumberPagination(PageNumberPagination):
    # Количество элементов на странице
    page_size = 5
    # Параметр запроса для изменения количества элементов на странице
    page_size_query_param = 'page_size'
    # Максимальное количество элементов на странице
    max_page_size = 10

@api_view(['GET'])
def GET_GeographicalObjects(request, pk=None, format=None):
    print('[INFO] API GET [GET_GeographicalObject_PAGINATIONS]')

    # Получим параметры запроса из URL
    feature = request.GET.get('feature')
    type = request.GET.get('type')
    size = request.GET.get('size')
    describe = request.GET.get('describe')
    status = request.GET.get('status')

    # Получение данные после запроса с БД (через ORM)
    geographical_object = GeographicalObject.objects.all()

    def update_url_photo():
        # Получение данные с MINIO и обновление ссылок на него (фотография) и измением данные
        try:
            try:
                DB = DB_Minio()
                for obj in geographical_object:
                    # Проверяет, существует ли такой объект в бакете
                    check_object = DB.stat_object(bucket_name='mars', object_name=obj.feature + '.jpg')
                    if bool(check_object):
                        obj.photo = DB.get_presigned_url(
                            method='GET', bucket_name='mars',
                            object_name=obj.feature + '.jpg'
                        )
                    else:
                        obj.photo = None
                    # Сохраняем обновленный объект в БД
                    obj.save()
            except Exception as ex:
                print(f"Ошибка при обработке объекта {obj.feature}: {str(ex)}")
        except Exception as ex:
            print('Ошибка соединения с БД Minio', ex)

    # Создадим поток для выполнения операций Minio
    thread = threading.Thread(target=update_url_photo)
    thread.start()

    # Подождем завершения потока с ожиданием в течение 3 секунд
    thread.join(timeout=3)

    if feature and type and size and describe and status is None:
        pass
    else:
        # Применим фильтры на основе параметров запроса, если они предоставлены
        if feature:
            geographical_object = geographical_object.filter(feature__icontains=feature)
        if type:
            geographical_object = geographical_object.filter(type__icontains=type)
        if size:
            geographical_object = geographical_object.filter(size=size)
        if describe:
            geographical_object = geographical_object.filter(describe__icontains=describe)
        if status:
            geographical_object = geographical_object.filter(status=status)

    paginator = CustomPageNumberPagination()
    result_page = paginator.paginate_queryset(geographical_object, request)
    geographical_object_serializer = GeographicalObjectSerializer(result_page, many=True)

    return paginator.get_paginated_response(geographical_object_serializer.data)


@api_view(['GET'])
def GET_GeographicalObject(request, pk=None, format=None):
    print('[INFO] API GET [GET_GeographicalObject]')
    if request.method == 'GET':
        geographical_object = get_object_or_404(GeographicalObject, pk=pk)
        def update_url_photo():
            try:
                DB = DB_Minio()
                # Проверяет, существует ли такой объект в бакете
                check_object = DB.stat_object(bucket_name='mars', object_name=geographical_object.feature + '.jpg')
                if bool(check_object):
                    photo = DB.get_presigned_url(
                        method='GET', bucket_name='mars',
                        object_name=geographical_object.feature + '.jpg'
                    )
                else:
                    photo = None

                geographical_object.photo = photo
                geographical_object.save()
            except Exception as ex:
                print(f"Ошибка при обработке объекта {geographical_object.feature}: {str(ex)}")

        # Создадим поток для выполнения операций Minio
        thread = threading.Thread(target=update_url_photo)
        thread.start()

        # Подождем завершения потока с ожиданием в течение 3 секунд
        thread.join(timeout=1)

        geographical_object_serializer = GeographicalObjectSerializer(geographical_object)
        return Response(geographical_object_serializer.data)

def process_image_from_url(feature, url_photo):
    if url_photo:
        DB = DB_Minio()
        DB.put_object_url(bucket_name='mars', object_name=feature+'.jpg', url=url_photo)
        # Загрузите данные по URL
        response = requests.get(url_photo)
        if response.status_code == 200:
            # Возврат данных в бинарном виде (в байтах)
            image_data = response.content

            # Используем Pillow для обработки изображения и сохранения его в формате JPEG
            try:
                image = Image.open(io.BytesIO(image_data))
                image = image.convert('RGB')  # Преобразование изображения в формат RGB
                output_buffer = io.BytesIO()
                image.save(output_buffer, format='JPEG')
                jpeg_data = output_buffer.getvalue()
                return jpeg_data
            except Exception as ex:
                return None  # Возвращаем None в случае ошибки при обработке изображения
        else:
            return None  # Возвращаем None в случае ошибки при получении изображения по URL
    else:
        # Если нет URL изображения, возвращаем None
        return None

@api_view(['POST'])
def POST_GeograficObject(request, format=None):
    serializer = GeographicalObjectSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Обновляет информацию о географическом объекте по ID
@api_view(['PUT'])
def PUT_GeograficObject(request, pk, format=None):
    print('[INFO] API PUT [PUT_GeograficObject]')
    geographical_object = get_object_or_404(GeographicalObject, pk=pk)

    photo = request.FILES.get('photo')
    if photo:
        DB = DB_Minio()
        url_photo = None
        check_object = False
        def update_url_photo():
            # Используем nonlocal для доступа к внешней переменной url_photo
            nonlocal url_photo, check_object
            try:
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    temp_file.write(photo.read())
                    # Сбросить указатель на файл
                    temp_file.seek(0)
                    # Загрузка файла в бакет
                    DB.fput_object(bucket_name='mars', object_name=photo.name, file_path=temp_file.name)
                    # Проверяет, существует ли такой объект в бакете
                    check_object = DB.stat_object(bucket_name='mars', object_name=photo.name)
                    # Get the presigned URL
                    if bool(check_object):
                        url_photo = DB.get_presigned_url(
                            method='GET', bucket_name='mars',
                            object_name=photo.name
                        )
            except Exception as ex:
                print(f"Ошибка при обработке объекта {photo.name}: {str(ex)}")

        # Создадим поток для выполнения операций Minio
        thread = threading.Thread(target=update_url_photo)
        thread.start()
        # Подождем завершения потока с ожиданием в течение 3 секунд
        thread.join(timeout=10)

        if not thread.is_alive() and bool(check_object) is False:
            return Response({'error': 'Timeout while waiting for URL update'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if url_photo:
            serializer = GeographicalObjectPhotoSerializer(geographical_object, data={'id': pk, 'photo': url_photo})
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Successfully uploaded and linked to the photo', 'data': serializer.data},
                                status=status.HTTP_200_OK)

        return Response({'error': 'No photo provided'}, status=status.HTTP_400_BAD_REQUEST)

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
def POST_GeograficObject_IN_MarsStation(request, pk_service, format=None):
    print('[INFO] API POST [POST_GeograficObject_IN_MarsStation]')
    # Проверим на наличие объекта с заданным pk
    try:
        geographical_object = GeographicalObject.objects.get(pk=pk_service)
    except GeographicalObject.DoesNotExist:
        return Response(f"ERROR! Object GeographicalObject there is no such object by ID!",
                        status=status.HTTP_404_NOT_FOUND)

    # Находим заявку с таким статусом
    mars_station = MarsStation.objects.filter(status_task=1, status_mission=3).last()
    # Если такой заявки нет, то создаем
    if mars_station == None:
        # status_task [1: Введен; 2: В работе; 3: Завершена; 4: Отменена; 5: Удалена]
        # status_mission [1: Успех; 2: Потеря; 3: Работает]
        mars_station = MarsStation.objects.create(
            date_create=datetime.now(),
            status_task=1,
            status_mission=3,
        )
        print('Create new statement')

    # Создание записи в таблице Location для связи между MarsStation и GeographicalObject
    Location.objects.create(
        id_geographical_object=geographical_object,
        id_mars_station=mars_station,
    )
    return Response(f'Successfully created, ID: {mars_station.id}', status=status.HTTP_201_CREATED)


# ==================================================================================
# ЗАЯВКА
# ==================================================================================

# Возвращает список марсианских станций
@api_view(['GET'])
def GET_MarsStationList(request, format=None):
    print('[INFO] API GET [GET_MarsStation]')
    mars_station = MarsStation.objects.all()

    # Получим параметры запроса из URL
    type_status = request.GET.get('type_status')
    status_task = request.GET.get('status_task')
    status_mission = request.GET.get('status_mission')
    date_create = request.GET.get('date_create')
    date_close = request.GET.get('date_close')
    # Дата после
    date_form_after = request.GET.get('date_form_after')
    # Дата ДО
    date_form_before = request.GET.get('date_form_before')

    # Проверяет, пустой запрос на фильтр
    if all(item is None for item in
           [type_status, status_task, status_mission, date_create, date_close, date_form_after, date_form_before]):
        # Сериализиуем его, чтобы получить в формате JSON
        mars_station_serializer = MarsStationSerializer(mars_station, many=True)
    else:
        # Применим фильтры на основе параметров запроса, если они предоставлены
        if type_status:
            mars_station = mars_station.filter(type_status=type_status)
        if status_task:
            mars_station = mars_station.filter(status_task=status_task)
        if status_mission:
            mars_station = mars_station.filter(status_mission=status_mission)
        if date_create:
            mars_station = mars_station.filter(date_create=date_create)
        if date_close:
            mars_station = mars_station.filter(date_close=date_close)

        # Дата формирования ПОСЛЕ
        if date_form_after and date_form_before is None:
            mars_station = mars_station.filter(date_form__gte=date_form_after)
        # Дата формирования ДО
        if date_form_after is None and date_form_before:
            mars_station = mars_station.filter(date_form__lte=date_form_before)

        # Дата формирования ПОСЛЕ и ДО
        if date_form_after and date_form_before:
            if date_form_after > date_form_before:
                return Response('Mistake! It is impossible to sort when "BEFORE" exceeds "AFTER"!')
            mars_station = mars_station.filter(date_form__gte=date_form_after)
            mars_station = mars_station.filter(date_form__lte=date_form_before)

        # Сериализуем результаты запроса
        mars_station_serializer = MarsStationSerializer(mars_station, many=True)

    return Response(mars_station_serializer.data)


# Возвращает данные о марсианской станции
@api_view(['GET'])
def GET_MarsStation(request, pk=None, format=None):
    print('[INFO] API GET [GET_MarsStation]')
    if request.method == 'GET':
        try:
            mars_station = get_object_or_404(MarsStation, pk=pk)
        except MarsStation.DoesNotExist:
            return Response({"error": "MarsStation not found"}, status=status.HTTP_404_NOT_FOUND)
        try:
            transport = get_object_or_404(Transport, id=mars_station.id_transport.id)
        except Transport.DoesNotExist:
            transport = None  # Транспорт не найден, устанавливаем moderator в None

        try:
            employee = get_object_or_404(Employee, id=mars_station.id_employee.id)
            try:
                user = get_object_or_404(Users, id=employee.id_user.id)
            except Users.DoesNotExist:
                user = None
        except Employee.DoesNotExist:
            employee = None  # Сотрудник не найден, устанавливаем employee в None

        try:
            moderator = get_object_or_404(Employee, id=mars_station.id_moderator.id)
        except Employee.DoesNotExist:
            moderator = None  # Модератор не найден, устанавливаем moderator в None

        locations = Location.objects.filter(id_mars_station=mars_station.id)
        geographical_object_serializer = []

        for location in locations:
            try:
                geographical_object = get_object_or_404(GeographicalObject, id=location.id_geographical_object.id)
                geographical_object_serializer.append(GeographicalObjectSerializer(geographical_object).data)
            except GeographicalObject.DoesNotExist:
                geographical_object_serializer.append({"error": "Geographical Object not found"})

        response = {
            "employee": EmployeeSerializer(employee).data,
            "moderator": EmployeeSerializer(moderator).data,
            "mars_station": MarsStationSerializer(mars_station).data,
            "transport": TransportSerializer(transport).data,
            "geographical_object": geographical_object_serializer
        }

        return Response(response)


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
    print('[INFO] API PUT [PUT_MarsStation_BY_USER]')
    if request.data['status_task'] in [4, 5]:
        try:
            mars_station = MarsStation.objects.get(pk=pk)
        except MarsStation.DoesNotExist:
            return Response("MarsStation not found", status=status.HTTP_404_NOT_FOUND)

        mars_station.status_task = request.data['status_task']

        if 'id_employee' in request.data:
            new_id_employee = request.data['id_employee']
            try:
                new_employee = Employee.objects.get(pk=new_id_employee)
                mars_station.id_employee = new_employee
                mars_station.save()
                return Response("Successfully updated status")
            except Employee.DoesNotExist:
                return Response("New moderator not found", status=status.HTTP_404_NOT_FOUND)
        # return Response(mars_station_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response('You are not moderator! Check status in [4, 5]')


# Обновляет информацию о марсианской станции по ID создателя
@api_view(['PUT'])
def PUT_MarsStation_BY_ADMIN(request, pk, format=None):
    print('[INFO] API PUT [PUT_MarsStation_BY_ADMIN]')
    if request.data['status_task'] in [2, 3, 4, 5]:
        try:
            mars_station = MarsStation.objects.get(pk=pk)
        except MarsStation.DoesNotExist:
            return Response("MarsStation not found", status=status.HTTP_404_NOT_FOUND)

        mars_station.date_form = datetime.today()
        mars_station.status_task = request.data['status_task']
        mars_station.status_mission = request.data['status_mission']
        if request.data['status_task'] in [3, 4, 5]:
            mars_station.date_close = datetime.today()

        if 'id_moderator' in request.data:
            new_moderator_id = request.data['id_moderator']
            try:
                new_moderator = Employee.objects.get(pk=new_moderator_id)
                mars_station.id_moderator = new_moderator
                mars_station.save()
                return Response("Successfully updated status")
            except Employee.DoesNotExist:
                return Response("New moderator not found", status=status.HTTP_404_NOT_FOUND)
    else:
        return Response('You dont updated status "IN PROCESS"! Check status in [2, 3, 4, 5]')


# Удаляет марсианскую станцию по ID
@api_view(['DELETE'])
def DELETE_MarsStation(request, pk, format=None):
    if not MarsStation.objects.filter(pk=pk).exists():
        return Response(f"ERROR! There is no such object!")

    print('[INFO] API DELETE [DELETE_MarsStation]')
    mars_station = get_object_or_404(MarsStation, pk=pk)
    mars_station.delete()
    return Response('Successfully deleted', status=status.HTTP_204_NO_CONTENT)


# Возвращает список транспортов марсианских станций МАРСОЛЕТЫ
@api_view(['GET'])
def GET_TransportList_AIRCRAFT(request, format=None):
    print('[INFO] API GET [GET_TransportList]')
    transport = Transport.objects.filter(type='Mars aircraft')
    # Сериализиуем его, чтобы получить в формате JSON
    transport_serializer = TransportSerializer(transport, many=True)
    return Response(transport_serializer.data)


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
            location.id_geographical_object_id = int(request.data['id_geographical_object'])
            location.id_mars_station_id = int(request.data['id_mars_station'])
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

# ==================================================================================
# ДЕТАЛЬНАЯ ИНФОРМАЦИЯ О ТРАНСПОРТАХ
# ==================================================================================

@api_view(['GET'])
def GET_Transport(request, format=None):
    print('[INFO] API GET [GET_TransportList]')
    type_transport = request.GET.get('type')

    # Обработка фильтрации по типу транспорта
    if type_transport:
        transport = Transport.objects.filter(type=type_transport)
    else:
        transport = Transport.objects.all()

    # Сериализируем список транспортов
    transport_serializer = TypeTransportSerializer(transport, many=True)

    return Response(transport_serializer.data)