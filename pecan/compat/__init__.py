import inspect

import six

if six.PY3:
    import urllib.parse as urlparse
    from urllib.parse import quote, unquote_plus
    from urllib.request import urlopen, URLError
    from html import escape
    izip = zip
else:
    import urlparse  # noqa
    from urllib import quote, unquote_plus  # noqa
    from urllib2 import urlopen, URLError  # noqa
    from cgi import escape  # noqa
    from itertools import izip


def is_bound_method(ob):
    return inspect.ismethod(ob) and six.get_method_self(ob) is not None


def getargspec(func):
    import sys
    if sys.version_info < (3, 5):
        return inspect.getargspec(func)

    sig = inspect._signature_from_callable(func, follow_wrapper_chains=False,
                                           skip_bound_arg=False,
                                           sigcls=inspect.Signature)
    args = [
        p.name for p in sig.parameters.values()
        if p.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
    ]
    varargs = [
        p.name for p in sig.parameters.values()
        if p.kind == inspect.Parameter.VAR_POSITIONAL
    ]
    varargs = varargs[0] if varargs else None
    varkw = [
        p.name for p in sig.parameters.values()
        if p.kind == inspect.Parameter.VAR_KEYWORD
    ]
    varkw = varkw[0] if varkw else None
    defaults = [
        p.default for p in sig.parameters.values()
        if (p.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD and
            p.default is not p.empty)
    ] or None
    if defaults is not None:
        defaults = tuple(defaults)

    from collections import namedtuple
    ArgSpec = namedtuple('ArgSpec', 'args varargs keywords defaults')

    return ArgSpec(args, varargs, varkw, defaults)
