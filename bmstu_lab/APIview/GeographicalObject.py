from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework import status, generics


# Для отображения на сайте в формате JSON
# from rest_framework.decorators import renderer_classes, permission_classes
# from rest_framework.renderers import JSONRenderer
# Пример разрешения
# from rest_framework.permissions import IsAuthenticatedOrReadOnly

from bmstu_lab.serializers import GeographicalObjectSerializer, TransportSerializer
from bmstu_lab.models import GeographicalObject

from bmstu_lab.database import Database
from django_filters.rest_framework import DjangoFilterBackend
from bmstu_lab.filters import GeographicalObjectFilter

@api_view(['GET'])
def get_geographical_objects(request):
    DB = Database()
    DB.connect()
    DB_geografical_object = GeographicalObject.objects.all()
    DB.close()
    return Response({'data': GeographicalObjectSerializer(DB_geografical_object, many=True).data})


@api_view(['GET'])
def get_objects_with_status(request):
    DB = Database()
    DB.connect()
    DB_geografical_object_with_status = DB.get_geografical_object_with_status_true()
    DB.close()
    return Response({'data': GeographicalObjectSerializer(DB_geografical_object_with_status, many=True).data})

@api_view(['GET'])
def get_geografical_object_and_transports_by_id(request, id):
    try:
        DB = Database()
        DB.connect()
        transports = DB.get_geografical_object_and_transports_by_id(id)
        DB.close()

        # Сериализиуем географический объект и транспорт, чтобы получить набор данных в формате JSON
        geo_serializer = GeographicalObjectSerializer(GeographicalObject.objects.get(id=id))
        transport_serializer = TransportSerializer(transports, many=True)

        response_data = {
            'GeograficObject': geo_serializer.data,
            'Transports': transport_serializer.instance,
        }

        return Response({'data': response_data})
    except GeographicalObject.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def filter_geographical_objects(request):
    filter_keyword = request.GET.get('filter_keyword')
    filter_field = request.GET.get('filter_field')

    if not filter_keyword or not filter_field:
        return Response(
            {"error": "Необходимо указать ключевое слово и поле для фильтрации"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Преобразовать ключевое слово в строку для поиска в базе данных
    filter_keyword = str(filter_keyword)

    # Получить список объектов из базы данных
    database = GeographicalObject.objects.all().values('id', 'feature', 'type', 'size', 'describe', 'url_photo', 'status')

    if filter_field == 'type':
        filtered_objects = [obj for obj in database if filter_keyword.lower() in obj['type'].lower()]
    elif filter_field == 'feature':
        filtered_objects = [obj for obj in database if filter_keyword.lower() in obj['feature'].lower()]
    elif filter_field == 'size':
        filtered_objects = [obj for obj in database if obj['size'] == int(filter_keyword)]
    elif filter_field == 'describe':
        filtered_objects = [obj for obj in database if filter_keyword.lower() in obj['describe'].lower()]
    else:
        return Response({"error": "Неподдерживаемое поле для фильтрации"}, status=status.HTTP_400_BAD_REQUEST)

    DB = Database()
    DB.connect()
    transports = DB.get_geografical_object_and_transports_by_id(int(filtered_objects[0]['id']))
    DB.close()

    # Сериализиуем географический объект и транспорт, чтобы получить набор данных в формате JSON
    transport_serializer = TransportSerializer(transports, many=True)

    response_data = {
        'GeograficObject': filtered_objects[0],
        'Transports': transport_serializer.instance,
    }

    return Response({'data': response_data})

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

class GeograficalObjectAPIView(APIView):
    def get(self, request):
        return get_geographical_objects(request)

    def get_object_with_status(self, request):
        return get_objects_with_status(request)

    def get_geografical_object_and_transports_by_id(self, request, id):
        return get_geografical_object_and_transports_by_id(request, id)

    def filter_geographical_objects(self, request):
        return filter_geographical_objects(request)

    def post(self, request):
        return create_geographical_object(request)