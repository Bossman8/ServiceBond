# Generated by Django 3.1.4 on 2021-01-24 04:18

import apps.administration.models
from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager
import django.utils.timezone
import django_multitenant.mixins
import jsonfield.fields
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, unique=True)),
                ('gender', models.CharField(choices=[('m', 'Male'), ('f', 'Female'), ('o', 'Other'), ('u', 'Unknown')], default='u', max_length=1)),
                ('birth_date', models.DateField(blank=True, null=True)),
                ('avatar', models.ImageField(blank=True, null=True, upload_to=apps.administration.models.avatar_file_path_func)),
                ('is_shop_admin', models.BooleanField(default=False)),
                ('is_master_shop_admin', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='shop',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(editable=False, max_length=64, unique=True)),
                ('title', models.CharField(max_length=64)),
                ('phone_number', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None, unique=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True, unique=True)),
                ('location_lat', models.DecimalField(blank=True, decimal_places=7, max_digits=9, null=True)),
                ('location_lon', models.DecimalField(blank=True, decimal_places=7, max_digits=10, null=True)),
                ('street_address', models.CharField(blank=True, max_length=256, null=True)),
                ('country', models.CharField(blank=True, max_length=128, null=True)),
                ('city', models.CharField(blank=True, max_length=128, null=True)),
                ('state', models.CharField(blank=True, max_length=128, null=True)),
                ('zipcode', models.CharField(blank=True, max_length=10, null=True)),
                ('social_contacts', jsonfield.fields.JSONField(blank=True, null=True)),
                ('opening_hours', jsonfield.fields.JSONField(blank=True, null=True)),
                ('preferences', jsonfield.fields.JSONField(blank=True, null=True)),
            ],
            options={
                'permissions': (('change_my_shop', 'Can change my shop'),),
            },
            bases=(django_multitenant.mixins.TenantModelMixin, models.Model),
            managers=[
                ('all_objects', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None, unique=True)),
                ('street_address', models.CharField(blank=True, max_length=256, null=True)),
                ('country', models.CharField(blank=True, max_length=128, null=True)),
                ('city', models.CharField(blank=True, max_length=128, null=True)),
                ('state', models.CharField(blank=True, max_length=128, null=True)),
                ('zipcode', models.CharField(blank=True, max_length=10, null=True)),
                ('height', models.PositiveIntegerField(blank=True, null=True)),
                ('weight', models.PositiveIntegerField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='shop',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='users', to='administration.shop'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
        migrations.CreateModel(
            name='shopCustomerMember',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('join_datetime', models.DateTimeField(auto_now_add=True)),
                ('shop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shop_customer_members', to='administration.shop')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shop_customer_members', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'shop')},
            },
            bases=(django_multitenant.mixins.TenantModelMixin, models.Model),
        ),
    ]