from django.urls import include, path
from rest_framework import routers

from apps.shop.rest_api.views import CustomerView

rest_router = routers.DefaultRouter()
rest_router.trailing_slash = "/?"  # added to support both / and slashless
rest_router.register(r'customer', CustomerView)
# rest_router.register(r'bike_reserve', BikeReserveView)

app_name = 'shop'

urlpatterns = [
    path('', include(rest_router.urls))
]
