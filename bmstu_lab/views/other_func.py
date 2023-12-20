from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status

from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny

from bmstu_lab.serializers import TypeTransportSerializerID_TYPE
from bmstu_lab.models import MarsStation, Transport

import json

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

# TODO: Добавить сериализацию для этой функции
@swagger_auto_schema(method='put')
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
