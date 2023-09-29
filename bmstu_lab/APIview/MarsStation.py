from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view

# Для отображения на сайте в формате JSON
# from rest_framework.decorators import renderer_classes, permission_classes
# from rest_framework.renderers import JSONRenderer
# Пример разрешения
# from rest_framework.permissions import IsAuthenticatedOrReadOnly

from bmstu_lab.serializers import UsersSerializer, StatusSerializer, EmployeeSerializer, LocationSerializer, TransportSerializer, GeographicalObjectSerializer, MarsStationSerializer
from bmstu_lab.models import Users, Status, Employee, Location, Transport, GeographicalObject, MarsStation

from bmstu_lab.database import Database

@api_view(['GET'])
def get_geographical_objects(request):
    DB = Database()
    DB.connect()
    DB_transports = GeographicalObject.objects.all()
    DB.close()
    return Response({'data': GeographicalObjectSerializer(DB_transports, many=True).data})

@api_view(['POST'])
def create_geographical_object(request):
    serializer = GeographicalObjectSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    post_new = GeographicalObject.objects.create(
        feature=request.data['feature'],
        type=request.data['type'],
        size=request.data['size'],
        describe=request.data['describe'],
        url_photo=request.data['url_photo'],
        status=request.data['status'],
    )

    return Response({'post': GeographicalObjectSerializer(post_new).data})

@api_view(['GET'])
def get_objects_with_status(request):
    DB = Database()
    DB.connect()
    DB_transports = DB.get_geografical_object_with_status_true()
    DB.close()
    return Response({'data': GeographicalObjectSerializer(DB_transports, many=True).data})

class GeograficalObjectAPIView(APIView):
    def get(self, request):
        return get_geographical_objects(request)

    def post(self, request):
        return create_geographical_object(request)

    def get_object_with_status(self, request):
        return get_objects_with_status(request)