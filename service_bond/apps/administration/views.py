from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView


class IndexView(View):

    def get(self, request, *args, **kwargs):
        ctx = {}
        return redirect(reverse('ui-panel'))


class UiPanelView(View):
    def get(self, request, *args, **kwargs):
        hash = kwargs.get('hash') or ''
        url = '/static/vue/index.html'
        if hash:
            url += '#{}'.format(hash)
        qs = request.GET.urlencode()
        if qs:
            url += '?' + qs
        return redirect(url)


class LogoutView(View):

    def get(self, request, *args, **kwargs):
        auth_logout(request)
        next_url = request.headers.get('Referer') or 'bike:index'
        return redirect(next_url)


class PrivacyPolicyView(TemplateView):
    template_name = 'bike/privacy_policy.html'


class TermsOfServiceView(TemplateView):
    template_name = 'bike/terms_of_service.html'
