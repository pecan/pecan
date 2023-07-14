from json import dumps
from webtest import TestApp

from pecan import Pecan, expose, abort
from pecan.tests import PecanTestCase


class TestGeneric(PecanTestCase):

    def test_simple_generic(self):
        class RootController(object):
            @expose(generic=True)
            def index(self):
                pass

            @index.when(method='POST', template='json')
            def do_post(self):
                return dict(result='POST')

            @index.when(method='GET')
            def do_get(self):
                return 'GET'

        app = TestApp(Pecan(RootController()))
        r = app.get('/')
        assert r.status_int == 200
        assert r.body == b'GET'

        r = app.post('/')
        assert r.status_int == 200
        assert r.body == dumps(dict(result='POST')).encode('utf-8')

        r = app.get('/do_get', status=404)
        assert r.status_int == 404

    def test_generic_allow_header(self):
        class RootController(object):
            @expose(generic=True)
            def index(self):
                abort(405)

            @index.when(method='POST', template='json')
            def do_post(self):
                return dict(result='POST')

            @index.when(method='GET')
            def do_get(self):
                return 'GET'

            @index.when(method='PATCH')
            def do_patch(self):
                return 'PATCH'

        app = TestApp(Pecan(RootController()))
        r = app.delete('/', expect_errors=True)
        assert r.status_int == 405
        assert r.headers['Allow'] == 'GET, PATCH, POST'

    def test_nested_generic(self):

        class SubSubController(object):
            @expose(generic=True)
            def index(self):
                return 'GET'

            @index.when(method='DELETE', template='json')
            def do_delete(self, name, *args):
                return dict(result=name, args=', '.join(args))

        class SubController(object):
            sub = SubSubController()

        class RootController(object):
            sub = SubController()

        app = TestApp(Pecan(RootController()))
        r = app.get('/sub/sub/')
        assert r.status_int == 200
        assert r.body == b'GET'

        r = app.delete('/sub/sub/joe/is/cool')
        assert r.status_int == 200
        assert r.body == dumps(
            dict(result='joe', args='is, cool')
        ).encode('utf-8')


class TestGenericWithSpecialMethods(PecanTestCase):

    def test_generics_not_allowed(self):

        class C(object):

            def _default(self):
                pass

            def _lookup(self):
                pass

            def _route(self):
                pass

        for method in (C._default, C._lookup, C._route):
            self.assertRaises(
                ValueError,
                expose(generic=True),
                getattr(method, '__func__', method)
            )
