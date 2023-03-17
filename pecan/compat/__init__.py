import inspect

import urllib.parse as urlparse  # noqa
from urllib.parse import quote, unquote_plus  # noqa
from urllib.request import urlopen, URLError  # noqa
from html import escape  # noqa
izip = zip


def is_bound_method(ob):
    return inspect.ismethod(ob) and ob.__self__ is not None


def getargspec(func):
    import sys
    if sys.version_info < (3, 5):
        return inspect.getargspec(func)

    from collections import namedtuple
    ArgSpec = namedtuple('ArgSpec', 'args varargs keywords defaults')
    args, varargs, keywords, defaults = inspect.getfullargspec(func)[:4]
    return ArgSpec(args=args, varargs=varargs, keywords=keywords,
                   defaults=defaults)
