from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from bmstu_lab.permissions import IsAuthenticated
from bmstu_lab.serializers import GeographicalObjectSerializer, LocationSerializer
from bmstu_lab.models import Location

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

