import functools
import unittest

from pecan import expose
from pecan import util
from pecan.compat import getargspec


class TestArgSpec(unittest.TestCase):

    @property
    def controller(self):

        class RootController(object):

            @expose()
            def index(self, a, b, c=1, *args, **kwargs):
                return 'Hello, World!'

            @staticmethod
            @expose()
            def static_index(a, b, c=1, *args, **kwargs):
                return 'Hello, World!'

        return RootController()

    def test_no_decorator(self):
        expected = getargspec(self.controller.index.__func__)
        actual = util.getargspec(self.controller.index.__func__)
        assert expected == actual

        expected = getargspec(self.controller.static_index)
        actual = util.getargspec(self.controller.static_index)
        assert expected == actual

    def test_simple_decorator(self):
        def dec(f):
            return f

        expected = getargspec(self.controller.index.__func__)
        actual = util.getargspec(dec(self.controller.index.__func__))
        assert expected == actual

        expected = getargspec(self.controller.static_index)
        actual = util.getargspec(dec(self.controller.static_index))
        assert expected == actual

    def test_simple_wrapper(self):
        def dec(f):
            @functools.wraps(f)
            def wrapped(*a, **kw):
                return f(*a, **kw)
            return wrapped

        expected = getargspec(self.controller.index.__func__)
        actual = util.getargspec(dec(self.controller.index.__func__))
        assert expected == actual

        expected = getargspec(self.controller.static_index)
        actual = util.getargspec(dec(self.controller.static_index))
        assert expected == actual

    def test_multiple_decorators(self):
        def dec(f):
            @functools.wraps(f)
            def wrapped(*a, **kw):
                return f(*a, **kw)
            return wrapped

        expected = getargspec(self.controller.index.__func__)
        actual = util.getargspec(dec(dec(dec(self.controller.index.__func__))))
        assert expected == actual

        expected = getargspec(self.controller.static_index)
        actual = util.getargspec(dec(dec(dec(
            self.controller.static_index))))
        assert expected == actual

    def test_decorator_with_args(self):
        def dec(flag):
            def inner(f):
                @functools.wraps(f)
                def wrapped(*a, **kw):
                    return f(*a, **kw)
                return wrapped
            return inner

        expected = getargspec(self.controller.index.__func__)
        actual = util.getargspec(dec(True)(self.controller.index.__func__))
        assert expected == actual

        expected = getargspec(self.controller.static_index)
        actual = util.getargspec(dec(True)(
            self.controller.static_index))
        assert expected == actual

    def test_nested_cells(self):

        def before(handler):
            def deco(f):
                def wrapped(*args, **kwargs):
                    if callable(handler):
                        handler()
                    return f(*args, **kwargs)
                return wrapped
            return deco

        class RootController(object):
            @expose()
            @before(lambda: True)
            def index(self, a, b, c):
                return 'Hello, World!'

        argspec = util._cfg(RootController.index)['argspec']
        assert argspec.args == ['self', 'a', 'b', 'c']

    def test_class_based_decorator(self):

        class deco(object):

            def __init__(self, arg):
                self.arg = arg

            def __call__(self, f):
                @functools.wraps(f)
                def wrapper(*args, **kw):
                    assert self.arg == '12345'
                    return f(*args, **kw)
                return wrapper

        class RootController(object):
            @expose()
            @deco('12345')
            def index(self, a, b, c):
                return 'Hello, World!'

        argspec = util._cfg(RootController.index)['argspec']
        assert argspec.args == ['self', 'a', 'b', 'c']
