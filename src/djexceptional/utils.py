import datetime
import decimal
import re

from django.utils import datetime_safe
from django.utils import simplejson


class ResilientJSONEncoder(simplejson.JSONEncoder):
    """A JSON encoder (with support for dates/times) that should never fail."""

    DATE_FORMAT = "%Y-%m-%d"
    TIME_FORMAT = "%H:%M:%S"

    def default(self, o):
        if isinstance(o, datetime.datetime):
            d = datetime_safe.new_datetime(o)
            return d.strftime("%s %s" % (self.DATE_FORMAT, self.TIME_FORMAT))
        elif isinstance(o, datetime.date):
            d = datetime_safe.new_date(o)
            return d.strftime(self.DATE_FORMAT)
        elif isinstance(o, datetime.time):
            return o.strftime(self.TIME_FORMAT)
        elif isinstance(o, decimal.Decimal):
            return str(o)
        else:
            try:
                return super(ResilientJSONEncoder, self).default(o)
            except Exception:
                return repr(o)


def json_dumps(obj):
    """Dump an object to a JSON string, using the resilient JSON encoder."""

    return simplejson.dumps(obj, cls=ResilientJSONEncoder)


def meta_to_http(meta):
    """Convert a request.META into a dictionary of HTTP headers."""

    headers = {}
    for key in meta:
        if key.startswith("HTTP_"):
            # A heuristic; HTTP_X_FORWARDED_FOR => X-Forwarded-For
            header = re.sub(r'^HTTP_', '', key)
            header = key.replace("_", " ").title().replace(" ", "-")
        elif key in ["CONTENT_LENGTH", "CONTENT_TYPE"]:
            header = key.replace("_", " ").title().replace(" ", "-")
        else:
            continue
        headers[header] = meta[key]
    return headers


def memoize(func):
    """A simple memoize decorator (with no support for keyword arguments)."""

    cache = {}
    def wrapper(*args):
        if args in cache:
            return cache[args]
        cache[args] = value = func(*args)
        return value

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    if hasattr(func, '__module__'):
        wrapper.__module__ = func.__module__
    wrapper.clear = cache.clear

    return wrapper
