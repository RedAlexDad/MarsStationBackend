from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.http import Http404
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema

from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from bmstu_lab.permissions import IsModerator, IsAuthenticated, get_jwt_payload, get_access_token
from bmstu_lab.serializers import GeographicalObjectSerializer, MarsStationSerializer, LocationSerializer, \
    TransportSerializer, EmployeeSerializer, MarsStationSerializerDetail
from bmstu_lab.models import GeographicalObject, MarsStation, Location, Transport, Employee, Users

from datetime import date

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
        'status_task': mars_station.status_task,
        'status_mission': mars_station.status_mission,
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
                return Response({'message': 'Ошибка! Невозможно выполнить сортировку, когда "ДО" превышает "ПОСЛЕ"'},
                                status=status.HTTP_400_BAD_REQUEST)
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
            return Response({'message': error}, status=status.HTTP_404_NOT_FOUND)


# Обновляет информацию о марсианской станции по ID
@swagger_auto_schema(method='put', request_body=MarsStationSerializer)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def PUT_MarsStation(request, pk, format=None):
    print('[INFO] API PUT [PUT_MarsStation]')
    try:
        mars_station = MarsStation.objects.get(pk=pk)
    except MarsStation.DoesNotExist:
        return Response({'message': 'Марсианская станция не найдена'},
                        status=status.HTTP_404_NOT_FOUND)

    serializer = MarsStationSerializer(instance=mars_station, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(data={'message': 'Марсианская станция успешно обновлено', 'data': serializer.data},
                        status=status.HTTP_200_OK)
    else:
        print(serializer.errors)
        return Response(data={'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


# Обновляет информацию о марсианской станции по ID создателя
@swagger_auto_schema(method='put', request_body=MarsStationSerializer)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def PUT_MarsStation_BY_USER(request, pk, format=None):
    print('[INFO] API PUT [PUT_MarsStation_BY_USER]')
    try:
        mars_station = MarsStation.objects.get(pk=pk)
    except MarsStation.DoesNotExist:
        return Response({'message': 'Марсианская станция не найдена'}, status=status.HTTP_404_NOT_FOUND)

    if mars_station.status_task in [2, 3, 4]:
        return Response({'message': 'Вы можете обновить статус только тогда, когда заявка черновая'},
                        status=status.HTTP_405_METHOD_NOT_ALLOWED)

    error_message, token = get_access_token(request)
    payload = get_jwt_payload(token)
    mars_station.id_employee_id = payload['id']

    # Меняет на статус 'В работе'
    mars_station.status_task = 2
    mars_station.date_form = date.today()
    mars_station.save()
    return Response({'message': 'Успешно обновлен статус'}, status=status.HTTP_200_OK)


# Обновляет информацию о марсианской станции по ID модератора
@swagger_auto_schema(method='put', request_body=MarsStationSerializer)
@api_view(['PUT'])
@permission_classes([IsModerator])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def PUT_MarsStation_BY_ADMIN(request, pk, format=None):
    print('[INFO] API PUT [PUT_MarsStation_BY_ADMIN]')
    try:
        mars_station = MarsStation.objects.get(pk=pk)
    except MarsStation.DoesNotExist:
        return Response({'message': 'Марсианская станция не найдена'},
                        status=status.HTTP_404_NOT_FOUND)
    # Изначальный статус заявки должн быть 'В работе'
    if mars_station.status_task != 2:
        return Response({'message': 'Вы забыл(-а) отправить заявку, чтобы обновить статус как "В работе"'},
                        status=status.HTTP_400_BAD_REQUEST)

    if request.data['status_task'] in [3, 4]:
        error_message, token = get_access_token(request)
        payload = get_jwt_payload(token)
        mars_station.id_moderator_id = payload['id']

        mars_station.status_task = request.data['status_task']
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

    mars_station.status_task = 5
    mars_station.save()
    return Response({'message': 'Марсианская станция успешно удалена'},
                    status=status.HTTP_200_OK)