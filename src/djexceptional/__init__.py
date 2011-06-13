from cStringIO import StringIO

import datetime
import gzip
import logging
import os
import sys
import traceback
import urllib
import urllib2

from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed, ImproperlyConfigured
from django.core.urlresolvers import resolve

from djexceptional.utils import memoize, json_dumps, meta_to_http


__version__ = '0.1.0'

EXCEPTIONAL_PROTOCOL_VERSION = 6
EXCEPTIONAL_API_ENDPOINT = "http://api.getexceptional.com/api/errors"


class ExceptionalMiddleware(object):

    """
    Middleware to interface with the Exceptional service.

    Requires very little intervention on behalf of the user; you just need to
    add `EXCEPTIONAL_API_KEY` to your Django settings.
    """

    def __init__(self):
        if settings.DEBUG:
            raise MiddlewareNotUsed

        try:
            self.api_key = settings.EXCEPTIONAL_API_KEY
        except AttributeError:
            raise ImproperlyConfigured("You need to add an EXCEPTIONAL_API_KEY setting.")

        self.api_endpoint = EXCEPTIONAL_API_ENDPOINT + "?" + urllib.urlencode({
            "api_key": self.api_key,
            "protocol_version": EXCEPTIONAL_PROTOCOL_VERSION
            })

    def process_exception(self, request, exc):
        info = {}
        info.update(self.environment_info())
        info.update(self.request_info(request))
        info.update(self.exception_info(exc, sys.exc_info()[2]))

        payload = self.compress(json_dumps(info))
        req = urllib2.Request(self.api_endpoint, data=payload)
        req.headers['Content-Encoding'] = 'gzip'
        req.headers['Content-Type'] = 'application/json'

        try:
            conn = urllib2.urlopen(req)
            try:
                conn.read()
            finally:
                conn.close()
        except Exception:
            logging.exception("Exception occurred while communicating with GetExceptional")

    @staticmethod
    def compress(bytes):
        """Compress a bytestring using gzip."""

        stream = StringIO()
        # Use `compresslevel=1`; it's the least compressive but it's fast.
        gzstream = gzip.GzipFile(fileobj=stream, compresslevel=1, mode='wb')
        try:
            try:
                gzstream.write(bytes)
            finally:
                gzstream.close()
            return stream.getvalue()
        finally:
            stream.close()

    @memoize
    def environment_info(self):

        """
        Return a dictionary representing the server environment.

        The idea is that the result of this function will rarely (if ever)
        change for a given app instance. Ergo, the result can be cached between
        requests.
        """

        return {
                "application_environment": {
                    "framework": "django",
                    "env": dict(os.environ),
                    "language": "python",
                    "language_version": sys.version.replace('\n', ''),
                    "application_root_directory": self.project_root()
                    },
                "client": {
                    "name": "django-exceptional",
                    "version": __version__,
                    "protocol_version": EXCEPTIONAL_PROTOCOL_VERSION
                    }
                }

    def request_info(self, request):

        """
        Return a dictionary of information for a given request.

        This will be run once for every request.
        """

        # We have to re-resolve the request path here, because the information
        # is not stored on the request.
        view, args, kwargs = resolve(request.path)
        for i, arg in enumerate(args):
            kwargs[i] = arg

        parameters = {}
        parameters.update(kwargs)
        parameters.update(request.POST.items())
        parameters = self.filter_params(parameters)

        return {
                "request": {
                    "session": dict(request.session),
                    "remote_ip": request.META["REMOTE_ADDR"],
                    "parameters": parameters,
                    "action": view.__name__,
                    "controller": view.__module__,
                    "url": request.build_absolute_uri(),
                    "request_method": request.method,
                    "headers": meta_to_http(request.META)
                    }
                }

    def exception_info(self, exception, tb, timestamp=None):
        backtrace = []
        for tb_part in traceback.format_tb(tb):
            backtrace.extend(tb_part.rstrip().splitlines())

        if timestamp is None:
            timestamp = datetime.datetime.utcnow()

        return {
                "exception": {
                    "occurred_at": timestamp.isoformat(),
                    "message": str(exception),
                    "backtrace": backtrace,
                    "exception_class": self.exception_class(exception)
                    }
                }

    def exception_class(self, exception):
        """Return a name representing the class of an exception."""

        cls = type(exception)
        if cls.__module__ == 'exceptions':  # Built-in exception.
            return cls.__name__
        return "%s.%s" % (cls.__module__, cls.__name__)

    @memoize
    def project_root(self):

        """
        Return the root of the current Django project on the filesystem.

        Looks for `settings.PROJECT_ROOT`; failing that, uses the directory
        containing the current settings file.
        """

        if hasattr(settings, 'PROJECT_ROOT'):
            return settings.PROJECT_ROOT

        settings_file = sys.modules[settings.SETTINGS_MODULE].__file__
        if settings_file.endswith(".pyc"):
            return settings_file[:-1]
        return settings_file

    @staticmethod
    def filter_params(params):
        """Filter sensitive information out of parameter dictionaries."""

        for key in params.keys():
            if "password" in key:
                del params[key]
        return params
