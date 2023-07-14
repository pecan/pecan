# -*- coding: utf-8 -*-

import sys
import os
import json
import traceback
import warnings
from io import StringIO, BytesIO

import webob
from webob.exc import HTTPNotFound
from webtest import TestApp

from pecan import (
    Pecan, Request, Response, expose, request, response, redirect,
    abort, make_app, override_template, render, route
)
from pecan.templating import (
    _builtin_renderers as builtin_renderers, error_formatters, MakoRenderer
)
from pecan.decorators import accept_noncanonical
from pecan.tests import PecanTestCase

import unittest


class SampleRootController(object):
    pass


class TestAppRoot(PecanTestCase):

    def test_controller_lookup_by_string_path(self):
        app = Pecan('pecan.tests.test_base.SampleRootController')
        assert app.root and app.root.__class__.__name__ == 'SampleRootController'


class TestEmptyContent(PecanTestCase):
    @property
    def app_(self):
        class RootController(object):
            @expose()
            def index(self):
                pass

            @expose()
            def explicit_body(self):
                response.body = b'Hello, World!'

            @expose()
            def empty_body(self):
                response.body = b''

            @expose()
            def explicit_text(self):
                response.text = 'Hello, World!'

            @expose()
            def empty_text(self):
                response.text = ''

            @expose()
            def explicit_json(self):
                response.json = {'foo': 'bar'}

            @expose()
            def explicit_json_body(self):
                response.json_body = {'foo': 'bar'}

            @expose()
            def non_unicode(self):
                return chr(0xc0)

        return TestApp(Pecan(RootController()))

    def test_empty_index(self):
        r = self.app_.get('/')
        self.assertEqual(r.status_int, 204)
        self.assertNotIn('Content-Type', r.headers)
        self.assertEqual(r.headers['Content-Length'], '0')
        self.assertEqual(len(r.body), 0)

    def test_index_with_non_unicode(self):
        r = self.app_.get('/non_unicode/')
        self.assertEqual(r.status_int, 200)

    def test_explicit_body(self):
        r = self.app_.get('/explicit_body/')
        self.assertEqual(r.status_int, 200)
        self.assertEqual(r.body, b'Hello, World!')

    def test_empty_body(self):
        r = self.app_.get('/empty_body/')
        self.assertEqual(r.status_int, 204)
        self.assertEqual(r.body, b'')

    def test_explicit_text(self):
        r = self.app_.get('/explicit_text/')
        self.assertEqual(r.status_int, 200)
        self.assertEqual(r.body, b'Hello, World!')

    def test_empty_text(self):
        r = self.app_.get('/empty_text/')
        self.assertEqual(r.status_int, 204)
        self.assertEqual(r.body, b'')

    def test_explicit_json(self):
        r = self.app_.get('/explicit_json/')
        self.assertEqual(r.status_int, 200)
        json_resp = json.loads(r.body.decode())
        assert json_resp == {'foo': 'bar'}

    def test_explicit_json_body(self):
        r = self.app_.get('/explicit_json_body/')
        self.assertEqual(r.status_int, 200)
        json_resp = json.loads(r.body.decode())
        assert json_resp == {'foo': 'bar'}


class TestAppIterFile(PecanTestCase):
    @property
    def app_(self):
        class RootController(object):
            @expose()
            def index(self):
                body = BytesIO(b'Hello, World!')
                response.body_file = body

            @expose()
            def empty(self):
                body = BytesIO(b'')
                response.body_file = body

        return TestApp(Pecan(RootController()))

    def test_body_generator(self):
        r = self.app_.get('/')
        self.assertEqual(r.status_int, 200)
        assert r.body == b'Hello, World!'

    def test_empty_body_generator(self):
        r = self.app_.get('/empty')
        self.assertEqual(r.status_int, 204)
        assert len(r.body) == 0


class TestInvalidURLEncoding(PecanTestCase):

    @property
    def app_(self):
        class RootController(object):

            @expose()
            def _route(self, args, request):
                assert request.path

        return TestApp(Pecan(RootController()))

    def test_rest_with_non_utf_8_body(self):
        r = self.app_.get('/%aa/', expect_errors=True)
        assert r.status_int == 400


class TestIndexRouting(PecanTestCase):

    @property
    def app_(self):
        class RootController(object):
            @expose()
            def index(self):
                return 'Hello, World!'

        return TestApp(Pecan(RootController()))

    def test_empty_root(self):
        r = self.app_.get('/')
        assert r.status_int == 200
        assert r.body == b'Hello, World!'

    def test_index(self):
        r = self.app_.get('/index')
        assert r.status_int == 200
        assert r.body == b'Hello, World!'

    def test_index_html(self):
        r = self.app_.get('/index.html')
        assert r.status_int == 200
        assert r.body == b'Hello, World!'


class TestObjectDispatch(PecanTestCase):

    @property
    def app_(self):
        class SubSubController(object):
            @expose()
            def index(self):
                return '/sub/sub/'

            @expose()
            def deeper(self):
                return '/sub/sub/deeper'

        class SubController(object):
            @expose()
            def index(self):
                return '/sub/'

            @expose()
            def deeper(self):
                return '/sub/deeper'

            sub = SubSubController()

        class RootController(object):
            @expose()
            def index(self):
                return '/'

            @expose()
            def deeper(self):
                return '/deeper'

            sub = SubController()

        return TestApp(Pecan(RootController()))

    def test_index(self):
        r = self.app_.get('/')
        assert r.status_int == 200
        assert r.body == b'/'

    def test_one_level(self):
        r = self.app_.get('/deeper')
        assert r.status_int == 200
        assert r.body == b'/deeper'

    def test_one_level_with_trailing(self):
        r = self.app_.get('/sub/')
        assert r.status_int == 200
        assert r.body == b'/sub/'

    def test_two_levels(self):
        r = self.app_.get('/sub/deeper')
        assert r.status_int == 200
        assert r.body == b'/sub/deeper'

    def test_two_levels_with_trailing(self):
        r = self.app_.get('/sub/sub/')
        assert r.status_int == 200

    def test_three_levels(self):
        r = self.app_.get('/sub/sub/deeper')
        assert r.status_int == 200
        assert r.body == b'/sub/sub/deeper'


class TestUnicodePathSegments(PecanTestCase):

    def test_unicode_methods(self):
        class RootController(object):
            pass
        setattr(RootController, '🌰', expose()(lambda self: 'Hello, World!'))
        app = TestApp(Pecan(RootController()))

        resp = app.get('/%F0%9F%8C%B0/')
        assert resp.status_int == 200
        assert resp.body == b'Hello, World!'

    def test_unicode_child(self):
        class ChildController(object):
            @expose()
            def index(self):
                return 'Hello, World!'

        class RootController(object):
            pass
        setattr(RootController, '🌰', ChildController())
        app = TestApp(Pecan(RootController()))

        resp = app.get('/%F0%9F%8C%B0/')
        assert resp.status_int == 200
        assert resp.body == b'Hello, World!'


class TestLookups(PecanTestCase):

    @property
    def app_(self):
        class LookupController(object):
            def __init__(self, someID):
                self.someID = someID

            @expose()
            def index(self):
                return '/%s' % self.someID

            @expose()
            def name(self):
                return '/%s/name' % self.someID

        class RootController(object):
            @expose()
            def index(self):
                return '/'

            @expose()
            def _lookup(self, someID, *remainder):
                return LookupController(someID), remainder

        return TestApp(Pecan(RootController()))

    def test_index(self):
        r = self.app_.get('/')
        assert r.status_int == 200
        assert r.body == b'/'

    def test_lookup(self):
        r = self.app_.get('/100/')
        assert r.status_int == 200
        assert r.body == b'/100'

    def test_lookup_with_method(self):
        r = self.app_.get('/100/name')
        assert r.status_int == 200
        assert r.body == b'/100/name'

    def test_lookup_with_wrong_argspec(self):
        class RootController(object):
            @expose()
            def _lookup(self, someID):
                return 'Bad arg spec'  # pragma: nocover

        app = TestApp(Pecan(RootController()))
        r = app.get('/foo/bar', expect_errors=True)
        assert r.status_int == 404

    def test_lookup_with_wrong_return(self):
        class RootController(object):
            @expose()
            def _lookup(self, someID, *remainder):
                return 1

        app = TestApp(Pecan(RootController()))
        self.assertRaises(TypeError,
                          app.get,
                          '/foo/bar', expect_errors=True)


class TestCanonicalLookups(PecanTestCase):

    @property
    def app_(self):
        class LookupController(object):
            def __init__(self, someID):
                self.someID = someID

            @expose()
            def index(self):
                return self.someID

        class UserController(object):
            @expose()
            def _lookup(self, someID, *remainder):
                return LookupController(someID), remainder

        class RootController(object):
            users = UserController()

        return TestApp(Pecan(RootController()))

    def test_canonical_lookup(self):
        assert self.app_.get('/users', expect_errors=404).status_int == 404
        assert self.app_.get('/users/', expect_errors=404).status_int == 404
        assert self.app_.get('/users/100').status_int == 302
        assert self.app_.get('/users/100/').body == b'100'


class TestControllerArguments(PecanTestCase):

    @property
    def app_(self):
        class RootController(object):
            @expose()
            def index(self, id):
                return 'index: %s' % id

            @expose()
            def multiple(self, one, two):
                return 'multiple: %s, %s' % (one, two)

            @expose()
            def optional(self, id=None):
                return 'optional: %s' % str(id)

            @expose()
            def multiple_optional(self, one=None, two=None, three=None):
                return 'multiple_optional: %s, %s, %s' % (one, two, three)

            @expose()
            def variable_args(self, *args):
                return 'variable_args: %s' % ', '.join(args)

            @expose()
            def variable_kwargs(self, **kwargs):
                data = [
                    '%s=%s' % (key, kwargs[key])
                    for key in sorted(kwargs.keys())
                ]
                return 'variable_kwargs: %s' % ', '.join(data)

            @expose()
            def variable_all(self, *args, **kwargs):
                data = [
                    '%s=%s' % (key, kwargs[key])
                    for key in sorted(kwargs.keys())
                ]
                return 'variable_all: %s' % ', '.join(list(args) + data)

            @expose()
            def eater(self, id, dummy=None, *args, **kwargs):
                data = [
                    '%s=%s' % (key, kwargs[key])
                    for key in sorted(kwargs.keys())
                ]
                return 'eater: %s, %s, %s' % (
                    id,
                    dummy,
                    ', '.join(list(args) + data)
                )

            @staticmethod
            @expose()
            def static(id):
                return "id is %s" % id

            @expose()
            def _route(self, args, request):
                if hasattr(self, args[0]):
                    return getattr(self, args[0]), args[1:]
                else:
                    return self.index, args

        return TestApp(Pecan(RootController()))

    def test_required_argument(self):
        try:
            r = self.app_.get('/')
            assert r.status_int != 200  # pragma: nocover
        except Exception as ex:
            assert type(ex) == TypeError
            assert ex.args[0] in (
                "index() takes exactly 2 arguments (1 given)",
                "index() missing 1 required positional argument: 'id'",
                (
                    "TestControllerArguments.app_.<locals>.RootController."
                    "index() missing 1 required positional argument: 'id'"
                ),
            )  # this messaging changed in Python 3.3 and again in Python 3.10

    def test_single_argument(self):
        r = self.app_.get('/1')
        assert r.status_int == 200
        assert r.body == b'index: 1'

    def test_single_argument_with_encoded_url(self):
        r = self.app_.get('/This%20is%20a%20test%21')
        assert r.status_int == 200
        assert r.body == b'index: This is a test!'

    def test_single_argument_with_plus(self):
        r = self.app_.get('/foo+bar')
        assert r.status_int == 200
        assert r.body == b'index: foo+bar'

    def test_single_argument_with_encoded_plus(self):
        r = self.app_.get('/foo%2Bbar')
        assert r.status_int == 200
        assert r.body == b'index: foo+bar'

    def test_two_arguments(self):
        r = self.app_.get('/1/dummy', status=404)
        assert r.status_int == 404

    def test_keyword_argument(self):
        r = self.app_.get('/?id=2')
        assert r.status_int == 200
        assert r.body == b'index: 2'

    def test_keyword_argument_with_encoded_url(self):
        r = self.app_.get('/?id=This%20is%20a%20test%21')
        assert r.status_int == 200
        assert r.body == b'index: This is a test!'

    def test_keyword_argument_with_plus(self):
        r = self.app_.get('/?id=foo+bar')
        assert r.status_int == 200
        assert r.body == b'index: foo bar'

    def test_keyword_argument_with_encoded_plus(self):
        r = self.app_.get('/?id=foo%2Bbar')
        assert r.status_int == 200
        assert r.body == b'index: foo+bar'

    def test_argument_and_keyword_argument(self):
        r = self.app_.get('/3?id=three')
        assert r.status_int == 200
        assert r.body == b'index: 3'

    def test_encoded_argument_and_keyword_argument(self):
        r = self.app_.get('/This%20is%20a%20test%21?id=three')
        assert r.status_int == 200
        assert r.body == b'index: This is a test!'

    def test_explicit_kwargs(self):
        r = self.app_.post('/', {'id': '4'})
        assert r.status_int == 200
        assert r.body == b'index: 4'

    def test_path_with_explicit_kwargs(self):
        r = self.app_.post('/4', {'id': 'four'})
        assert r.status_int == 200
        assert r.body == b'index: 4'

    def test_explicit_json_kwargs(self):
        r = self.app_.post_json('/', {'id': '4'})
        assert r.status_int == 200
        assert r.body == b'index: 4'

    def test_path_with_explicit_json_kwargs(self):
        r = self.app_.post_json('/4', {'id': 'four'})
        assert r.status_int == 200
        assert r.body == b'index: 4'

    def test_multiple_kwargs(self):
        r = self.app_.get('/?id=5&dummy=dummy')
        assert r.status_int == 200
        assert r.body == b'index: 5'

    def test_kwargs_from_root(self):
        r = self.app_.post('/', {'id': '6', 'dummy': 'dummy'})
        assert r.status_int == 200
        assert r.body == b'index: 6'

    def test_json_kwargs_from_root(self):
        r = self.app_.post_json('/', {'id': '6', 'dummy': 'dummy'})
        assert r.status_int == 200
        assert r.body == b'index: 6'

        # multiple args

    def test_multiple_positional_arguments(self):
        r = self.app_.get('/multiple/one/two')
        assert r.status_int == 200
        assert r.body == b'multiple: one, two'

    def test_multiple_positional_arguments_with_url_encode(self):
        r = self.app_.get('/multiple/One%20/Two%21')
        assert r.status_int == 200
        assert r.body == b'multiple: One , Two!'

    def test_multiple_positional_arguments_with_kwargs(self):
        r = self.app_.get('/multiple?one=three&two=four')
        assert r.status_int == 200
        assert r.body == b'multiple: three, four'

    def test_multiple_positional_arguments_with_url_encoded_kwargs(self):
        r = self.app_.get('/multiple?one=Three%20&two=Four%20%21')
        assert r.status_int == 200
        assert r.body == b'multiple: Three , Four !'

    def test_positional_args_with_dictionary_kwargs(self):
        r = self.app_.post('/multiple', {'one': 'five', 'two': 'six'})
        assert r.status_int == 200
        assert r.body == b'multiple: five, six'

    def test_positional_args_with_json_kwargs(self):
        r = self.app_.post_json('/multiple', {'one': 'five', 'two': 'six'})
        assert r.status_int == 200
        assert r.body == b'multiple: five, six'

    def test_positional_args_with_url_encoded_dictionary_kwargs(self):
        r = self.app_.post('/multiple', {'one': 'Five%20', 'two': 'Six%20%21'})
        assert r.status_int == 200
        assert r.body == b'multiple: Five%20, Six%20%21'

        # optional arg
    def test_optional_arg(self):
        r = self.app_.get('/optional')
        assert r.status_int == 200
        assert r.body == b'optional: None'

    def test_multiple_optional(self):
        r = self.app_.get('/optional/1')
        assert r.status_int == 200
        assert r.body == b'optional: 1'

    def test_multiple_optional_url_encoded(self):
        r = self.app_.get('/optional/Some%20Number')
        assert r.status_int == 200
        assert r.body == b'optional: Some Number'

    def test_multiple_optional_missing(self):
        r = self.app_.get('/optional/2/dummy', status=404)
        assert r.status_int == 404

    def test_multiple_with_kwargs(self):
        r = self.app_.get('/optional?id=2')
        assert r.status_int == 200
        assert r.body == b'optional: 2'

    def test_multiple_with_url_encoded_kwargs(self):
        r = self.app_.get('/optional?id=Some%20Number')
        assert r.status_int == 200
        assert r.body == b'optional: Some Number'

    def test_multiple_args_with_url_encoded_kwargs(self):
        r = self.app_.get('/optional/3?id=three')
        assert r.status_int == 200
        assert r.body == b'optional: 3'

    def test_url_encoded_positional_args(self):
        r = self.app_.get('/optional/Some%20Number?id=three')
        assert r.status_int == 200
        assert r.body == b'optional: Some Number'

    def test_optional_arg_with_kwargs(self):
        r = self.app_.post('/optional', {'id': '4'})
        assert r.status_int == 200
        assert r.body == b'optional: 4'

    def test_optional_arg_with_json_kwargs(self):
        r = self.app_.post_json('/optional', {'id': '4'})
        assert r.status_int == 200
        assert r.body == b'optional: 4'

    def test_optional_arg_with_url_encoded_kwargs(self):
        r = self.app_.post('/optional', {'id': 'Some%20Number'})
        assert r.status_int == 200
        assert r.body == b'optional: Some%20Number'

    def test_multiple_positional_arguments_with_dictionary_kwargs(self):
        r = self.app_.post('/optional/5', {'id': 'five'})
        assert r.status_int == 200
        assert r.body == b'optional: 5'

    def test_multiple_positional_arguments_with_json_kwargs(self):
        r = self.app_.post_json('/optional/5', {'id': 'five'})
        assert r.status_int == 200
        assert r.body == b'optional: 5'

    def test_multiple_positional_url_encoded_arguments_with_kwargs(self):
        r = self.app_.post('/optional/Some%20Number', {'id': 'five'})
        assert r.status_int == 200
        assert r.body == b'optional: Some Number'

    def test_optional_arg_with_multiple_kwargs(self):
        r = self.app_.get('/optional?id=6&dummy=dummy')
        assert r.status_int == 200
        assert r.body == b'optional: 6'

    def test_optional_arg_with_multiple_url_encoded_kwargs(self):
        r = self.app_.get('/optional?id=Some%20Number&dummy=dummy')
        assert r.status_int == 200
        assert r.body == b'optional: Some Number'

    def test_optional_arg_with_multiple_dictionary_kwargs(self):
        r = self.app_.post('/optional', {'id': '7', 'dummy': 'dummy'})
        assert r.status_int == 200
        assert r.body == b'optional: 7'

    def test_optional_arg_with_multiple_json_kwargs(self):
        r = self.app_.post_json('/optional', {'id': '7', 'dummy': 'dummy'})
        assert r.status_int == 200
        assert r.body == b'optional: 7'

    def test_optional_arg_with_multiple_url_encoded_dictionary_kwargs(self):
        r = self.app_.post('/optional', {
            'id': 'Some%20Number',
            'dummy': 'dummy'
        })
        assert r.status_int == 200
        assert r.body == b'optional: Some%20Number'

        # multiple optional args

    def test_multiple_optional_positional_args(self):
        r = self.app_.get('/multiple_optional')
        assert r.status_int == 200
        assert r.body == b'multiple_optional: None, None, None'

    def test_multiple_optional_positional_args_one_arg(self):
        r = self.app_.get('/multiple_optional/1')
        assert r.status_int == 200
        assert r.body == b'multiple_optional: 1, None, None'

    def test_multiple_optional_positional_args_one_url_encoded_arg(self):
        r = self.app_.get('/multiple_optional/One%21')
        assert r.status_int == 200
        assert r.body == b'multiple_optional: One!, None, None'

    def test_multiple_optional_positional_args_all_args(self):
        r = self.app_.get('/multiple_optional/1/2/3')
        assert r.status_int == 200
        assert r.body == b'multiple_optional: 1, 2, 3'

    def test_multiple_optional_positional_args_all_url_encoded_args(self):
        r = self.app_.get('/multiple_optional/One%21/Two%21/Three%21')
        assert r.status_int == 200
        assert r.body == b'multiple_optional: One!, Two!, Three!'

    def test_multiple_optional_positional_args_too_many_args(self):
        r = self.app_.get('/multiple_optional/1/2/3/dummy', status=404)
        assert r.status_int == 404

    def test_multiple_optional_positional_args_with_kwargs(self):
        r = self.app_.get('/multiple_optional?one=1')
        assert r.status_int == 200
        assert r.body == b'multiple_optional: 1, None, None'

    def test_multiple_optional_positional_args_with_url_encoded_kwargs(self):
        r = self.app_.get('/multiple_optional?one=One%21')
        assert r.status_int == 200
        assert r.body == b'multiple_optional: One!, None, None'

    def test_multiple_optional_positional_args_with_string_kwargs(self):
        r = self.app_.get('/multiple_optional/1?one=one')
        assert r.status_int == 200
        assert r.body == b'multiple_optional: 1, None, None'

    def test_multiple_optional_positional_args_with_encoded_str_kwargs(self):
        r = self.app_.get('/multiple_optional/One%21?one=one')
        assert r.status_int == 200
        assert r.body == b'multiple_optional: One!, None, None'

    def test_multiple_optional_positional_args_with_dict_kwargs(self):
        r = self.app_.post('/multiple_optional', {'one': '1'})
        assert r.status_int == 200
        assert r.body == b'multiple_optional: 1, None, None'

    def test_multiple_optional_positional_args_with_json_kwargs(self):
        r = self.app_.post_json('/multiple_optional', {'one': '1'})
        assert r.status_int == 200
        assert r.body == b'multiple_optional: 1, None, None'

    def test_multiple_optional_positional_args_with_encoded_dict_kwargs(self):
        r = self.app_.post('/multiple_optional', {'one': 'One%21'})
        assert r.status_int == 200
        assert r.body == b'multiple_optional: One%21, None, None'

    def test_multiple_optional_positional_args_and_dict_kwargs(self):
        r = self.app_.post('/multiple_optional/1', {'one': 'one'})
        assert r.status_int == 200
        assert r.body == b'multiple_optional: 1, None, None'

    def test_multiple_optional_positional_args_and_json_kwargs(self):
        r = self.app_.post_json('/multiple_optional/1', {'one': 'one'})
        assert r.status_int == 200
        assert r.body == b'multiple_optional: 1, None, None'

    def test_multiple_optional_encoded_positional_args_and_dict_kwargs(self):
        r = self.app_.post('/multiple_optional/One%21', {'one': 'one'})
        assert r.status_int == 200
        assert r.body == b'multiple_optional: One!, None, None'

    def test_multiple_optional_args_with_multiple_kwargs(self):
        r = self.app_.get('/multiple_optional?one=1&two=2&three=3&four=4')
        assert r.status_int == 200
        assert r.body == b'multiple_optional: 1, 2, 3'

    def test_multiple_optional_args_with_multiple_encoded_kwargs(self):
        r = self.app_.get(
            '/multiple_optional?one=One%21&two=Two%21&three=Three%21&four=4'
        )
        assert r.status_int == 200
        assert r.body == b'multiple_optional: One!, Two!, Three!'

    def test_multiple_optional_args_with_multiple_dict_kwargs(self):
        r = self.app_.post(
            '/multiple_optional',
            {'one': '1', 'two': '2', 'three': '3', 'four': '4'}
        )
        assert r.status_int == 200
        assert r.body == b'multiple_optional: 1, 2, 3'

    def test_multiple_optional_args_with_multiple_json_kwargs(self):
        r = self.app_.post_json(
            '/multiple_optional',
            {'one': '1', 'two': '2', 'three': '3', 'four': '4'}
        )
        assert r.status_int == 200
        assert r.body == b'multiple_optional: 1, 2, 3'

    def test_multiple_optional_args_with_multiple_encoded_dict_kwargs(self):
        r = self.app_.post(
            '/multiple_optional',
            {
                'one': 'One%21',
                'two': 'Two%21',
                'three': 'Three%21',
                'four': '4'
            }
        )
        assert r.status_int == 200
        assert r.body == b'multiple_optional: One%21, Two%21, Three%21'

    def test_multiple_optional_args_with_last_kwarg(self):
        r = self.app_.get('/multiple_optional?three=3')
        assert r.status_int == 200
        assert r.body == b'multiple_optional: None, None, 3'

    def test_multiple_optional_args_with_last_encoded_kwarg(self):
        r = self.app_.get('/multiple_optional?three=Three%21')
        assert r.status_int == 200
        assert r.body == b'multiple_optional: None, None, Three!'

    def test_multiple_optional_args_with_middle_arg(self):
        r = self.app_.get('/multiple_optional', {'two': '2'})
        assert r.status_int == 200
        assert r.body == b'multiple_optional: None, 2, None'

    def test_variable_args(self):
        r = self.app_.get('/variable_args')
        assert r.status_int == 200
        assert r.body == b'variable_args: '

    def test_multiple_variable_args(self):
        r = self.app_.get('/variable_args/1/dummy')
        assert r.status_int == 200
        assert r.body == b'variable_args: 1, dummy'

    def test_multiple_encoded_variable_args(self):
        r = self.app_.get('/variable_args/Testing%20One%20Two/Three%21')
        assert r.status_int == 200
        assert r.body == b'variable_args: Testing One Two, Three!'

    def test_variable_args_with_kwargs(self):
        r = self.app_.get('/variable_args?id=2&dummy=dummy')
        assert r.status_int == 200
        assert r.body == b'variable_args: '

    def test_variable_args_with_dict_kwargs(self):
        r = self.app_.post('/variable_args', {'id': '3', 'dummy': 'dummy'})
        assert r.status_int == 200
        assert r.body == b'variable_args: '

    def test_variable_args_with_json_kwargs(self):
        r = self.app_.post_json(
            '/variable_args',
            {'id': '3', 'dummy': 'dummy'}
        )
        assert r.status_int == 200
        assert r.body == b'variable_args: '

    def test_variable_kwargs(self):
        r = self.app_.get('/variable_kwargs')
        assert r.status_int == 200
        assert r.body == b'variable_kwargs: '

    def test_multiple_variable_kwargs(self):
        r = self.app_.get('/variable_kwargs/1/dummy', status=404)
        assert r.status_int == 404

    def test_multiple_variable_kwargs_with_explicit_kwargs(self):
        r = self.app_.get('/variable_kwargs?id=2&dummy=dummy')
        assert r.status_int == 200
        assert r.body == b'variable_kwargs: dummy=dummy, id=2'

    def test_multiple_variable_kwargs_with_explicit_encoded_kwargs(self):
        r = self.app_.get(
            '/variable_kwargs?id=Two%21&dummy=This%20is%20a%20test'
        )
        assert r.status_int == 200
        assert r.body == b'variable_kwargs: dummy=This is a test, id=Two!'

    def test_multiple_variable_kwargs_with_dict_kwargs(self):
        r = self.app_.post('/variable_kwargs', {'id': '3', 'dummy': 'dummy'})
        assert r.status_int == 200
        assert r.body == b'variable_kwargs: dummy=dummy, id=3'

    def test_multiple_variable_kwargs_with_json_kwargs(self):
        r = self.app_.post_json(
            '/variable_kwargs',
            {'id': '3', 'dummy': 'dummy'}
        )
        assert r.status_int == 200
        assert r.body == b'variable_kwargs: dummy=dummy, id=3'

    def test_multiple_variable_kwargs_with_encoded_dict_kwargs(self):
        r = self.app_.post(
            '/variable_kwargs',
            {'id': 'Three%21', 'dummy': 'This%20is%20a%20test'}
        )
        assert r.status_int == 200
        result = b'variable_kwargs: dummy=This%20is%20a%20test, id=Three%21'
        assert r.body == result

    def test_variable_all(self):
        r = self.app_.get('/variable_all')
        assert r.status_int == 200
        assert r.body == b'variable_all: '

    def test_variable_all_with_one_extra(self):
        r = self.app_.get('/variable_all/1')
        assert r.status_int == 200
        assert r.body == b'variable_all: 1'

    def test_variable_all_with_two_extras(self):
        r = self.app_.get('/variable_all/2/dummy')
        assert r.status_int == 200
        assert r.body == b'variable_all: 2, dummy'

    def test_variable_mixed(self):
        r = self.app_.get('/variable_all/3?month=1&day=12')
        assert r.status_int == 200
        assert r.body == b'variable_all: 3, day=12, month=1'

    def test_variable_mixed_explicit(self):
        r = self.app_.get('/variable_all/4?id=four&month=1&day=12')
        assert r.status_int == 200
        assert r.body == b'variable_all: 4, day=12, id=four, month=1'

    def test_variable_post(self):
        r = self.app_.post('/variable_all/5/dummy')
        assert r.status_int == 200
        assert r.body == b'variable_all: 5, dummy'

    def test_variable_post_with_kwargs(self):
        r = self.app_.post('/variable_all/6', {'month': '1', 'day': '12'})
        assert r.status_int == 200
        assert r.body == b'variable_all: 6, day=12, month=1'

    def test_variable_post_with_json_kwargs(self):
        r = self.app_.post_json(
            '/variable_all/6',
            {'month': '1', 'day': '12'}
        )
        assert r.status_int == 200
        assert r.body == b'variable_all: 6, day=12, month=1'

    def test_variable_post_mixed(self):
        r = self.app_.post(
            '/variable_all/7',
            {'id': 'seven', 'month': '1', 'day': '12'}
        )
        assert r.status_int == 200
        assert r.body == b'variable_all: 7, day=12, id=seven, month=1'

    def test_variable_post_mixed_with_json(self):
        r = self.app_.post_json(
            '/variable_all/7',
            {'id': 'seven', 'month': '1', 'day': '12'}
        )
        assert r.status_int == 200
        assert r.body == b'variable_all: 7, day=12, id=seven, month=1'

    def test_duplicate_query_parameters_GET(self):
        r = self.app_.get('/variable_kwargs?list=1&list=2')
        assert r.status_int == 200
        assert r.body == b"variable_kwargs: list=['1', '2']"

    def test_duplicate_query_parameters_POST(self):
        r = self.app_.post('/variable_kwargs',
                           {'list': ['1', '2']})
        assert r.status_int == 200
        assert r.body == b"variable_kwargs: list=['1', '2']"

    def test_duplicate_query_parameters_POST_mixed(self):
        r = self.app_.post('/variable_kwargs?list=1&list=2',
                           {'list': ['3', '4']})
        assert r.status_int == 200
        assert r.body == b"variable_kwargs: list=['1', '2', '3', '4']"

    def test_duplicate_query_parameters_POST_mixed_json(self):
        r = self.app_.post('/variable_kwargs?list=1&list=2',
                           {'list': 3})
        assert r.status_int == 200
        assert r.body == b"variable_kwargs: list=['1', '2', '3']"

    def test_staticmethod(self):
        r = self.app_.get('/static/foobar')
        assert r.status_int == 200
        assert r.body == b'id is foobar'

    def test_no_remainder(self):
        try:
            r = self.app_.get('/eater')
            assert r.status_int != 200  # pragma: nocover
        except Exception as ex:
            assert type(ex) == TypeError
            assert ex.args[0] in (
                "eater() takes exactly 2 arguments (1 given)",
                "eater() missing 1 required positional argument: 'id'",
                (
                    "TestControllerArguments.app_.<locals>.RootController."
                    "eater() missing 1 required positional argument: 'id'"
                ),
            )  # this messaging changed in Python 3.3 and again in Python 3.10

    def test_one_remainder(self):
        r = self.app_.get('/eater/1')
        assert r.status_int == 200
        assert r.body == b'eater: 1, None, '

    def test_two_remainders(self):
        r = self.app_.get('/eater/2/dummy')
        assert r.status_int == 200
        assert r.body == b'eater: 2, dummy, '

    def test_many_remainders(self):
        r = self.app_.get('/eater/3/dummy/foo/bar')
        assert r.status_int == 200
        assert r.body == b'eater: 3, dummy, foo, bar'

    def test_remainder_with_kwargs(self):
        r = self.app_.get('/eater/4?month=1&day=12')
        assert r.status_int == 200
        assert r.body == b'eater: 4, None, day=12, month=1'

    def test_remainder_with_many_kwargs(self):
        r = self.app_.get('/eater/5?id=five&month=1&day=12&dummy=dummy')
        assert r.status_int == 200
        assert r.body == b'eater: 5, dummy, day=12, month=1'

    def test_post_remainder(self):
        r = self.app_.post('/eater/6')
        assert r.status_int == 200
        assert r.body == b'eater: 6, None, '

    def test_post_three_remainders(self):
        r = self.app_.post('/eater/7/dummy')
        assert r.status_int == 200
        assert r.body == b'eater: 7, dummy, '

    def test_post_many_remainders(self):
        r = self.app_.post('/eater/8/dummy/foo/bar')
        assert r.status_int == 200
        assert r.body == b'eater: 8, dummy, foo, bar'

    def test_post_remainder_with_kwargs(self):
        r = self.app_.post('/eater/9', {'month': '1', 'day': '12'})
        assert r.status_int == 200
        assert r.body == b'eater: 9, None, day=12, month=1'

    def test_post_empty_remainder_with_json_kwargs(self):
        r = self.app_.post_json('/eater/9/', {'month': '1', 'day': '12'})
        assert r.status_int == 200
        assert r.body == b'eater: 9, None, day=12, month=1'

    def test_post_remainder_with_json_kwargs(self):
        r = self.app_.post_json('/eater/9', {'month': '1', 'day': '12'})
        assert r.status_int == 200
        assert r.body == b'eater: 9, None, day=12, month=1'

    def test_post_many_remainders_with_many_kwargs(self):
        r = self.app_.post(
            '/eater/10',
            {'id': 'ten', 'month': '1', 'day': '12', 'dummy': 'dummy'}
        )
        assert r.status_int == 200
        assert r.body == b'eater: 10, dummy, day=12, month=1'

    def test_post_many_remainders_with_many_json_kwargs(self):
        r = self.app_.post_json(
            '/eater/10',
            {'id': 'ten', 'month': '1', 'day': '12', 'dummy': 'dummy'}
        )
        assert r.status_int == 200
        assert r.body == b'eater: 10, dummy, day=12, month=1'


class TestDefaultErrorRendering(PecanTestCase):

    def test_plain_error(self):
        class RootController(object):
            pass

        app = TestApp(Pecan(RootController()))
        r = app.get('/', status=404)
        assert r.status_int == 404
        assert r.content_type == 'text/plain'
        assert r.body == HTTPNotFound().plain_body({}).encode('utf-8')

    def test_html_error(self):
        class RootController(object):
            pass

        app = TestApp(Pecan(RootController()))
        r = app.get('/', headers={'Accept': 'text/html'}, status=404)
        assert r.status_int == 404
        assert r.content_type == 'text/html'
        assert r.body == HTTPNotFound().html_body({}).encode('utf-8')

    def test_json_error(self):
        class RootController(object):
            pass

        app = TestApp(Pecan(RootController()))
        r = app.get('/', headers={'Accept': 'application/json'}, status=404)
        assert r.status_int == 404
        json_resp = json.loads(r.body.decode())
        assert json_resp['code'] == 404
        assert json_resp['description'] is None
        assert json_resp['title'] == 'Not Found'
        assert r.content_type == 'application/json'


class TestAbort(PecanTestCase):

    def test_abort(self):
        class RootController(object):
            @expose()
            def index(self):
                abort(404)

        app = TestApp(Pecan(RootController()))
        r = app.get('/', status=404)
        assert r.status_int == 404

    def test_abort_with_detail(self):
        class RootController(object):
            @expose()
            def index(self):
                abort(status_code=401, detail='Not Authorized')

        app = TestApp(Pecan(RootController()))
        r = app.get('/', status=401)
        assert r.status_int == 401

    def test_abort_keeps_traceback(self):
        last_exc, last_traceback = None, None

        try:
            try:
                raise Exception('Bottom Exception')
            except:
                abort(404)
        except Exception:
            last_exc, _, last_traceback = sys.exc_info()

        assert last_exc is HTTPNotFound
        assert 'Bottom Exception' in traceback.format_tb(last_traceback)[-1]


class TestScriptName(PecanTestCase):

    def setUp(self):
        super(TestScriptName, self).setUp()
        self.environ = {'SCRIPT_NAME': '/foo'}

    def test_handle_script_name(self):
        class RootController(object):
            @expose()
            def index(self):
                return 'Root Index'

        app = TestApp(Pecan(RootController()), extra_environ=self.environ)
        r = app.get('/foo/')
        assert r.status_int == 200


class TestRedirect(PecanTestCase):

    @property
    def app_(self):
        class RootController(object):
            @expose()
            def index(self):
                redirect('/testing')

            @expose()
            def internal(self):
                redirect('/testing', internal=True)

            @expose()
            def bad_internal(self):
                redirect('/testing', internal=True, code=301)

            @expose()
            def permanent(self):
                redirect('/testing', code=301)

            @expose()
            def testing(self):
                return 'it worked!'

        return TestApp(make_app(RootController(), debug=False))

    def test_index(self):
        r = self.app_.get('/')
        assert r.status_int == 302
        r = r.follow()
        assert r.status_int == 200
        assert r.body == b'it worked!'

    def test_internal(self):
        r = self.app_.get('/internal')
        assert r.status_int == 200
        assert r.body == b'it worked!'

    def test_internal_with_301(self):
        self.assertRaises(ValueError, self.app_.get, '/bad_internal')

    def test_permanent_redirect(self):
        r = self.app_.get('/permanent')
        assert r.status_int == 301
        r = r.follow()
        assert r.status_int == 200
        assert r.body == b'it worked!'

    def test_x_forward_proto(self):
        class ChildController(object):
            @expose()
            def index(self):
                redirect('/testing')  # pragma: nocover

        class RootController(object):
            @expose()
            def index(self):
                redirect('/testing')  # pragma: nocover

            @expose()
            def testing(self):
                return 'it worked!'  # pragma: nocover
            child = ChildController()

        app = TestApp(make_app(RootController(), debug=True))
        res = app.get(
            '/child', extra_environ=dict(HTTP_X_FORWARDED_PROTO='https')
        )
        # non-canonical url will redirect, so we won't get a 301
        assert res.status_int == 302
        # should add trailing / and changes location to https
        assert res.location == 'https://localhost/child/'
        assert res.request.environ['HTTP_X_FORWARDED_PROTO'] == 'https'


class TestInternalRedirectContext(PecanTestCase):

    @property
    def app_(self):
        class RootController(object):

            @expose()
            def redirect_with_context(self):
                request.context['foo'] = 'bar'
                redirect('/testing')

            @expose()
            def internal_with_context(self):
                request.context['foo'] = 'bar'
                redirect('/testing', internal=True)

            @expose('json')
            def testing(self):
                return request.context

        return TestApp(make_app(RootController(), debug=False))

    def test_internal_with_request_context(self):
        r = self.app_.get('/internal_with_context')
        assert r.status_int == 200
        assert json.loads(r.body.decode()) == {'foo': 'bar'}

    def test_context_does_not_bleed(self):
        r = self.app_.get('/redirect_with_context').follow()
        assert r.status_int == 200
        assert json.loads(r.body.decode()) == {}


class TestStreamedResponse(PecanTestCase):

    def test_streaming_response(self):

        class RootController(object):
            @expose(content_type='text/plain')
            def test(self, foo):
                if foo == 'stream':
                    # mimic large file
                    contents = BytesIO(b'stream')
                    response.content_type = 'application/octet-stream'
                    contents.seek(0, os.SEEK_END)
                    response.content_length = contents.tell()
                    contents.seek(0, os.SEEK_SET)
                    response.app_iter = contents
                    return response
                else:
                    return 'plain text'

        app = TestApp(Pecan(RootController()))
        r = app.get('/test/stream')
        assert r.content_type == 'application/octet-stream'
        assert r.body == b'stream'

        r = app.get('/test/plain')
        assert r.content_type == 'text/plain'
        assert r.body == b'plain text'


class TestManualResponse(PecanTestCase):

    def test_manual_response(self):

        class RootController(object):
            @expose()
            def index(self):
                resp = webob.Response(response.environ)
                resp.body = b'Hello, World!'
                return resp

        app = TestApp(Pecan(RootController()))
        r = app.get('/')
        assert r.body == b'Hello, World!'


class TestCustomResponseandRequest(PecanTestCase):

    def test_custom_objects(self):

        class CustomRequest(Request):

            @property
            def headers(self):
                headers = super(CustomRequest, self).headers
                headers['X-Custom-Request'] = 'ABC'
                return headers

        class CustomResponse(Response):

            @property
            def headers(self):
                headers = super(CustomResponse, self).headers
                headers['X-Custom-Response'] = 'XYZ'
                return headers

        class RootController(object):
            @expose()
            def index(self):
                return request.headers.get('X-Custom-Request')

        app = TestApp(Pecan(
            RootController(),
            request_cls=CustomRequest,
            response_cls=CustomResponse
        ))
        r = app.get('/')
        assert r.body == b'ABC'
        assert r.headers.get('X-Custom-Response') == 'XYZ'


class TestThreadLocalState(PecanTestCase):

    def test_thread_local_dir(self):
        """
        Threadlocal proxies for request and response should properly
        proxy ``dir()`` calls to the underlying webob class.
        """
        class RootController(object):
            @expose()
            def index(self):
                assert 'method' in dir(request)
                assert 'status' in dir(response)
                return '/'

        app = TestApp(Pecan(RootController()))
        r = app.get('/')
        assert r.status_int == 200
        assert r.body == b'/'

    def test_request_state_cleanup(self):
        """
        After a request, the state local() should be totally clean
        except for state.app (so that objects don't leak between requests)
        """
        from pecan.core import state

        class RootController(object):
            @expose()
            def index(self):
                return '/'

        app = TestApp(Pecan(RootController()))
        r = app.get('/')
        assert r.status_int == 200
        assert r.body == b'/'

        assert state.__dict__ == {}


class TestFileTypeExtensions(PecanTestCase):

    @property
    def app_(self):
        """
        Test extension splits
        """
        class RootController(object):
            @expose(content_type=None)
            def _default(self, *args):
                ext = request.pecan['extension']
                assert len(args) == 1
                if ext:
                    assert ext not in args[0]
                return ext or ''

        return TestApp(Pecan(RootController()))

    def test_html_extension(self):
        for path in ('/index.html', '/index.html/'):
            r = self.app_.get(path)
            assert r.status_int == 200
            assert r.body == b'.html'

    def test_image_extension(self):
        for path in ('/index.png', '/index.png/'):
            r = self.app_.get(path)
            assert r.status_int == 200
            assert r.body == b'.png'

    def test_hidden_file(self):
        for path in ('/.vimrc', '/.vimrc/'):
            r = self.app_.get(path)
            assert r.status_int == 204
            assert r.body == b''

    def test_multi_dot_extension(self):
        for path in ('/gradient.min.js', '/gradient.min.js/'):
            r = self.app_.get(path)
            assert r.status_int == 200
            assert r.body == b'.js'

    def test_bad_content_type(self):
        class RootController(object):
            @expose()
            def index(self):
                return '/'

        app = TestApp(Pecan(RootController()))
        r = app.get('/')
        assert r.status_int == 200
        assert r.body == b'/'

        r = app.get('/index.html', expect_errors=True)
        assert r.status_int == 200
        assert r.body == b'/'

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            r = app.get('/index.txt', expect_errors=True)
            assert r.status_int == 404

    def test_unknown_file_extension(self):
        class RootController(object):
            @expose(content_type=None)
            def _default(self, *args):
                assert 'example:x.tiny' in args
                assert request.pecan['extension'] is None
                return 'SOME VALUE'

        app = TestApp(Pecan(RootController()))

        r = app.get('/example:x.tiny')
        assert r.status_int == 200
        assert r.body == b'SOME VALUE'

    def test_guessing_disabled(self):
        class RootController(object):
            @expose(content_type=None)
            def _default(self, *args):
                assert 'index.html' in args
                assert request.pecan['extension'] is None
                return 'SOME VALUE'

        app = TestApp(Pecan(RootController(),
                            guess_content_type_from_ext=False))

        r = app.get('/index.html')
        assert r.status_int == 200
        assert r.body == b'SOME VALUE'

    def test_content_type_guessing_disabled(self):

        class ResourceController(object):

            def __init__(self, name):
                self.name = name
                assert self.name == 'file.html'

            @expose('json')
            def index(self):
                return dict(name=self.name)

        class RootController(object):

            @expose()
            def _lookup(self, name, *remainder):
                return ResourceController(name), remainder

        app = TestApp(
            Pecan(RootController(), guess_content_type_from_ext=False)
        )

        r = app.get('/file.html/')
        assert r.status_int == 200
        result = dict(json.loads(r.body.decode()))
        assert result == {'name': 'file.html'}

        r = app.get('/file.html')
        assert r.status_int == 302
        r = r.follow()
        result = dict(json.loads(r.body.decode()))
        assert result == {'name': 'file.html'}


class TestContentTypeByAcceptHeaders(PecanTestCase):

    @property
    def app_(self):
        """
        Test that content type is set appropriately based on Accept headers.
        """
        class RootController(object):

            @expose(content_type='text/html')
            @expose(content_type='application/json')
            def index(self, *args):
                return 'Foo'

        return TestApp(Pecan(RootController()))

    def test_missing_accept(self):
        r = self.app_.get('/', headers={
            'Accept': ''
        })
        assert r.status_int == 200
        assert r.content_type == 'text/html'

    def test_quality(self):
        r = self.app_.get('/', headers={
            'Accept': 'text/html,application/json;q=0.9,*/*;q=0.8'
        })
        assert r.status_int == 200
        assert r.content_type == 'text/html'

        r = self.app_.get('/', headers={
            'Accept': 'application/json,text/html;q=0.9,*/*;q=0.8'
        })
        assert r.status_int == 200
        assert r.content_type == 'application/json'

    def test_discarded_accept_parameters(self):
        r = self.app_.get('/', headers={
            'Accept': 'application/json;discard=me'
        })
        assert r.status_int == 200
        assert r.content_type == 'application/json'

    def test_file_extension_has_higher_precedence(self):
        r = self.app_.get('/index.html', headers={
            'Accept': 'application/json,text/html;q=0.9,*/*;q=0.8'
        })
        assert r.status_int == 200
        assert r.content_type == 'text/html'

    def test_not_acceptable(self):
        r = self.app_.get('/', headers={
            'Accept': 'application/xml',
        }, status=406)
        assert r.status_int == 406

    def test_accept_header_missing(self):
        r = self.app_.get('/')
        assert r.status_int == 200
        assert r.content_type == 'text/html'


class TestCanonicalRouting(PecanTestCase):

    @property
    def app_(self):
        class ArgSubController(object):
            @expose()
            def index(self, arg):
                return arg

        class AcceptController(object):
            @accept_noncanonical
            @expose()
            def index(self):
                return 'accept'

        class SubController(object):
            @expose()
            def index(self, **kw):
                return 'subindex'

        class RootController(object):
            @expose()
            def index(self):
                return 'index'

            sub = SubController()
            arg = ArgSubController()
            accept = AcceptController()

        return TestApp(Pecan(RootController()))

    def test_root(self):
        r = self.app_.get('/')
        assert r.status_int == 200
        assert b'index' in r.body

    def test_index(self):
        r = self.app_.get('/index')
        assert r.status_int == 200
        assert b'index' in r.body

    def test_broken_clients(self):
        # for broken clients
        r = self.app_.get('', status=302)
        assert r.status_int == 302
        assert r.location == 'http://localhost/'

    def test_sub_controller_with_trailing(self):
        r = self.app_.get('/sub/')
        assert r.status_int == 200
        assert b'subindex' in r.body

    def test_sub_controller_redirect(self):
        r = self.app_.get('/sub', status=302)
        assert r.status_int == 302
        assert r.location == 'http://localhost/sub/'

    def test_with_query_string(self):
        # try with query string
        r = self.app_.get('/sub?foo=bar', status=302)
        assert r.status_int == 302
        assert r.location == 'http://localhost/sub/?foo=bar'

    def test_posts_fail(self):
        try:
            self.app_.post('/sub', dict(foo=1))
            raise Exception("Post should fail")  # pragma: nocover
        except Exception as e:
            assert isinstance(e, RuntimeError)

    def test_with_args(self):
        r = self.app_.get('/arg/index/foo')
        assert r.status_int == 200
        assert r.body == b'foo'

    def test_accept_noncanonical(self):
        r = self.app_.get('/accept/')
        assert r.status_int == 200
        assert r.body == b'accept'

    def test_accept_noncanonical_no_trailing_slash(self):
        r = self.app_.get('/accept')
        assert r.status_int == 200
        assert r.body == b'accept'


class TestNonCanonical(PecanTestCase):

    @property
    def app_(self):
        class ArgSubController(object):
            @expose()
            def index(self, arg):
                return arg  # pragma: nocover

        class AcceptController(object):
            @accept_noncanonical
            @expose()
            def index(self):
                return 'accept'  # pragma: nocover

        class SubController(object):
            @expose()
            def index(self, **kw):
                return 'subindex'

        class RootController(object):
            @expose()
            def index(self):
                return 'index'

            sub = SubController()
            arg = ArgSubController()
            accept = AcceptController()

        return TestApp(Pecan(RootController(), force_canonical=False))

    def test_index(self):
        r = self.app_.get('/')
        assert r.status_int == 200
        assert b'index' in r.body

    def test_subcontroller(self):
        r = self.app_.get('/sub')
        assert r.status_int == 200
        assert b'subindex' in r.body

    def test_subcontroller_with_kwargs(self):
        r = self.app_.post('/sub', dict(foo=1))
        assert r.status_int == 200
        assert b'subindex' in r.body

    def test_sub_controller_with_trailing(self):
        r = self.app_.get('/sub/')
        assert r.status_int == 200
        assert b'subindex' in r.body

    def test_proxy(self):
        class RootController(object):
            @expose()
            def index(self):
                request.testing = True
                assert request.testing is True
                del request.testing
                assert hasattr(request, 'testing') is False
                return '/'

        app = TestApp(make_app(RootController(), debug=True))
        r = app.get('/')
        assert r.status_int == 200

    def test_app_wrap(self):
        class RootController(object):
            pass

        wrapped_apps = []

        def wrap(app):
            wrapped_apps.append(app)
            return app

        make_app(RootController(), wrap_app=wrap, debug=True)
        assert len(wrapped_apps) == 1


class TestLogging(PecanTestCase):

    def test_logging_setup(self):
        class RootController(object):
            @expose()
            def index(self):
                import logging
                logging.getLogger('pecantesting').info('HELLO WORLD')
                return "HELLO WORLD"

        f = StringIO()

        app = TestApp(make_app(RootController(), logging={
            'loggers': {
                'pecantesting': {
                    'level': 'INFO', 'handlers': ['memory']
                }
            },
            'handlers': {
                'memory': {
                    'level': 'INFO',
                    'class': 'logging.StreamHandler',
                    'stream': f
                }
            }
        }))

        app.get('/')
        assert f.getvalue() == 'HELLO WORLD\n'

    def test_logging_setup_with_config_obj(self):
        class RootController(object):
            @expose()
            def index(self):
                import logging
                logging.getLogger('pecantesting').info('HELLO WORLD')
                return "HELLO WORLD"

        f = StringIO()

        from pecan.configuration import conf_from_dict
        app = TestApp(make_app(RootController(), logging=conf_from_dict({
            'loggers': {
                'pecantesting': {
                    'level': 'INFO', 'handlers': ['memory']
                }
            },
            'handlers': {
                'memory': {
                    'level': 'INFO',
                    'class': 'logging.StreamHandler',
                    'stream': f
                }
            }
        })))

        app.get('/')
        assert f.getvalue() == 'HELLO WORLD\n'


class TestEngines(PecanTestCase):

    template_path = os.path.join(os.path.dirname(__file__), 'templates')

    @unittest.skipIf('genshi' not in builtin_renderers, 'Genshi not installed')
    def test_genshi(self):

        class RootController(object):
            @expose('genshi:genshi.html')
            def index(self, name='Jonathan'):
                return dict(name=name)

            @expose('genshi:genshi_bad.html')
            def badtemplate(self):
                return dict()

        app = TestApp(
            Pecan(RootController(), template_path=self.template_path)
        )
        r = app.get('/')
        assert r.status_int == 200
        assert b"<h1>Hello, Jonathan!</h1>" in r.body

        r = app.get('/index.html?name=World')
        assert r.status_int == 200
        assert b"<h1>Hello, World!</h1>" in r.body

        error_msg = None
        try:
            r = app.get('/badtemplate.html')
        except Exception as e:
            for error_f in error_formatters:
                error_msg = error_f(e)
                if error_msg:
                    break
        assert error_msg is not None

    @unittest.skipIf('kajiki' not in builtin_renderers, 'Kajiki not installed')
    def test_kajiki(self):

        class RootController(object):
            @expose('kajiki:kajiki.html')
            def index(self, name='Jonathan'):
                return dict(name=name)

        app = TestApp(
            Pecan(RootController(), template_path=self.template_path)
        )
        r = app.get('/')
        assert r.status_int == 200
        assert b"<h1>Hello, Jonathan!</h1>" in r.body

        r = app.get('/index.html?name=World')
        assert r.status_int == 200
        assert b"<h1>Hello, World!</h1>" in r.body

    @unittest.skipIf('jinja' not in builtin_renderers, 'Jinja not installed')
    def test_jinja(self):

        class RootController(object):
            @expose('jinja:jinja.html')
            def index(self, name='Jonathan'):
                return dict(name=name)

            @expose('jinja:jinja_bad.html')
            def badtemplate(self):
                return dict()

        app = TestApp(
            Pecan(RootController(), template_path=self.template_path)
        )
        r = app.get('/')
        assert r.status_int == 200
        assert b"<h1>Hello, Jonathan!</h1>" in r.body

        error_msg = None
        try:
            r = app.get('/badtemplate.html')
        except Exception as e:
            for error_f in error_formatters:
                error_msg = error_f(e)
                if error_msg:
                    break
        assert error_msg is not None

    @unittest.skipIf('mako' not in builtin_renderers, 'Mako not installed')
    def test_mako(self):

        class RootController(object):
            @expose('mako:mako.html')
            def index(self, name='Jonathan'):
                return dict(name=name)

            @expose('mako:mako_bad.html')
            def badtemplate(self):
                return dict()

        app = TestApp(
            Pecan(RootController(), template_path=self.template_path)
        )
        r = app.get('/')
        assert r.status_int == 200
        assert b"<h1>Hello, Jonathan!</h1>" in r.body

        r = app.get('/index.html?name=World')
        assert r.status_int == 200
        assert b"<h1>Hello, World!</h1>" in r.body

        error_msg = None
        try:
            r = app.get('/badtemplate.html')
        except Exception as e:
            for error_f in error_formatters:
                error_msg = error_f(e)
                if error_msg:
                    break
        assert error_msg is not None

    def test_renderer_not_found(self):

        class RootController(object):
            @expose('mako3:mako.html')
            def index(self, name='Jonathan'):
                return dict(name=name)

        app = TestApp(
            Pecan(RootController(), template_path=self.template_path)
        )
        try:
            r = app.get('/')
        except Exception as e:
            expected = e

        assert 'support for "mako3" was not found;' in str(expected)

    def test_json(self):
        expected_result = dict(
            name='Jonathan',
            age=30, nested=dict(works=True)
        )

        class RootController(object):
            @expose('json')
            def index(self):
                return expected_result

        app = TestApp(Pecan(RootController()))
        r = app.get('/')
        assert r.status_int == 200
        result = json.loads(r.body.decode())
        assert result == expected_result

    def test_custom_renderer(self):

        class RootController(object):
            @expose('backwards:mako.html')
            def index(self, name='Joe'):
                return dict(name=name)

        class BackwardsRenderer(MakoRenderer):
            # Custom renderer that reverses all string namespace values
            def render(self, template_path, namespace):
                namespace = dict(
                    (k, v[::-1])
                    for k, v in namespace.items()
                )
                return super(BackwardsRenderer, self).render(template_path,
                                                             namespace)

        app = TestApp(Pecan(
            RootController(),
            template_path=self.template_path,
            custom_renderers={'backwards': BackwardsRenderer}
        ))
        r = app.get('/')
        assert r.status_int == 200
        assert b"<h1>Hello, eoJ!</h1>" in r.body

        r = app.get('/index.html?name=Tim')
        assert r.status_int == 200
        assert b"<h1>Hello, miT!</h1>" in r.body

    def test_override_template(self):
        class RootController(object):
            @expose('foo.html')
            def index(self):
                override_template(None, content_type='text/plain')
                return 'Override'

        app = TestApp(Pecan(RootController()))
        r = app.get('/')
        assert r.status_int == 200
        assert b'Override' in r.body
        assert r.content_type == 'text/plain'

    def test_render(self):
        class RootController(object):
            @expose()
            def index(self, name='Jonathan'):
                return render('mako.html', dict(name=name))

        app = TestApp(
            Pecan(RootController(), template_path=self.template_path)
        )
        r = app.get('/')
        assert r.status_int == 200
        assert b"<h1>Hello, Jonathan!</h1>" in r.body

    def test_default_json_renderer(self):

        class RootController(object):
            @expose()
            def index(self, name='Bill'):
                return dict(name=name)

        app = TestApp(Pecan(RootController(), default_renderer='json'))
        r = app.get('/')
        assert r.status_int == 200
        result = dict(json.loads(r.body.decode()))
        assert result == {'name': 'Bill'}

    def test_default_json_renderer_with_explicit_content_type(self):

        class RootController(object):
            @expose(content_type='text/plain')
            def index(self, name='Bill'):
                return name

        app = TestApp(Pecan(RootController(), default_renderer='json'))
        r = app.get('/')
        assert r.status_int == 200
        assert r.body == b"Bill"


class TestDeprecatedRouteMethod(PecanTestCase):

    @property
    def app_(self):
        class RootController(object):

            @expose()
            def index(self, *args):
                return ', '.join(args)

            @expose()
            def _route(self, args):
                return self.index, args

        return TestApp(Pecan(RootController()))

    def test_required_argument(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            r = self.app_.get('/foo/bar/')
            assert r.status_int == 200
            assert b'foo, bar' in r.body


class TestExplicitRoute(PecanTestCase):

    def test_alternate_route(self):

        class RootController(object):

            @expose(route='some-path')
            def some_path(self):
                return 'Hello, World!'

        app = TestApp(Pecan(RootController()))

        r = app.get('/some-path/')
        assert r.status_int == 200
        assert r.body == b'Hello, World!'

        r = app.get('/some_path/', expect_errors=True)
        assert r.status_int == 404

    def test_manual_route(self):

        class SubController(object):

            @expose(route='some-path')
            def some_path(self):
                return 'Hello, World!'

        class RootController(object):
            pass

        route(RootController, 'some-controller', SubController())

        app = TestApp(Pecan(RootController()))

        r = app.get('/some-controller/some-path/')
        assert r.status_int == 200
        assert r.body == b'Hello, World!'

        r = app.get('/some-controller/some_path/', expect_errors=True)
        assert r.status_int == 404

    def test_manual_route_conflict(self):

        class SubController(object):
            pass

        class RootController(object):

            @expose()
            def hello(self):
                return 'Hello, World!'

        self.assertRaises(
            RuntimeError,
            route,
            RootController,
            'hello',
            SubController()
        )

    def test_custom_route_on_index(self):

        class RootController(object):

            @expose(route='some-path')
            def index(self):
                return 'Hello, World!'

        app = TestApp(Pecan(RootController()))

        r = app.get('/some-path/')
        assert r.status_int == 200
        assert r.body == b'Hello, World!'

        r = app.get('/')
        assert r.status_int == 200
        assert r.body == b'Hello, World!'

        r = app.get('/index/', expect_errors=True)
        assert r.status_int == 404

    def test_custom_route_with_attribute_conflict(self):

        class RootController(object):

            @expose(route='mock')
            def greet(self):
                return 'Hello, World!'

            @expose()
            def mock(self):
                return 'You are not worthy!'

        app = TestApp(Pecan(RootController()))

        self.assertRaises(
            RuntimeError,
            app.get,
            '/mock/'
        )

    def test_conflicting_custom_routes(self):

        class RootController(object):

            @expose(route='testing')
            def foo(self):
                return 'Foo!'

            @expose(route='testing')
            def bar(self):
                return 'Bar!'

        app = TestApp(Pecan(RootController()))

        self.assertRaises(
            RuntimeError,
            app.get,
            '/testing/'
        )

    def test_conflicting_custom_routes_in_subclass(self):

        class BaseController(object):

            @expose(route='testing')
            def foo(self):
                return request.path

        class ChildController(BaseController):
            pass

        class RootController(BaseController):
            child = ChildController()

        app = TestApp(Pecan(RootController()))

        r = app.get('/testing/')
        assert r.body == b'/testing/'

        r = app.get('/child/testing/')
        assert r.body == b'/child/testing/'

    def test_custom_route_prohibited_on_lookup(self):
        try:
            class RootController(object):

                @expose(route='some-path')
                def _lookup(self):
                    return 'Hello, World!'
        except ValueError:
            pass
        else:
            raise AssertionError(
                '_lookup cannot be used with a custom path segment'
            )

    def test_custom_route_prohibited_on_default(self):
        try:
            class RootController(object):

                @expose(route='some-path')
                def _default(self):
                    return 'Hello, World!'
        except ValueError:
            pass
        else:
            raise AssertionError(
                '_default cannot be used with a custom path segment'
            )

    def test_custom_route_prohibited_on_route(self):
        try:
            class RootController(object):

                @expose(route='some-path')
                def _route(self):
                    return 'Hello, World!'
        except ValueError:
            pass
        else:
            raise AssertionError(
                '_route cannot be used with a custom path segment'
            )

    def test_custom_route_with_generic_controllers(self):

        class RootController(object):

            @expose(route='some-path', generic=True)
            def foo(self):
                return 'Hello, World!'

            @foo.when(method='POST')
            def handle_post(self):
                return 'POST!'

        app = TestApp(Pecan(RootController()))

        r = app.get('/some-path/')
        assert r.status_int == 200
        assert r.body == b'Hello, World!'

        r = app.get('/foo/', expect_errors=True)
        assert r.status_int == 404

        r = app.post('/some-path/')
        assert r.status_int == 200
        assert r.body == b'POST!'

        r = app.post('/foo/', expect_errors=True)
        assert r.status_int == 404

    def test_custom_route_prohibited_on_generic_controllers(self):
        try:
            class RootController(object):

                @expose(generic=True)
                def foo(self):
                    return 'Hello, World!'

                @foo.when(method='POST', route='some-path')
                def handle_post(self):
                    return 'POST!'
        except ValueError:
            pass
        else:
            raise AssertionError(
                'generic controllers cannot be used with a custom path segment'
            )

    def test_invalid_route_arguments(self):
        class C(object):

            def secret(self):
                return {}

        self.assertRaises(TypeError, route)
        self.assertRaises(TypeError, route, 'some-path', lambda x: x)
        self.assertRaises(TypeError, route, 'some-path', C.secret)
        self.assertRaises(TypeError, route, C, {}, C())

        for path in (
            'VARIED-case-PATH',
            'this,custom,path',
            '123-path',
            'path(with-parens)',
            'path;with;semicolons',
            'path:with:colons',
            'v2.0',
            '~username',
            'somepath!',
            'four*four',
            'one+two',
            '@twitterhandle',
            'package=pecan'
        ):
            handler = C()
            route(C, path, handler)
            assert getattr(C, path, handler)

        self.assertRaises(ValueError, route, C, '/path/', C())
        self.assertRaises(ValueError, route, C, '.', C())
        self.assertRaises(ValueError, route, C, '..', C())
        self.assertRaises(ValueError, route, C, 'path?', C())
        self.assertRaises(ValueError, route, C, 'percent%20encoded', C())
