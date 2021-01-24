import django_filters
from django_filters import rest_framework as filters

from apps.administration.models import Customer


class CustomerFilter(filters.FilterSet):


    class Meta:
        model = Customer
        exclude = ['shop']