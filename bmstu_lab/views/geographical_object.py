from django.http import HttpResponse
from rest_framework.response import Response
from django.db.models import Max
from django.shortcuts import get_object_or_404
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema

from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from bmstu_lab.permissions import IsModerator, IsAuthenticated, get_jwt_payload, get_access_token

from bmstu_lab.serializers import GeographicalObjectSerializer, LocationSerializer
from bmstu_lab.models import GeographicalObject, MarsStation, Location, Employee, Users
from bmstu_lab.DB_Minio import DB_Minio

from datetime import date
# Время прогрузки, получение данных, запросов, изображение
import tempfile, requests, io
# Изображение
from PIL import Image
# Возвращает список географические объекты
from rest_framework.pagination import PageNumberPagination


# ==================================================================================
# УСЛУГА
# ==================================================================================
@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def GET_GeographicalObjects(request, format=None):
    print('[INFO] API GET [GET_GeographicalObject_PAGINATIONS]')

    # Получим параметры запроса из URL
    feature = request.GET.get('feature')
    type = request.GET.get('type')
    size = request.GET.get('size')
    describe = request.GET.get('describe')
    status = request.GET.get('status')
    # кол-во услуг на странице
    count_item = request.GET.get('count_item', 5)

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
        # print(error)
        pass

    # Пагинации
    paginator = PageNumberPagination()
    # Количество элементов на странице
    paginator.page_size = count_item
    # Параметр запроса для изменения количества элементов на странице
    paginator.page_size_query_param = 'page_size'
    # Максимальное количество элементов на странице
    paginator.max_page_size = count_item

    result_page = paginator.paginate_queryset(geographical_object, request)
    geographical_object_serializer = GeographicalObjectSerializer(result_page, many=True)

    response_data = {
        'count': paginator.page.paginator.count,
        'id_draft_service': id_draft_service,
        'count_geographical_object_by_draft': Location.objects.filter(id_mars_station=id_draft_service).count(),
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


@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def GET_GeograficObject_IMAGE(request, pk):
    if not GeographicalObject.objects.filter(pk=pk).exists():
        return Response(data={'message': f'Не существует географический объект с {pk}'},
                        status=status.HTTP_404_NOT_FOUND)

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
        return HttpResponse(date={'message': f'Ошибка при обработке объекта\n{error}'},
                            status=status.HTTP_400_BAD_REQUEST)


# TODO: Добавить возможность выбора изображение или вообще не реализовать это
@swagger_auto_schema(method='put')
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
                if photo:
                    return HttpResponse(photo, content_type='image/jpeg')
                else:
                    return Response(data={'message': 'Изображение пусто'}, status=status.HTTP_404_NOT_FOUND)
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
    try:
        geographical_object = GeographicalObject.objects.get(pk=pk)
    except GeographicalObject.DoesNotExist:
        return Response(f'Географический объект по {pk} не существует', status=status.HTTP_404_NOT_FOUND)

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

    return Response(data={'message': f'Успешно создана заявка'}, status=status.HTTP_201_CREATED)
