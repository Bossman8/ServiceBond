from django.shortcuts import redirect
from django.urls import reverse
from django.views import View


class IndexView(View):
    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def get(self, request, *args, **kwargs):
        ctx = {}
        # return render(request, 'shop/index.html', ctx)
        # return redirect(reverse('admin:index'))
        url_hash = "/shop/{}/".format(request.shop.pk)
        return redirect(reverse('ui-panel', kwargs={'hash': url_hash}))
