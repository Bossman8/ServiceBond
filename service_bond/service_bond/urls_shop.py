
from apps.administration.views import UiPanelView
from apps.shop import admin
from django.urls import path, include, re_path

from service_bond.urls import API_ENDPOINT

SUBPATH = 'shop/0'  # 0 is a trick. this will be replace with current shop dynamic in SubpathURLRoutingMiddleware

urlpatterns = [
    re_path('{}/admin/'.format(SUBPATH), admin.site.urls),
    re_path('{}/'.format(SUBPATH), include('apps.shop.urls', namespace='shop')),
    re_path('{}/{}/'.format(SUBPATH, API_ENDPOINT),
            include('apps.shop.rest_api.urls', namespace='shop_rest_api')),
    re_path(r'^ui-panel(?:(?P<hash>\S+))?$', UiPanelView.as_view(), name='ui-panel'),
]
