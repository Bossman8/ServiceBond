from django.db import models
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
# Create your models here.


class Customer(models.Model):
    phone_number = PhoneNumberField(null=True, blank=True, unique=True)
    street_address = models.CharField(max_length=256, blank=True, null=True)
    country = models.CharField(max_length=128, blank=True, null=True)
    city = models.CharField(max_length=128, blank=True, null=True)
    state = models.CharField(max_length=128, blank=True, null=True)
    zipcode = models.CharField(max_length=10, blank=True, null=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    weight = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return str(self.user)