import inspect
import sys

import six


def iscontroller(obj):
    return getattr(obj, 'exposed', False)


def getargspec(method):
    """
    Drill through layers of decorators attempting to locate the actual argspec
    for a method.
    """

    argspec = inspect.getargspec(method)
    args = argspec[0]
    if args and args[0] == 'self':
        return argspec
    if hasattr(method, '__func__'):
        method = method.__func__

    func_closure = six.get_function_closure(method)

    # NOTE(sileht): if the closure is None we cannot look deeper,
    # so return actual argspec, this occurs when the method
    # is static for example.
    if not func_closure:
        return argspec

    closure = None
    # In the case of deeply nested decorators (with arguments), it's possible
    # that there are several callables in scope;  Take a best guess and go
    # with the one that looks most like a pecan controller function
    # ('self' is the first argument)
    func_closure = filter(
        lambda c: six.callable(c.cell_contents),
        func_closure
    )
    func_closure = sorted(
        func_closure,
        key=lambda c: 'self' in c.cell_contents.__code__.co_varnames,
        reverse=True
    )

    closure = func_closure[0]

    method = closure.cell_contents
    return getargspec(method)


def _cfg(f):
    if not hasattr(f, '_pecan'):
        f._pecan = {}
    return f._pecan


if sys.version_info >= (2, 6, 5):
    def encode_if_needed(s):
        return s
else:
    def encode_if_needed(s):  # noqa
        return s.encode('utf-8')
