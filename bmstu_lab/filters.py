import django_filters
from .models import GeographicalObject

class GeographicalObjectFilter(django_filters.FilterSet):
    class Meta:
        model = GeographicalObject
        fields = ['type', 'feature', 'size', 'describe']
