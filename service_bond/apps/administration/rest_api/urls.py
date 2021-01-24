from django.urls import include, path
from rest_framework import routers

from apps.administration.rest_api.views import SessionView, ProfileView, GlobalConfView, shopView, SitePreferencesViewSet

rest_router = routers.DefaultRouter()
rest_router.trailing_slash = "/?"  # added to support both / and slashless
rest_router.register(r'session', SessionView, basename='session')
rest_router.register(r'me', ProfileView, basename='profile')
rest_router.register(r'shop', shopView)
rest_router.register(r'global_conf', GlobalConfView, basename='global_conf')
rest_router.register(r'site_pref', SitePreferencesViewSet, basename='site_pref')

app_name = 'bike'

urlpatterns = [
    path('', include(rest_router.urls))
]
