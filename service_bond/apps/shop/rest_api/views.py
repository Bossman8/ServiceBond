from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Count
from django.template.loader import render_to_string
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.administration.models import Customer
from apps.shop.rest_api.filters import CustomerFilter
from apps.shop.rest_api.serializers import CustomerSerializer
from service_bond.helpers.utils import CustomLoggingMixin as LoggingMixin, IsOwnerPermission, shopCustomerPermission, \
    CreateListMixin


class CustomerView(LoggingMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Customer.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = CustomerSerializer
    filterset_class = CustomerFilter
    ordering = 'id'
    ordering_fields = '__all__'
    search_fields = '__all__'

    def get_queryset(self):
        # Notice!!! dont call super().get_queryset().
        # because this call that return not expected objects because of current tenant
        return Customer.objects.all()

    # def get_queryset(self):
    #     # Notice!!! dont call super().get_queryset().
    #     # because this call that return not expected objects because of current tenant
    #     return Bike.objects.all().select_related('model', 'model__brand').prefetch_related('photos')

    # @action(detail=False, methods=['GET',], serializer_class=ReserveListOfBikeSerializer)
    # def summary(self, request, *args, **kwargs):
    #     styles_qs = Bike.objects.values('model__style').annotate(count=Count('id'))
    #     styles_count = {r['model__style']: r['count'] for r in styles_qs}
    #     styles = [
    #         dict(name=s[0], title=s[1], count=styles_count.get(s[0], 0)) for s in Model.STYLE_CHOICES
    #     ]
    #     brands_qs =Bike.objects.values('model__brand').annotate(count=Count('id'))
    #     brands_count = {r['model__brand']: r['count'] for r in brands_qs}
    #     brands = [
    #         dict(id=b.id, name=b.name, count=brands_count.get(b.id, 0)) for b in Brand.objects.order_by('name')
    #     ]
    #     summary = {
    #         'styles': styles,
    #         'brands': brands
    #     }
    #     return Response(summary)

    # @action(detail=True, methods=['GET',], serializer_class=ReserveListOfBikeSerializer)
    # def reserve_list(self, request, *args, **kwargs):
    #     bike = self.get_object()
    #     reserve_list = bike.bike_reserve.order_by('-date').all()
    #     reserve_list = BikeReserveFilter(data=request.GET, queryset=reserve_list).qs
    #     reserve_list = self.paginate_queryset(reserve_list)
    #     serializer = self.get_serializer(reserve_list, many=True)
    #     results = serializer.data
    #     return self.get_paginated_response(results)


# class BikeReserveView(CreateListMixin, viewsets.ModelViewSet):
#     owner_permission_field = 'reserved_by'
#     queryset = BikeReserve.objects.all()
#     # TODO: finally we should use shopCustomerPermission to check a customer is a verified member of a shop or not
#     # permission_classes = (shopCustomerPermission, IsOwnerPermission,)
#     permission_classes = (IsAuthenticated, IsOwnerPermission,)
#     serializer_class = BikeReserveSerializer
#     filterset_class = BikeReserveFilter
#     ordering = ('date', 'bike')
#     ordering_fields = '__all__'
#     search_fields = ['bike__model__name', 'bike__model__brand__name']

#     def get_queryset(self):
#         # Notice!!! dont call super().get_queryset().
#         # because this call that return not expected objects because of current tenant
#         qs = BikeReserve.objects.all().filter(reserved_by=self.request.user.id)
#         return qs.select_related('bike__model', 'bike__model__brand')

#     def send_user_reservation_email(self, bike, reserved_by, dates):
#         context = {'bike': bike, 'reserved_by': reserved_by, 'dates': dates, 'request': self.request}
#         template_name = 'bike/email/bike_reservation_email.html'
#         message = render_to_string(template_name, context)
#         subject = 'Bike Reserve Notification'
#         email = reserved_by.email
#         if email:
#             send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email],
#                       html_message=message, fail_silently=False)

#     def send_shop_reservation_email(self, bike, reserved_by, dates):
#         context = {'bike': bike, 'reserved_by': reserved_by, 'dates': dates, 'request': self.request}
#         template_name = 'shop/email/bike_reservation_email.html'
#         message = render_to_string(template_name, context)
#         subject = 'Bike Reserve Notification'
#         shop = bike.shop
#         emails = shop.preferences.get('reserve_notification_emails') or ''
#         emails = [e.strip() for e in emails.split(',') if e.strip()]
#         if emails:
#             send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, emails,
#                       html_message=message, fail_silently=False)

#     def perform_create(self, serializer):
#         super().perform_create(serializer)
#         bike_reserves = serializer.instance
#         if not isinstance(bike_reserves, list):
#             bike_reserves = [bike_reserves]
#         bike = bike_reserves[0].bike
#         reserved_by = bike_reserves[0].reserved_by
#         dates = [r.date for r in bike_reserves]
#         self.send_user_reservation_email(bike, reserved_by, dates)
#         self.send_shop_reservation_email(bike, reserved_by, dates)
