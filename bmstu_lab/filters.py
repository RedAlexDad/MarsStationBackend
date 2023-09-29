import django_filters
from bmstu_lab.models import GeographicalObject

class GeographicalObjectFilter(django_filters.FilterSet):
    # http://127.0.0.1:8000/api/geografic_objects/?feature=Amazonis&filter_field=feature
    feature = django_filters.CharFilter(field_name='feature', lookup_expr='icontains')
    type = django_filters.CharFilter(field_name='type', lookup_expr='icontains')
    size = django_filters.CharFilter(field_name='size', lookup_expr='icontains')
    describe = django_filters.CharFilter(field_name='describe', lookup_expr='icontains')

    class Meta:
        model = GeographicalObject
        fields = {
            'feature': ['icontains'],
            'type': ['icontains'],
            'size': ['icontains'],
            'describe': ['icontains'],
        }
