import django_filters
from django_filters import rest_framework as filters

from apps.administration.models import Shop


class shopFilter(filters.FilterSet):

    class Meta:
        model = Shop
        fields = '__all__'
