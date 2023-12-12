from django.http import QueryDict
from django.core.handlers.asgi import ASGIRequest
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.http import Http404
from rest_framework import status, generics
from drf_yasg.utils import swagger_auto_schema
# Полномочия
from bmstu_lab.views import IsModerator

from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, BasePermission
from bmstu_lab.permissions import IsModerator, IsAuthenticated, create_access_token, create_refresh_token, \
    get_jwt_payload, get_access_token, get_refresh_token, add_in_blacklist

from bmstu_lab.serializers import GeographicalObjectSerializer, MarsStationSerializer, LocationSerializer, \
    TransportSerializer, EmployeeSerializer, UsersSerializer, TypeTransportSerializer, GeographicalObjectPhotoSerializer
from bmstu_lab.models import GeographicalObject, MarsStation, Location, Transport, Employee, Users
from bmstu_lab.DB_Minio import DB_Minio

# Дата
# from datetime import datetime
from datetime import date
# Время прогрузки, получение данных, запросов
import threading, tempfile, requests
# Изображение
from PIL import Image
import io, json
# Возвращает список географические объекты
from rest_framework.pagination import PageNumberPagination


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
@permission_classes([AllowAny])
@authentication_classes([SessionAuthentication, BasicAuthentication])
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

    # Получение ID черновика
    id_draft_service = None
    try:
        # Получаем пользователя
        error_message, token = get_access_token(request)
        payload = get_jwt_payload(token)
        id = payload['id']

        user = Users.objects.get(id=id)
        if user.is_moderator:
            return Response(data={'error': f'Error, user isnt employee'}, status=status.HTTP_400_BAD_REQUEST)

        employee = get_object_or_404(Employee, pk=id)
        try:
            # Находим заявку с таким статусом
            mars_station = MarsStation.objects.filter(
                status_task=1,
                status_mission=1,
                id_employee=employee
            ).last()
            if mars_station:
                id_draft_service = mars_station.id
        except MarsStation.DoesNotExist:
            id_draft_service = {"error": "MarsStation not found"}
    except Exception as error:
        # id_draft_service = {"error": error}
        pass

    # Создадим словарь с желаемым форматом ответа
    response_data = {
        "count": paginator.page.paginator.count,
        "next": paginator.get_next_link(),
        "previous": paginator.get_previous_link(),
        "id_draft_service": id_draft_service,
        "results": geographical_object_serializer.data
    }

    return Response(response_data)


@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([SessionAuthentication, BasicAuthentication])
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
        DB.put_object_url(bucket_name='mars', object_name=feature + '.jpg', url=url_photo)
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


@swagger_auto_schema(method='post', request_body=GeographicalObjectSerializer)
@api_view(['POST'])
@permission_classes([IsModerator])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def POST_GeograficObject(request, format=None):
    serializer = GeographicalObjectSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Обновляет информацию о географическом объекте по ID
@swagger_auto_schema(method='put', request_body=GeographicalObjectSerializer)
@api_view(['PUT'])
@permission_classes([IsModerator])
@authentication_classes([SessionAuthentication, BasicAuthentication])
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
@permission_classes([IsModerator])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def DELETE_GeograficObject(request, pk, format=None):
    if not GeographicalObject.objects.filter(pk=pk).exists():
        return Response(f"ERROR! There is no such object!")

    print('[INFO] API DELETE [DELETE_GeograficObjects]')
    geographical_object = get_object_or_404(GeographicalObject, pk=pk)
    geographical_object.delete()
    return Response(data={"message": 'Successfully deleted'}, status=status.HTTP_204_NO_CONTENT)


# Добавляет новую запись в заявку
@swagger_auto_schema(method='post', request_body=GeographicalObjectSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def POST_GeograficObject_IN_MarsStation(request, pk_service, format=None):
    print('[INFO] API POST [POST_GeograficObject_IN_MarsStation]')
    # Проверим на наличие объекта с заданным pk
    try:
        geographical_object = GeographicalObject.objects.get(pk=pk_service)
    except GeographicalObject.DoesNotExist:
        return Response({'error': f'ERROR! Object GeographicalObject there is no such object by ID!'},
                        status=status.HTTP_404_NOT_FOUND)

    # Получаем пользователя
    error_message, token = get_access_token(request)
    payload = get_jwt_payload(token)
    id = payload['id']

    user = Users.objects.get(id=id)
    if user.is_moderator:
        return Response(data={'error': f'Error, user isnt employee'}, status=status.HTTP_400_BAD_REQUEST)

    employee = get_object_or_404(Employee, pk=id)
    # Находим заявку с таким статусом
    mars_station = MarsStation.objects.filter(
        status_task=1,
        status_mission=1,
        id_employee=employee
    ).last()

    # Если такой заявки нет, то создаем
    if mars_station == None:
        # status_task [1: Черновик; 2: В работе; 3: Завершена; 4: Отменена; 5: Удалена]
        # status_mission [1: Успех; 2: Потеря; 3: Работает]

        mars_station = MarsStation.objects.create(
            date_create=date.today(),
            status_task=1,
            status_mission=1,
            id_employee=employee
        )
        print({"message": 'Create new statement'})

    location = Location.objects.filter(id_mars_station_id=mars_station.id).all()
    location_serializer = LocationSerializer(location, many=True)

    # Создание записи в таблице Location для связи между MarsStation и GeographicalObject
    Location.objects.create(
        id_geographical_object=geographical_object,
        id_mars_station=mars_station,
        sequence_number=int(location_serializer.data.__len__() + 1)
    )

    # Получаем список географических объектов от ID черновика или других статусов
    geographical_object = GeographicalObject.objects.filter(location__id_mars_station=mars_station)
    geographical_objects_serializer = GeographicalObjectSerializer(geographical_object, many=True)

    data = {
        'message': f'Successfully created!',
        'id_draft': mars_station.id,
        'geographical_object': geographical_objects_serializer.data
    }

    return Response(data=data, status=status.HTTP_201_CREATED)


# ==================================================================================
# ЗАЯВКА
# ==================================================================================

def info_request_mars_station(request=None, pk_mars_station=None, format=None):
    try:
        mars_station = get_object_or_404(MarsStation, pk=pk_mars_station)
    except Http404 as error:
        return Response({"message": "MarsStation not found", "error": str(error)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as error:
        return Response({"message": "An error occurred", "error": str(error)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    try:
        transport = get_object_or_404(Transport, id=mars_station.id_transport_id)
    except Http404 as error:
        transport = None
    #     return Response({"message": "Transport not found", "error": str(error)}, status=status.HTTP_404_NOT_FOUND)
    # except Exception as error:
    #     return Response({"message": "An error occurred", "error": str(error)},
    #                     status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    try:
        employee = get_object_or_404(Employee, id=mars_station.id_employee_id)
        try:
            user = get_object_or_404(Users, id=employee.id_user_id)
        except Http404 as error:
            return Response({"message": "Users not found", "error": str(error)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as error:
            return Response({"message": "An error occurred", "error": str(error)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Http404 as error:
        return Response({"message": "Employee not found", "error": str(error)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as error:
        return Response({"message": "An error occurred", "error": str(error)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    try:
        moderator = get_object_or_404(Employee, id=mars_station.id_moderator_id)
    except Http404 as error:
        moderator = None
    #     return Response({"message": "Moderator not found", "error": str(error)}, status=status.HTTP_404_NOT_FOUND)
    # except Exception as error:
    #     return Response({"message": "An error occurred", "error": str(error)},
    #                     status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    locations = Location.objects.filter(id_mars_station=mars_station.id)
    geographical_object_serializer = []

    for location in locations:
        try:
            geographical_object = get_object_or_404(GeographicalObject, id=location.id_geographical_object.id)
            geographical_object_serializer.append(GeographicalObjectSerializer(geographical_object).data)
        except Http404 as error:
            return Response({"message": "GeographicalObject not found", "error": str(error)},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as error:
            return Response({"message": "An error occurred", "error": str(error)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    response = {
        "id": pk_mars_station,
        "type_status": mars_station.type_status,
        "date_create": mars_station.date_create,
        "date_form": mars_station.date_form,
        "date_close": mars_station.date_close,
        "status_task": mars_station.get_status_task_display_word(),
        "status_mission": mars_station.get_status_mission_display_word(),
        "employee": EmployeeSerializer(employee).data,
        "moderator": EmployeeSerializer(moderator).data,
        "transport": TransportSerializer(transport).data,
        "geographical_object": geographical_object_serializer
    }

    return Response(response)


# Возвращает список марсианских станций
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def GET_MarsStationList(request, format=None):
    print('[INFO] API GET [GET_MarsStation]')
    error_message, token = get_access_token(request)
    payload = get_jwt_payload(token)
    id = payload['id']

    employee = get_object_or_404(Employee, pk=id) if not request.user.is_staff else None

    # Если это не модератор, то выводит конкретные его заявки
    if not employee.id_user.is_moderator:
        mars_station = MarsStation.objects.filter(id_employee=employee.id)
    # Для модератора доступны все заявки
    else:
        mars_station = MarsStation.objects.all()

    # Получим параметры запроса из URL
    params = {
        'status_task__in': request.GET.get('status_task').split(';') if request.GET.get('status_task') else [],
        'status_mission': request.GET.get('status_mission'),
        'date_create': request.GET.get('date_create'),
        'date_close': request.GET.get('date_close'),
    }
    date_form_after = request.GET.get('date_form_after')
    date_form_before = request.GET.get('date_form_before')

    # Проверим, пустой ли запрос на фильтр
    if (all(value is None for value in params.values())
            and date_form_after is None
            and date_form_before is None
    ):
        # Вызываем функцию get_mars_station_info для каждой станции
        result_data = [info_request_mars_station(pk_mars_station=station.pk).data for station in mars_station]
        return Response(result_data)
    # Формируем фильтры на основе параметров запроса
    filters = Q()

    for key, value in params.items():
        if value is not None:
            if key == 'status_task':
                filters &= Q(**{f'{key}__in': value})
            else:
                filters &= Q(**{key: value})

    # Добавим фильтры по дате
    if date_form_after and date_form_before:
        if date_form_after > date_form_before:
            return Response('Mistake! It is impossible to sort when "BEFORE" exceeds "AFTER"!')
        filters &= Q(date_form__gte=date_form_after, date_form__lte=date_form_before)
    elif date_form_after:
        filters &= Q(date_form__gte=date_form_after)
    elif date_form_before:
        filters &= Q(date_form__lte=date_form_before)

    # Применяем фильтры к mars_station
    if filters:
        mars_station = mars_station.filter(filters)

    # Вызываем функцию get_mars_station_info для каждой станции
    result_data = [info_request_mars_station(pk_mars_station=station.pk).data for station in mars_station]
    return Response(result_data)


# Возвращает данные о марсианской станции
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def GET_MarsStation(request, pk=None, format=None):
    print('[INFO] API GET [GET_MarsStation]')
    if request.method == 'GET':
        try:
            return info_request_mars_station(request, pk_mars_station=pk)
        except Exception as error:
            return Response({"message": error}, status=status.HTTP_404_NOT_FOUND)


# Обновляет информацию о марсианской станции по ID
@swagger_auto_schema(method='put', request_body=MarsStationSerializer)
@api_view(['PUT'])
@permission_classes([IsModerator])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def PUT_MarsStation(request, pk, format=None):
    print('[INFO] API PUT [PUT_MarsStation]')
    mars_station = get_object_or_404(MarsStation, pk=pk)
    # Обновление текущего дата
    request.data['date_form'] = date.today()
    mars_station_serializer = MarsStationSerializer(mars_station, data=request.data)
    if mars_station_serializer.is_valid():
        mars_station_serializer.save()
        return Response(mars_station_serializer.data)
    return Response(mars_station_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Обновляет информацию о марсианской станции по ID создателя
@swagger_auto_schema(method='put', request_body=MarsStationSerializer)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def PUT_MarsStation_BY_USER(request, pk, format=None):
    print('[INFO] API PUT [PUT_MarsStation_BY_USER]')
    error_message, token = get_access_token(request)
    payload = get_jwt_payload(token)
    id = payload['id']

    user = Users.objects.get(id=id)
    if user.is_moderator:
        return Response(data={'error': f'Error, user isnt employee'}, status=status.HTTP_400_BAD_REQUEST)

    employee = get_object_or_404(Employee, pk=id)

    try:
        mars_station = MarsStation.objects.get(pk=pk)
    except MarsStation.DoesNotExist:
        return Response({"error": 'MarsStation not found'}, status=status.HTTP_404_NOT_FOUND)

    if mars_station.status_task == request.data['status_task']:
        return Response(
            {'error': f'This application already has the status "{mars_station.get_status_task_display_word()}"'},
            status=status.HTTP_400_BAD_REQUEST)

    if mars_station.status_task in [3, 4]:
        return Response({'error': 'You cant edit it because the application process has already been completed'},
                        status=status.HTTP_400_BAD_REQUEST)

    if request.data['status_task'] in [2, 5]:
        mars_station.status_task = request.data['status_task']
        id_draft = mars_station.id
        # Асинхронный веб-сервис
        url = 'http://127.0.0.1:5000/api/async_calc/'

        data = {
            'id_draft': id_draft,
            'access_token': token
        }
        try:
            response = requests.post(url, data=data)

            if response.status_code == 200:
                mars_station.status_mission = 1
            else:
                mars_station.status_mission = 0

            mars_station.save()
        except Exception as error:
            print(error)
        return Response({'message': 'Successfully updated status'})
    else:
        return Response({'error': 'You are not moderator! Check status in [2, 4, 5]'})


# Обновляет информацию о марсианской станции по ID модератора
@swagger_auto_schema(method='put', request_body=MarsStationSerializer)
@api_view(['PUT'])
@permission_classes([IsModerator])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def PUT_MarsStation_BY_ADMIN(request, pk, format=None):
    print('[INFO] API PUT [PUT_MarsStation_BY_ADMIN]')
    error_message, token = get_access_token(request)
    payload = get_jwt_payload(token)
    id = payload['id']

    try:
        mars_station = MarsStation.objects.get(pk=pk)
    except MarsStation.DoesNotExist:
        return Response({'message': 'MarsStation not found!'}, status=status.HTTP_404_NOT_FOUND)
    # Изначальный статус заявки должн быть 'В работе'
    if mars_station.status_task != 2:
        return Response({'message': 'Mistake! The application must have the status "В работе"!'},
                        status=status.HTTP_400_BAD_REQUEST)

    if request.data['status_task'] in [3, 4]:
        mars_station.date_form = date.today()
        mars_station.status_task = request.data['status_task']
        mars_station.status_mission = request.data['status_mission']
        mars_station.id_moderator_id = id

        if request.data['status_task'] in [3, 4]:
            mars_station.date_close = date.today()

        mars_station.save()

        return Response({'message': 'Successfully updated status'})
    else:
        return Response({'message': 'You dont updated status "IN PROCESS"! Check status in [3, 4]'})


# Удаляет марсианскую станцию по ID
@api_view(['DELETE'])
@permission_classes([IsModerator])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def DELETE_MarsStation(request, pk, format=None):
    if not MarsStation.objects.filter(pk=pk).exists():
        return Response(f'ERROR! There is no such object!')

    print('[INFO] API DELETE [DELETE_MarsStation]')
    mars_station = get_object_or_404(MarsStation, pk=pk)
    mars_station.delete()
    return Response({'message': 'Successfully deleted'}, status=status.HTTP_204_NO_CONTENT)


# ==================================================================================
# М-М
# ==================================================================================

# Обновляет информацию о марсианской станции по ID
@swagger_auto_schema(method='put', request_body=LocationSerializer)
@api_view(['PUT'])
@permission_classes([IsModerator])
@authentication_classes([SessionAuthentication, BasicAuthentication])
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
            return Response({'message': 'Invalid sequence number format'}, status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response({'message': 'Sequence number not provided in the request'}, status=status.HTTP_400_BAD_REQUEST)


# Удаляет марсианскую станцию по ID
@api_view(['DELETE'])
@permission_classes([IsModerator])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def DELETE_Location(request, pk, format=None):
    print('[INFO] API DELETE [DELETE_Location]')
    location = get_object_or_404(Location, pk=pk)

    # Удаляет связанную марсианскую станцию
    location.id_mars_station.delete()
    # Затем удалим сам объект Location
    location.delete()

    return Response({'message': 'Successfully deleted'}, status=status.HTTP_204_NO_CONTENT)


# ==================================================================================
# ДЕТАЛЬНАЯ ИНФОРМАЦИЯ О ТРАНСПОРТАХ
# ==================================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([SessionAuthentication, BasicAuthentication])
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

# ==================================================================================
# АСИНХРОННЫЙ ВЕБ СЕРВИС
# ==================================================================================

@api_view(['PUT'])
@permission_classes([AllowAny])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def PUT_async_result(request, format=None):
    print('[INFO] API PUT [PUT_async_result]')
    try:
        # Преобразуем строку в объект Python JSON
        json_data = json.loads(request.body.decode('utf-8'))
        print(json_data)

        payload = get_jwt_payload(json_data['access_token'])
        id = payload['id']
        employee = get_object_or_404(Employee, pk=id) if not request.user.is_staff else None
        # Изменяем значение sequence_number
        try:
            # Выводит конкретную заявку создателя
            mars_station = get_object_or_404(MarsStation, id_employee=employee.id, pk=json_data['id_draft'])
            mars_station.status_mission = json_data['status_mission']
            # Сохраняем объект Location
            mars_station.save()
            mars_station_serializer = MarsStationSerializer(mars_station, many=False)
            return Response(data={'message': 'Successfully updated!', 'data': mars_station_serializer.data},
                            status=status.HTTP_200_OK)
        except ValueError:
            return Response({'message': 'Invalid sequence number format'}, status=status.HTTP_400_BAD_REQUEST)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return Response(data={'message': 'Error decoding JSON'}, status=status.HTTP_400_BAD_REQUEST)