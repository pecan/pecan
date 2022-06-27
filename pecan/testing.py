import os
from pecan import load_app


def load_test_app(config=None, **kwargs):
    """
    Used for functional tests where you need to test your
    literal application and its integration with the framework.

    :param config: Can be a dictionary containing configuration, a string which
                    represents a (relative) configuration filename or ``None``
                    which will fallback to get the ``PECAN_CONFIG`` env
                    variable.

    returns a pecan.Pecan WSGI application wrapped in a webtest.TestApp
    instance.

    ::
        app = load_test_app('path/to/some/config.py')

        resp = app.get('/path/to/some/resource').status_int
        assert resp.status_int == 200

        resp = app.post('/path/to/some/resource', params={'param': 'value'})
        assert resp.status_int == 302

    Alternatively you could call ``load_test_app`` with no parameters if the
    environment variable is set ::

        app = load_test_app()

        resp = app.get('/path/to/some/resource').status_int
        assert resp.status_int == 200
    """
    # Only import at runtime, since this is a relatively heavy-weight
    # dependency:
    from webtest import TestApp
    return TestApp(load_app(config, **kwargs))


def reset_global_config():
    """
    When tests alter application configurations they can get sticky and pollute
    other tests that might rely on a pristine configuration. This helper will
    reset the config by overwriting it with ``pecan.configuration.DEFAULT``.
    """
    from pecan import configuration
    configuration.set_config(
        dict(configuration.initconf()),
        overwrite=True
    )
    os.environ.pop('PECAN_CONFIG', None)
