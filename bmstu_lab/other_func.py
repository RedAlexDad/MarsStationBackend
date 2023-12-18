from django.http import QueryDict, HttpResponse, FileResponse
from django.core.handlers.asgi import ASGIRequest
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q, F, Max
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
    TransportSerializer, EmployeeSerializer, UsersSerializer, TypeTransportSerializerID_TYPE, \
    GeographicalObjectPhotoSerializer, MarsStationSerializerDetail
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

    # Получение ID черновика
    id_draft_service = None
    try:
        # Получаем пользователя
        error_message, token = get_access_token(request)
        payload = get_jwt_payload(token)
        id = payload['id']

        user = Users.objects.get(id=id)
        if user.is_moderator:
            return Response(data={'message': f'Ошибка, аккаунт не является сотрудником'}, status=status.HTTP_400_BAD_REQUEST)

        employee = Employee.objects.get(id_user=id)
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
            id_draft_service = {'message': 'Марсианская станция чернового варианта не найдена'}
    except Exception as error:
        # id_draft_service = {'error': error}
        pass

    # Пагинации
    paginator = PageNumberPagination()
    # Количество элементов на странице
    paginator.page_size = 5
    # Параметр запроса для изменения количества элементов на странице
    paginator.page_size_query_param = 'page_size'
    # Максимальное количество элементов на странице
    paginator.max_page_size = 5

    result_page = paginator.paginate_queryset(geographical_object, request)
    geographical_object_serializer = GeographicalObjectSerializer(result_page, many=True)

    # Создадим словарь с желаемым форматом ответа
    response_data = {
        'count': paginator.page.paginator.count,
        'id_draft_service': id_draft_service,
        'results': geographical_object_serializer.data
    }

    return Response(response_data)


@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def GET_GeographicalObject(request, pk=None, format=None):
    print('[INFO] API GET [GET_GeographicalObject]')
    if request.method == 'GET':
        if not GeographicalObject.objects.filter(pk=pk).exists():
            return Response(data={'message': f'Не существует географический объект с {pk}'},
                            status=status.HTTP_404_NOT_FOUND)

        geographical_object = GeographicalObject.objects.get(pk=pk)
        return Response(GeographicalObjectSerializer(geographical_object).data)


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


@swagger_auto_schema(method='get', request_body=GeographicalObjectSerializer)
@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def GET_GeograficObject_IMAGE(request, pk):
    if not GeographicalObject.objects.filter(pk=pk).exists():
        return Response(data={'message': f'Не существует географический объект с {pk}'}, status=status.HTTP_404_NOT_FOUND)

    geographical_object = GeographicalObject.objects.get(pk=pk)

    try:
        DB = DB_Minio()
        # Проверяет, существует ли такой объект в бакете
        check_object = DB.stat_object(bucket_name='mars', object_name=geographical_object.feature + '.jpg')
        if bool(check_object):
            photo = DB.get_object(bucket_name='mars', object_name=geographical_object.feature + '.jpg')
            if photo:
                return HttpResponse(photo, content_type='image/jpeg')
            else:
                return Response(data={'message': 'Изображение пусто'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(data={'message': 'Изображение не найдено'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as error:
        print(f'Ошибка при обработке объекта {geographical_object.feature}: {str(error)}')
        return HttpResponse(date={'message': f'Ошибка при обработке объекта\n{error}'}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='put', request_body=GeographicalObjectSerializer)
@api_view(['PUT'])
@permission_classes([AllowAny])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def PUT_GeograficObject_IMAGE(request, pk):
    if not GeographicalObject.objects.filter(pk=pk).exists():
        return Response(data={'message': f'Не существует географический объект с {pk}'},
                        status=status.HTTP_404_NOT_FOUND)

    geographical_object = GeographicalObject.objects.get(pk=pk)
    photo = request.FILES.get('photo')

    if not photo:
        return Response({'message': 'Фотография не предоставлена'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        DB = DB_Minio()
        try:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(photo.read())
                temp_file.seek(0)
                DB.fput_object(bucket_name='mars', object_name=photo.name, file_path=temp_file.name)
        except Exception as ex:
            print(f'Ошибка при обработке объекта {photo.name}: {str(ex)}')
        try:
            image_bytes = io.BytesIO(photo.read())
            # geographical_object.photo = image_bytes.read()
            geographical_object.photo = image_bytes.getvalue()
            geographical_object.save()
        except:
            return Response({'message': 'Ошибка при сохранении фотографии в базе данных'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # Проверяет, существует ли такой объект в бакете
        try:
            check_object = DB.stat_object(bucket_name='mars', object_name=geographical_object.feature + '.jpg')
            if bool(check_object):
                photo = DB.get_object(bucket_name='mars', object_name=geographical_object.feature + '.jpg')
                return HttpResponse(photo, content_type='image/jpeg')
            else:
                return Response(data={'message': 'Изображение не найдено'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as error:
            print(f'Ошибка при обработке объекта {geographical_object.feature}: {str(error)}')
            return HttpResponse(date={'message': f'Ошибка при обработке объекта\n{error}'},
                                status=status.HTTP_400_BAD_REQUEST)
    except Exception as error:
        return Response({'message': error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Обновляет информацию о географическом объекте по ID
@swagger_auto_schema(method='put', request_body=GeographicalObjectSerializer)
@api_view(['PUT'])
@permission_classes([IsModerator])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def PUT_GeograficObject(request, pk, format=None):
    print('[INFO] API PUT [PUT_GeograficObject]')
    geographical_object = get_object_or_404(GeographicalObject, pk=pk)
    serializer = GeographicalObjectSerializer(geographical_object, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Удаляет географический объект по ID
@api_view(['DELETE'])
@permission_classes([IsModerator])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def DELETE_GeograficObject(request, pk, format=None):
    print('[INFO] API DELETE [DELETE_GeograficObjects]')
    if not GeographicalObject.objects.filter(pk=pk).exists():
        return Response(f'Географический объект по {pk} не существует', status=status.HTTP_404_NOT_FOUND)

    geographical_object = get_object_or_404(GeographicalObject, pk=pk)
    geographical_object.status = False
    geographical_object.save()
    return Response(data={'message': 'Географический объект успешно удален'}, status=status.HTTP_200_OK)


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
        return Response(f'Географический объект по {pk_service} не существует', status=status.HTTP_404_NOT_FOUND)

    # Получаем пользователя
    error_message, token = get_access_token(request)
    payload = get_jwt_payload(token)
    id = payload['id']

    user = Users.objects.get(id=id)
    if user.is_moderator:
        return Response(data={'message': f'Аккаунт не является сотрудником'}, status=status.HTTP_400_BAD_REQUEST)

    employee = Employee.objects.get(id_user=id)
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
    # Получаем максимальный порядковый номер для данной марсианской станции
    max_sequence_number = Location.objects.filter(id_mars_station=mars_station).aggregate(Max('sequence_number'))[
        'sequence_number__max']
    # Если нет существующих записей, устанавливаем порядковый номер в 1
    sequence_number = max_sequence_number + 1 if max_sequence_number else 1
    # Создаем новый объект Location
    Location.objects.create(
        id_geographical_object=geographical_object,
        id_mars_station=mars_station,
        sequence_number=sequence_number
    )

    # Получаем список географических объектов от ID черновика или других статусов
    geographical_object = GeographicalObject.objects.filter(location__id_mars_station=mars_station)
    geographical_objects_serializer = GeographicalObjectSerializer(geographical_object, many=True)

    location = Location.objects.filter(id_mars_station_id=mars_station.id).all()
    location_serializer = LocationSerializer(location, many=True)

    data = {
        'message': f'Успешно создана заявка',
        'id_draft': mars_station.id,
        'geographical_object': geographical_objects_serializer.data,
        'location': location_serializer.data
    }

    return Response(data=data, status=status.HTTP_201_CREATED)


# ==================================================================================
# ЗАЯВКА
# ==================================================================================

def info_request_mars_station(request=None, pk_mars_station=None, format=None):
    try:
        mars_station = get_object_or_404(MarsStation, pk=pk_mars_station)
    except Exception as error:
        return Response({'message': f'Марсианская станция по {pk_mars_station} не существует, \nerror: {str(error)}'},
                        status=status.HTTP_404_NOT_FOUND)

    def get_object_or_none(model, **kwargs):
        try:
            return get_object_or_404(model, **kwargs)
        except Http404:
            return None

    transport = get_object_or_none(Transport, id=mars_station.id_transport_id)
    employee = get_object_or_none(Employee, id=mars_station.id_employee_id)
    moderator = get_object_or_none(Employee, id=mars_station.id_moderator_id)

    locations = Location.objects.filter(id_mars_station=mars_station.id)
    geographical_object_serializer = []

    for location in locations:
        geographical_object = get_object_or_none(GeographicalObject, id=location.id_geographical_object.id)
        if geographical_object:
            geographical_object_serializer.append(GeographicalObjectSerializer(geographical_object, many=False).data)
        else:
            return Response({'message': 'Географический объект не найден'},
                            status=status.HTTP_404_NOT_FOUND)
    response = {
        'id': pk_mars_station,
        'type_status': mars_station.type_status,
        'date_create': mars_station.date_create,
        'date_form': mars_station.date_form,
        'date_close': mars_station.date_close,
        'status_task': mars_station.get_status_task_display_word(),
        'status_mission': mars_station.get_status_mission_display_word(),
        'employee': EmployeeSerializer(employee, many=False).data if employee else None,
        'moderator': EmployeeSerializer(moderator, many=False).data if moderator else None,
        'transport': TransportSerializer(transport, many=False).data if transport else None,
        'location': LocationSerializer(locations, many=True).data,
        'geographical_object': geographical_object_serializer
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

    employee = Employee.objects.get(id_user=id) if not request.user.is_staff else None

    # Если это не модератор, то выводит конкретные его заявки
    if not employee.id_user.is_moderator:
        mars_station = MarsStation.objects.filter(id_employee=employee.id)
    # Для модератора доступны все заявки
    else:
        mars_station = MarsStation.objects.all()

    # Получим параметры запроса из URL
    params = {
        'status_mission': request.GET.get('status_mission'),
        'date_create': request.GET.get('date_create'),
        'date_close': request.GET.get('date_close'),
    }
    status_task__in = request.GET.get('status_task').split(',') if request.GET.get('status_task') else []
    date_form_after = request.GET.get('date_form_after')
    date_form_before = request.GET.get('date_form_before')

    # Проверим, пустой ли запрос на фильтр
    if not (all(value is None for value in params.values())
            and date_form_after is None
            and date_form_before is None
            and status_task__in == []
    ):
        # Формируем фильтры на основе параметров запроса
        filters = Q()

        for key, value in params.items():
            if value is not None:
                filters &= Q(**{key: value})

        for key in ['status_task']:
            value = status_task__in
            if value:
                filters &= Q(**{f'{key}__in': value})

        # Добавим фильтры по дате
        if date_form_after and date_form_before:
            if date_form_after > date_form_before:
                return Response({'message': 'Ошибка! Невозможно выполнить сортировку, когда "ДО" превышает "ПОСЛЕ"'}, status=status.HTTP_400_BAD_REQUEST)
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

    # Пагинации
    # paginator = PageNumberPagination()
    # # Количество элементов на странице
    # paginator.page_size = 100
    # # Параметр запроса для изменения количества элементов на странице
    # paginator.page_size_query_param = 'page_size'
    # # Максимальное количество элементов на странице
    # paginator.max_page_size = 100

    # result_page = paginator.paginate_queryset(result_data, request)

    # Создадим словарь с желаемым форматом ответа
    response_data = {
        # 'count': paginator.page.paginator.count,
        # 'next': paginator.get_next_link(),
        # 'previous': paginator.get_previous_link(),
        'results': result_data
    }

    # return Response(response_data)
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
            return Response({'message': error}, status=status.HTTP_404_NOT_FOUND)


# Обновляет информацию о марсианской станции по ID
@swagger_auto_schema(method='put', request_body=MarsStationSerializer)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def PUT_MarsStation(request, pk, format=None):
    print('[INFO] API PUT [PUT_MarsStation]')
    mars_station = get_object_or_404(MarsStation, pk=pk)

    mars_station.type_status = request.data.get('type_status', '')
    mars_station.date_create = request.data.get('date_create')

    employee_data = request.data.get('employee', {})
    moderator_data = request.data.get('moderator', {})
    transport_data = request.data.get('transport', {})


    # Создаем или получаем объекты Employee и Transport
    employee_instance, _ = Employee.objects.get_or_create(id=employee_data.get('id'), defaults=employee_data)
    mars_station.id_employee = employee_instance

    try:
        moderator_instance, _ = Employee.objects.get_or_create(id=moderator_data.get('id'), defaults=moderator_data)
        mars_station.id_moderator = moderator_instance
    except Exception as error:
        print(error)

    try:
        default_values = {'describe': '', 'name': '', 'photo': '', 'type': ''}
        # Объединяем данные транспорта с дополнительными значениями по умолчанию
        merged_data = {**default_values, **transport_data[0]}
        transport_instance, _ = Transport.objects.get_or_create(id=merged_data.get('id'), defaults=merged_data)
        mars_station.id_transport = transport_instance
    except Exception as error:
        print(error)

    mars_station.status_task = mars_station.convert_status_task_string_to_number(request.data.get('status_task'))
    mars_station.status_mission = mars_station.convert_status_mission_string_to_number(request.data.get('status_mission'))
    mars_station.save()
    mars_station_serializer = MarsStationSerializerDetail(mars_station).data

    return Response(mars_station_serializer, status=status.HTTP_200_OK)


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
        return Response(data={'message': f'Ошибка, аккаунт не является сотрудником(пользователем)'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        mars_station = MarsStation.objects.get(pk=pk)
    except MarsStation.DoesNotExist:
        return Response({'message': 'Марсианская станция не найдена'}, status=status.HTTP_404_NOT_FOUND)

    # Меняет на статус 'В работе'
    mars_station.status_task = 2
    mars_station.date_form = date.today()

    # Подключение к асинхронному веб-сервису
    const_token = 'my_secret_token'
    id_draft = mars_station.id
    # Асинхронный веб-сервис
    url = 'http://127.0.0.1:8100/api/async_calc/'
    data = {
        'id_draft': id_draft,
        'token': const_token
    }
    try:
        response = requests.post(url, json=data)

        if response.status_code == 200:
            mars_station.status_mission = 1
        else:
            mars_station.status_mission = 0

        mars_station.save()
    except Exception as error:
        print(error)

    return Response({'message': 'Успешно обновлен статус'}, status=status.HTTP_200_OK)


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
        return Response({'message': 'Марсианская станция не найдена'},
                        status=status.HTTP_404_NOT_FOUND)
    # Изначальный статус заявки должн быть 'В работе'
    if mars_station.status_task != 2:
        return Response({'message': 'Вы забыл(-а) отправить заявку, чтобы обновить статус как "В работе"'},
                        status=status.HTTP_400_BAD_REQUEST)

    mars_station.status_task = request.data['status_task']
    mars_station.id_moderator_id = id

    if request.data['status_task'] in [3, 4]:
        mars_station.date_close = date.today()
        mars_station.save()
        return Response({'message': 'Успешно обновлен статус'}, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'Вы можете обновить статус только с этими "Принята" или "Отменена"'})


# Удаляет марсианскую станцию по ID
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def DELETE_MarsStation(request, pk, format=None):
    print('[INFO] API DELETE [DELETE_MarsStation]')
    error_message, token = get_access_token(request)
    payload = get_jwt_payload(token)
    id = payload['id']

    user = Users.objects.get(id=id)
    if user.is_moderator:
        return Response(data={'message': f'Ошибка, аккаунт не является сотрудником'},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        mars_station = MarsStation.objects.get(pk=pk)
    except MarsStation.DoesNotExist:
        return Response({'message': 'Марсианская станция не найдена'},
                        status=status.HTTP_404_NOT_FOUND)

    mars_station = get_object_or_404(MarsStation, pk=pk)
    mars_station.status_task = 5
    mars_station.save()
    return Response({'message': 'Марсианская станция успешно удалена'},
                    status=status.HTTP_200_OK)


# ==================================================================================
# М-М
# ==================================================================================

# Обновляет информацию о марсианской станции по ID
@swagger_auto_schema(method='put', request_body=LocationSerializer)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def PUT_Location(request, pk_location, pk_mars_station, format=None):
    print('[INFO] API PUT [PUT_Location]')
    location = get_object_or_404(Location, pk=pk_location)
    direction = request.data['direction']

    # Получаем все объекты Location для данной марсианской станции
    locations = Location.objects.filter(id_mars_station=pk_mars_station).order_by('sequence_number')
    locations = list(locations)

    # Определяем индекс текущего объекта в списке
    current_index = locations.index(location)

    # Определяем новый индекс в зависимости от направления
    new_index = current_index - 1 if direction == 'up' else current_index + 1

    # Проверяем, не выходит ли новый индекс за границы списка
    if 0 <= new_index < len(locations):
        # Меняем значения sequence_number для текущего и нового объекта
        current_sequence_number = location.sequence_number
        new_sequence_number = locations[new_index].sequence_number

        location.sequence_number = new_sequence_number
        locations[new_index].sequence_number = current_sequence_number

        # Сохраняем объекты Location
        location.save()
        locations[new_index].save()

        # Получаем все объекты Location для данной марсианской станции
        locations = Location.objects.filter(id_mars_station=pk_mars_station)
        locations_serializer = LocationSerializer(locations, many=True)

        geographical_objects_data = []
        for location in locations:
            geographical_object = location.id_geographical_object
            geographical_object_serializer = GeographicalObjectSerializer(geographical_object)
            geographical_objects_data.append(geographical_object_serializer.data)

        return Response(data={'message': 'Местоположение успешно отредактировано',
                              'location': locations_serializer.data,
                              'geographical_object': geographical_objects_data},
                        status=status.HTTP_200_OK)
    else:
        return Response({'message': 'Недопустимый запрос на перемещение'}, status=status.HTTP_400_BAD_REQUEST)

# Удаляет марсианскую станцию по ID
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def DELETE_Location(request, pk_location, pk_mars_station, format=None):
    print('[INFO] API DELETE [DELETE_Location]')
    # Удаляем объект Location
    location = get_object_or_404(Location, pk=pk_location)
    # Удаляет объект Location
    location.delete()
    # Получаем все объекты Location для данной марсианской станции
    locations = Location.objects.filter(id_mars_station=pk_mars_station)
    locations_serializer = LocationSerializer(locations, many=True)

    geographical_objects_data = []
    for location in locations:
        geographical_object = location.id_geographical_object
        geographical_object_serializer = GeographicalObjectSerializer(geographical_object)
        geographical_objects_data.append(geographical_object_serializer.data)

    return Response(data={'message': 'Местоположение успешно удалено',
                          'location': locations_serializer.data,
                          'geographical_object': geographical_objects_data},
                    status=status.HTTP_200_OK)


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
    transport_serializer = TypeTransportSerializerID_TYPE(transport, many=True)

    return Response(transport_serializer.data, status=status.HTTP_200_OK)


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
        const_token = 'my_secret_token'

        if const_token != json_data['token']:
            return Response(data={'message': 'Ошибка, токен не соответствует'}, status=status.HTTP_403_FORBIDDEN)

        # Изменяем значение sequence_number
        try:
            # Выводит конкретную заявку создателя
            mars_station = get_object_or_404(MarsStation, pk=json_data['id_draft'])
            mars_station.status_mission = json_data['status_mission']
            # Сохраняем объект Location
            mars_station.save()
            data_json = {
                'id': mars_station.id,
                'status_task': mars_station.get_status_task_display_word(),
                'status_mission': mars_station.get_status_mission_display_word()
            }
            return Response(data={'message': 'Статус миссии успешно обновлен', 'data': data_json},
                            status=status.HTTP_200_OK)
        except ValueError:
            return Response({'message': 'Недопустимый формат преобразования'}, status=status.HTTP_400_BAD_REQUEST)
    except json.JSONDecodeError as e:
        print(f'Error decoding JSON: {e}')
        return Response(data={'message': 'Ошибка декодирования JSON'}, status=status.HTTP_400_BAD_REQUEST)
