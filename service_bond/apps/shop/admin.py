import operator
from functools import reduce, update_wrapper

from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.urls import path, reverse_lazy
from django.utils.html import format_html
from django.views.generic import UpdateView
from django_multitenant.utils import get_current_tenant

from apps.administration.models import User, Shop, Customer
from django.utils.translation import gettext_lazy as _

from service_bond.helpers.utils import shopModelBackend, PermissionRequiredMixin


class shopAdminAuthenticationForm(AuthenticationForm):
    """
    A custom authentication form used in the admin app.
    """
    error_messages = {
        **AuthenticationForm.error_messages,
        'invalid_login': _(
            "Please enter the correct %(username)s and password for a shop "
            "account. Note that both fields may be case-sensitive."
        ),
    }
    required_css_class = 'required'

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.shop_id:
            raise forms.ValidationError(
                self.error_messages['invalid_login'],
                code='invalid_login',
                params={'username': self.username_field.verbose_name}
            )

class MyshopEditForm(forms.ModelForm):

    class Meta:
        model = Shop
        fields = '__all__'

    class Media:
        js = ('admin/js/jsoneditor.min.js', 'admin/js/utils.js',)


class MyshopEditView(PermissionRequiredMixin, UpdateView):
    permission_required = 'administration.change_my_shop'
    template_name = 'admin/edit_my_shop.html'
    form_class = MyshopEditForm
    success_url = reverse_lazy('admin:edit_my_shop')

    def form_valid(self, form):
        return super().form_valid(form)
    def get_object(self, queryset=None):
        current_shop = get_current_tenant()
        return current_shop


class shopAdminSite(admin.AdminSite):
    site_header = "Administration shop Admin"
    site_title = "Administration shop Admin Panel"
    index_title = "Administration shop Admin Panel"
    login_form = shopAdminAuthenticationForm

    def has_permission(self, request):
        current_shop = get_current_tenant()
        return request.user.is_active and current_shop and (request.user.shop_id == current_shop.id)

    def edit_my_shop(self, request, extra_context=None):
        """
        Handle the "change password" task -- both form display and validation.
        """
        defaults = {
            'extra_context': {**self.each_context(request), **(extra_context or {})},
        }
        request.current_app = self.name
        return MyshopEditView.as_view(**defaults)(request)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('edit-my-shop/', self.admin_view(self.edit_my_shop), name='edit_my_shop'),
        ]
        return urls + custom_urls


site = shopAdminSite(name='shop_admin')


class MyUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = User


    def save(self, commit=True):
        user = super().save(commit=False)
        current_shop = get_current_tenant()
        user.shop = current_shop
        if commit:
            user.save()
        return user


class MyUserChangeForm(UserChangeForm):
    user_permissions = forms.ModelMultipleChoiceField(queryset=Permission.objects.all(),
                                                      widget=FilteredSelectMultiple('Permissions', False),
                                                      required=False)

    class Meta(UserChangeForm.Meta):
        model = User

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user_permissions'].queryset = self._get_user_permissions_qs(
            self.fields['user_permissions'].queryset)

    def _get_user_permissions_qs(self, base_qs=None):
        qs = base_qs or Permission.objects
        queries = []
        for m, actions in shopModelBackend.PERMISSION_MODELS.items():
            app_label, model = m
            for a in actions:
                codename = '{}_{}'.format(a, model)
                queries.append(Q(content_type__app_label=app_label, content_type__model=model, codename=codename))
        qs = qs.filter(reduce(operator.or_, queries))
        return qs

    def clean_is_shop_admin(self):
        is_shop_admin = self.cleaned_data['is_shop_admin']
        if not is_shop_admin and self.instance.is_master_shop_admin:
            raise ValidationError('Cannot change is_shop_admin field of "Master shop Admin" user')


class MyUserAdmin(UserAdmin):
    form = MyUserChangeForm
    add_form = MyUserCreationForm
    list_select_related = ('shop',)
    readonly_fields = ('last_login', 'date_joined',)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_shop_admin_user', 'is_active')
    list_filter = ('is_active', 'is_shop_admin')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (None, {'fields': ('gender', 'avatar', 'birth_date', 'is_shop_admin')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('email', 'is_shop_admin',)}),
    )

    def is_shop_admin_user(self, obj):
        icon = "remove"
        color = "danger"
        title = "Not shop Admin"
        if obj.is_master_shop_admin:
            icon = "check"
            color = "success"
            title = "shop Admin (Master)"
        elif obj.is_shop_admin:
            icon = "ok"
            color = "success"
            title = "shop Admin"

        return format_html('<span class="glyphicon glyphicon-{} text-{}" title="{}"></span>'.format(icon, color, title))

    is_shop_admin_user.short_description = 'Is shop Admin?'
    is_shop_admin_user.allow_tags = True

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        current_shop = get_current_tenant()
        return qs.filter(shop=current_shop)


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'city', 'phone_number', 'zipcode')
    search_fields = ( 'first_name', 'last_name', 'city', 'phone_number', 'zipcode')
    # list_filter = ('model',)
    exclude = ('shop',)

    def save_formset(self, request, form, formset, change):
        for f in formset.forms:
            f.instance.upload_by = request.user
        super().save_formset(request, form, formset, change)


site.register(User, MyUserAdmin)
site.register(Customer, CustomerAdmin)
