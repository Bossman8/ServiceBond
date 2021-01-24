import jsonfield
from rest_framework import serializers

from apps.administration.models import Customer
from service_bond.helpers.utils import DynamicFieldsSerializerMixin

serializers.ModelSerializer.serializer_field_mapping[jsonfield.JSONField] = serializers.JSONField


class CustomerSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = ('id', 'first_name', 'last_name', 'street_address', 'phone_number', 'city', 'state', 'zipcode' )