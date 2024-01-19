from rest_framework.response import Response
from rest_framework import status

from rest_framework.decorators import api_view

from bmstu_lab.serializers import TypeTransportSerializerID_TYPE
from bmstu_lab.models import Transport

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
    transport_serializer = TypeTransportSerializerID_TYPE(transport, many=True)

    return Response(transport_serializer.data, status=status.HTTP_200_OK)
