from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.forms import PasswordInput
from django.template.defaultfilters import truncatewords
from django.utils.html import format_html, strip_tags
from django.utils.safestring import mark_safe
from dynamic_preferences.admin import GlobalPreferenceAdmin
from dynamic_preferences.models import GlobalPreferenceModel

from .models import Shop, User, Customer


class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User


class MyUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'shop',
                    'is_shop_admin_user', 'is_active')
    list_filter = UserAdmin.list_filter + ('is_shop_admin', 'shop')
    form = MyUserChangeForm
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('gender', 'avatar', 'birth_date', 'shop', 'is_shop_admin', 'is_master_shop_admin')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('email', 'shop', 'is_master_shop_admin')}),
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


class MastershopAdminUserInline(admin.TabularInline):
    model = User
    # max_num = 1
    extra = 1
    verbose_name = "Master Admin User"
    verbose_name_plural = "Master Admin Users"
    fields = ('username', 'password', 'email')

    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_master_shop_admin=True)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)
        field.help_text = None
        field.widget.attrs['placeholder'] = db_field.name.capitalize()
        if db_field.name == 'password':
            field.widget = PasswordInput(attrs={'placeholder': 'Passowrd(Leave blank for unchanged)'})
            field.required = False

        return field


class shopAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'title', 'phone_number', 'email', 'city')
    exclude = ('preferences', 'opening_hours', 'social_contacts')
    inlines = [MastershopAdminUserInline]

    def save_formset(self, request, form, formset, change):
        if formset.model != User:
            return super().save_formset(request, form, formset, change)

        instances = formset.save(commit=False)
        for instance in instances:
            instance.is_master_shop_admin = True
            if instance.id and not instance.password:
                del instance.password
            else:
                instance.set_password(instance.password)
            instance.save()
        formset.save_m2m()


class MyGlobalPreferenceAdmin(GlobalPreferenceAdmin):
    list_display = ('verbose_name', 'name', 'section_name', 'ellipsis_raw_value')

    def has_add_permission(self, request, obj=None):
        return False

    def ellipsis_raw_value(self, obj):
        return truncatewords(mark_safe(strip_tags(obj.raw_value or '')), 20)
    ellipsis_raw_value.short_description = "Raw Value"


admin.site.register(User, MyUserAdmin)
admin.site.register(Customer)
admin.site.register(Shop, shopAdmin)
admin.site.unregister(GlobalPreferenceModel)
admin.site.register(GlobalPreferenceModel, MyGlobalPreferenceAdmin)
