import functools
import logging
import os
import re
import sys
import traceback
import types
import uuid
import datetime
from importlib import import_module

import simplejson as json
from django.conf import settings

from django.db import connection
from django.urls import set_urlconf
from django_multitenant.utils import set_current_tenant, unset_current_tenant
from reversion.middleware import RevisionMiddleware

print = functools.partial(print, flush=True)


class DisableCSRFMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if getattr(settings, 'CSRF_DISABLED', False):
            setattr(request, '_dont_enforce_csrf_checks', True)

        response = self.get_response(request)
        return response


class InjectUiVersionInHeadersMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def _get_ui_version(self):
        ui_packages_path = os.path.join(settings.BASE_DIR, 'FRONTEND', 'service_bond_ui', 'package.json')
        if not os.path.exists(ui_packages_path):
            return
        version = None
        try:
            with open(ui_packages_path) as f:
                data = json.load(f)
            version = data.get('version')
        except Exception:
            traceback.print_exc()
        return version

    def __call__(self, request):
        response = self.get_response(request)
        ui_version = self._get_ui_version()
        if ui_version:
            response['X-UI-Version'] = ui_version
        else:
            print('Cannot discover UI version!')
        return response


class SqlQueryLogging:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        from sys import stdout
        if stdout.isatty():
            for query in connection.queries:
                print("\033[1;31m[%s]\033[0m \033[1m%s\033[0m" % (query['time'], " ".join(query['sql'].split())))
        return response


class RequestTimeLoggingMiddleware(object):
    """Middleware class logging request time to stderr.

    This class can be used to measure time of request processing
    within Django.  It can be also used to log time spent in
    middleware and in view itself, by putting middleware multiple
    times in INSTALLED_MIDDLEWARE.

    Static method `log_message' may be used independently of the
    middleware itself, outside of it, and even when middleware is not
    listed in INSTALLED_MIDDLEWARE.
    """

    @staticmethod
    def log_message(request, tag, message=''):
        """Log timing message to stderr.

        Logs message about `request' with a `tag' (a string, 10
        characters or less if possible), timing info and optional
        `message'.

        Log format is "timestamp tag uuid count path +delta message"
        - timestamp is microsecond timestamp of message
        - tag is the `tag' parameter
        - uuid is the UUID identifying request
        - count is number of logged message for this request
        - path is request.path
        - delta is timedelta between first logged message
          for this request and current message
        - message is the `message' parameter.
        """

        dt = datetime.datetime.utcnow()
        if not hasattr(request, '_logging_uuid'):
            request._logging_uuid = uuid.uuid1()
            request._logging_start_dt = dt
            request._logging_pass = 0

        request._logging_pass += 1
        print(
            u'%s %-10s %s %2d %s +%s %s' % (
                dt.isoformat(),
                tag,
                request._logging_uuid,
                request._logging_pass,
                request.path,
                dt - request._logging_start_dt,
                message,
            ), file=sys.stderr)

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.DEBUG:
            self.log_message(request, 'request ')
        response = self.get_response(request)
        if settings.DEBUG:
            s = getattr(response, 'status_code', 0)
            r = str(s)
            if s in (300, 301, 302, 307):
                r += ' => %s' % response.get('Location', '?')
            elif getattr(response, 'content', None):
                r += ' (%db)' % len(response.content)
            self.log_message(request, 'response', r)
        return response


class CustomRevisionMiddleware(RevisionMiddleware):
    atomic = False


logger = logging.getLogger(__name__)


class SubpathURLRoutingMiddleware(object):
    """
    A middleware class that adds a ``subpath`` attribute to the current request.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.set_subpath(request)
        response = self.get_response(request)
        return response

    @staticmethod
    def _load_shop_urlconf(url_conf, shop_id, request):
        from service_bond.urls_shop import urlpatterns
        from apps.administration.models import Shop
        try:
            Shop = Shop.all_objects.get(id=shop_id)
        except (Shop.DoesNotExist, ValueError, TypeError):
            shop = None
        urlconf_module = None
        if Shop:
            urlconf_module = types.ModuleType('{}{}'.format(url_conf, Shop.id))
            urlconf_module.urlpatterns = []
            for p in urlpatterns:
                p.pattern._regex = re.sub('^shop/\d+', 'shop/{}'.format(Shop.id), p.pattern._regex)
                p.pattern.regex = re.compile(p.pattern._regex)
                urlconf_module.urlpatterns.append(p)

        request.Shop = Shop
        set_current_tenant(request.Shop)
        return urlconf_module

    def set_subpath(self, request):
        """
        Adds a ``subpath`` attribute to the ``request`` parameter.
        """
        splitted_path = request.path_info.lstrip('/').split('/', 1)
        subpath = splitted_path[0]
        if subpath and subpath in settings.SUBPATH_URLCONFS:
            request.subpath = subpath
        else:
            request.subpath = None

        urlconf = settings.SUBPATH_URLCONFS.get(request.subpath)
        if subpath == 'shop':
            shop_id = splitted_path[1].split('/', 1)[0]
            urlconf = self._load_shop_urlconf(urlconf, shop_id, request)
        else:
            unset_current_tenant()

        if urlconf is not None:
            logger.debug("Using urlconf %s for subpath: %s", repr(urlconf), repr(request.subpath))
        request.urlconf = urlconf
