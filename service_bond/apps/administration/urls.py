from django.urls import re_path, path

from .views import (IndexView, LogoutView, PrivacyPolicyView, TermsOfServiceView)

app_name = 'administration'

urlpatterns = [
    re_path(r'^$', IndexView.as_view(), name='index'),
    path('privacy-policy', PrivacyPolicyView.as_view(), name='privacy-policy'),
    path('terms-of-service', TermsOfServiceView.as_view(), name='terms-of-service'),
    re_path(r'^logout/$', LogoutView.as_view(), name="logout"),
]
