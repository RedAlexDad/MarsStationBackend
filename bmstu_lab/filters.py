import django_filters
from bmstu_lab.models import GeographicalObject

class GeographicalObjectFilter(django_filters.FilterSet):
    feature = django_filters.CharFilter(field_name='feature', lookup_expr='icontains')

    class Meta:
        model = GeographicalObject
        fields = {
            'feature': ['icontains'],
        }
