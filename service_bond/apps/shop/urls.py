from django.urls import re_path

from .views import IndexView

app_name = 'shop'

urlpatterns = [
    re_path(r'^$', IndexView.as_view(), name='index'),
]
