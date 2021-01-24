import jsonfield
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers
from django.contrib.auth.models import Group, Permission
from django.core import exceptions as django_exceptions

from apps.administration.models import User, Shop, Customer
from service_bond.helpers.utils import DynamicFieldsSerializerMixin, Base64ImageField

serializers.ModelSerializer.serializer_field_mapping[jsonfield.JSONField] = serializers.JSONField


class SessionSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30)
    password = serializers.CharField(max_length=128, style={'input_type': 'password'})
    remember = serializers.BooleanField(initial=False, required=False)


class PermissionSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ('id', 'name', 'codename')


class SetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(style={'input_type': 'password'})
    current_password = serializers.CharField(style={'input_type': 'password'})

    default_error_messages = {
        'invalid_password': 'Invalid Password',
    }

    def validate_current_password(self, value):
        is_password_valid = self.context['request'].user.check_password(value)
        if is_password_valid:
            return value
        else:
            self.fail('invalid_password')

    def validate_new_password(self, new_password):
        try:
            validate_password(new_password, self.context['request'].user)
        except django_exceptions.ValidationError as e:
            raise serializers.ValidationError({'new_password': list(e.messages)})
        return new_password


class NestedGroupSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(read_only=True, many=True)

    class Meta:
        model = Group
        fields = ('id', 'name', 'permissions')


class NestedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name')


class UserSessionSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    user_permissions = PermissionSerializer(read_only=True, many=True)
    groups = NestedGroupSerializer(read_only=True, many=True)

    class Meta:
        model = User
        exclude = ('password',)


class CustomerProfileSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'
        read_only_fields = ('user',)


class UserProfileSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    avatar = Base64ImageField(required=False, allow_null=True)
    customer = CustomerProfileSerializer(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'gender', 'birth_date', 'avatar', 'shop',
                  'is_shop_admin', 'is_master_shop_admin', 'customer')
        read_only_fields = ('email', 'username', 'is_shop_admin', 'is_master_shop_admin', 'shop')

    @transaction.atomic()
    def update(self, instance, validated_data):
        customer_data = validated_data.pop('customer', {})
        if customer_data:
            try:
                customer_object = instance.customer
            except Customer.DoesNotExist:
                customer_object = None
            if not customer_object:
                customer_object = Customer(user=instance)
            for k, v in customer_data.items():
                setattr(customer_object, k, v)
            customer_object.save()

        return super(UserProfileSerializer, self).update(instance, validated_data)

    def to_representation(self, instance):
        res = super(UserProfileSerializer, self).to_representation(instance)
        if not res.get('customer'):
            res['customer'] = {}
        return res


class shopSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):

    class Meta:
        model = Shop
        fields = '__all__'
