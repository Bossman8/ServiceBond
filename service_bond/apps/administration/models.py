import os

import jsonfield as jsonfield
from cerberus import Validator
from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, _user_has_perm, UserManager
from django.core.exceptions import ValidationError
from django.core.files.storage import get_storage_class
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.functional import LazyObject
from django.utils.text import slugify
from django_multitenant.mixins import TenantManagerMixin, TenantModelMixin
from django_multitenant.models import TenantModel
from model_utils import FieldTracker
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models.sql import DeleteQuery

DeleteQuery.get_compiler._sign = 'skipped'  # TODO! this is only a trick for a bug in multitenant


def avatar_file_path_func(instance, filename):
    from service_bond.helpers.utils import get_random_upload_path
    return get_random_upload_path(os.path.join('uploads', 'user', 'avatar'), filename)


class PublicStorage(LazyObject):
    def _setup(self):
        self._wrapped = get_storage_class(settings.PUBLIC_FILE_STORAGE)()


public_storage = PublicStorage()


class TenantUserManager(TenantManagerMixin, UserManager):
    pass


# class User(TenantModelMixin, AbstractUser):
class User(AbstractUser):
    GENDER_MALE = 'm'
    GENDER_FEMALE = 'f'
    GENDER_OTHER = 'o'
    GENDER_UNKNOWN = 'u'
    GENDER_CHOICES = (
        (GENDER_MALE, 'Male'),
        (GENDER_FEMALE, 'Female'),
        (GENDER_OTHER, 'Other'),
        (GENDER_UNKNOWN, 'Unknown'),
    )
    tenant_id = 'shop_id'

    email = models.EmailField(null=True, unique=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default=GENDER_UNKNOWN)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(blank=True, null=True, upload_to=avatar_file_path_func)
    shop = models.ForeignKey("shop", on_delete=models.SET_NULL, null=True, blank=True, related_name="users")
    is_shop_admin = models.BooleanField(default=False)
    is_master_shop_admin = models.BooleanField(default=False)

    # objects = TenantUserManager()

    @property
    def is_shop_admin_user(self):
        return self.is_master_shop_admin or self.is_shop_admin

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.lower()
        else:
            self.email = None
        if self.username:
            self.username = self.username.lower()
        if self.is_master_shop_admin:
            self.is_shop_admin = True
        if not (self.shop_id or self.shop):
            self.is_shop_admin = False
            self.is_master_shop_admin = False
        if not self.is_shop_admin:
            self.is_shop_admin = False
        if not self.is_master_shop_admin:
            self.is_master_shop_admin = False
        super().save(*args, **kwargs)


class Shop(TenantModel):
    SOCIAL_CONTACTS_VALIDATOR = {
        'type': 'dict', 'schema': {
            'facebook': {'type': 'string', 'required': False},
            'twitter': {'type': 'string', 'required': False},
            'instagram': {'type': 'string', 'required': False},
            'pinterest': {'type': 'string', 'required': False},
        }
    }
    OPENING_HOURS_VALIDATOR = {
        'type': 'dict', 'schema': {
            'monday': {'type': 'string', 'required': False},
            'tuesday': {'type': 'string', 'required': False},
            'wednesday': {'type': 'string', 'required': False},
            'thursday': {'type': 'string', 'required': False},
            'friday': {'type': 'string', 'required': False},
            'saturday': {'type': 'string', 'required': False},
            'sunday': {'type': 'string', 'required': False},
        }
    }
    PREFERENCES_VALIDATOR = {
        'type': 'dict', 'schema': {
            'reserve_notification_emails': {'type': 'string', 'required': False},
        }
    }
    tenant_id = 'id'
    name = models.CharField(max_length=64, unique=True, editable=False)
    title = models.CharField(max_length=64)
    phone_number = PhoneNumberField(null=True, blank=True, unique=True)
    email = models.EmailField(null=True, blank=True, unique=True)
    location_lat = models.DecimalField(max_digits=9, decimal_places=7, null=True, blank=True)
    location_lon = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    street_address = models.CharField(max_length=256, blank=True, null=True)
    country = models.CharField(max_length=128, blank=True, null=True)
    city = models.CharField(max_length=128, blank=True, null=True)
    state = models.CharField(max_length=128, blank=True, null=True)
    zipcode = models.CharField(max_length=10, blank=True, null=True)
    social_contacts = jsonfield.JSONField(null=True, blank=True)
    opening_hours = jsonfield.JSONField(null=True, blank=True)
    preferences = jsonfield.JSONField(null=True, blank=True)

    all_objects = models.Manager()

    class Meta:
        permissions = (
            ('change_my_shop', 'Can change my shop'),
        )

    def save(self, *args, **kwargs):
        self.name = slugify(self.title)
        json_fields = [
            ('social_contacts', self.SOCIAL_CONTACTS_VALIDATOR),
            ('opening_hours', self.OPENING_HOURS_VALIDATOR),
            ('preferences', self.PREFERENCES_VALIDATOR),
        ]
        for field, validator in json_fields:
            v = Validator({field: validator}, purge_unknown=True)
            if not v.validate({field: getattr(self, field) or {}}):
                raise ValidationError({field: str(v.errors)})
            setattr(self, field, v.document[field])

        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Customer(TenantModel):
    tenant_id = 'shop_id'
    shop = models.ForeignKey(Shop, on_delete=models.PROTECT)
    first_name = models.CharField(max_length=256, blank=True, null=True)
    last_name = models.CharField(max_length=256, blank=True, null=True)
    street_address = models.CharField(max_length=256, blank=True, null=True)
    phone_number = PhoneNumberField(null=True, blank=True, unique=True)
    street_address = models.CharField(max_length=256, blank=True, null=True)
    city = models.CharField(max_length=128, blank=True, null=True)
    state = models.CharField(max_length=128, blank=True, null=True)
    zipcode = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return str(self.first_name +" "+ self.last_name)
# class shopCustomerMember(TenantModel):
#     tenant_id = 'shop_id'
#     customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='shop_customer_members')
#     shop = models.ForeignKey(shop, on_delete=models.CASCADE, related_name='shop_customer_members')
#     join_datetime = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = (("user", "shop"),)

#     def __str__(self):
#         return '{} - {}'.format(self.user, self.shop)


