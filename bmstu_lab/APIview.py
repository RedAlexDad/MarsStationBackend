from rest_framework.response import Response
from rest_framework.views import APIView

# Для отображения на сайте в формате JSON
# from rest_framework.decorators import renderer_classes, permission_classes
# from rest_framework.renderers import JSONRenderer
# Пример разрешения
# from rest_framework.permissions import IsAuthenticatedOrReadOnly

from bmstu_lab.serializers import UsersSerializer, StatusSerializer, EmployeeSerializer, LocationSerializer, TransportSerializer, GeographicalObjectSerializer, MarsStationSerializer
from bmstu_lab.models import GeographicalObject, Transport

class GeograficalObjectAPIView(APIView):
    def get(self, request):
        queryset = GeographicalObject.objects.all()
        return Response({'data': GeographicalObjectSerializer(queryset, many=True).data})

    def post(self, request):
        serializer = GeographicalObjectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        post_new = GeographicalObject.objects.create(
            feature=request.data['feature'],
            type=request.data['type'],
            size=request.data['size'] ,
            describe=request.data['describe'],
            url_photo=request.data['url_photo'],
            status=request.data['status'],
        )

        return Response({'post': GeographicalObjectSerializer(post_new).data})