1.3.3
=====
* fixed a bug in RestController that incorrectly routed certain @secure
  requests (https://github.com/pecan/pecan/pull/105)
* removed official support for Python 3.3

1.3.2
=====
* pecan now works with webob < and > 1.8
  (https://github.com/pecan/pecan/pull/99)

1.3.1
=====
* pinned webob to <1.8 due to breaking changes in Accept header parsing
  (https://github.com/pecan/pecan/pull/97)
  (https://github.com/Pylons/webob/pull/338)

1.3.0
=====
* pecan is now officially supported for Python 3.6
* pecan is no longer supported for Python 2.6

1.2.1
=====
* Reverts a stable API change/regression (in the 1.2 release)
  (https://github.com/pecan/pecan/issues/72).  This change will re-released in
  a future major version upgrade.

1.2
===
* Added a better error message when an invalid template renderer is specified
  in `pecan.expose()` (https://github.com/pecan/pecan/issues/81).
* Pecan controllers that return `None` are now treated as an `HTTP 204 No
  Content` (https://github.com/pecan/pecan/issues/72).
* The `method` argument to `pecan.expose()` for generic controllers is no
  longer optional (https://github.com/pecan/pecan/pull/77).

1.1.2
=====
* Fixed a bug where JSON-formatted HTTP response bodies were not making
  use of pecan's JSON type registration functionality
  (http://pecan.readthedocs.io/en/latest/jsonify.html)
  (https://github.com/pecan/pecan/issues/68).
* Updated code and documentation examples to support readthedoc's move from
  `readthedocs.org` to `readthedocs.io`.

1.1.1
=====
* Pecan now officially supports Python 3.5.
* Pecan now uses `inspect.signature` instead of `inspect.getargspec` in
  Python 3.5 and higher (because `inspect.getargspec` is deprecated in these
  versions of Python 3).
* Fixed a bug that caused "after" hooks to run multiple times when
  `pecan.redirect(..., internal=True)` was used
  (https://github.com/pecan/pecan/issues/58).

1.1.0
=====
* `pecan.middleware.debug.DebugMiddleware` now logs exceptions at the ERROR
  level (https://github.com/pecan/pecan/pull/56).
* Fix a Javascript bug in the default project scaffold
  (https://github.com/pecan/pecan/pull/55).

1.0.5
=====
* Fix a bug in controller argspec detection when class-based decorators are
  used (https://github.com/pecan/pecan/issues/47).

1.0.4
=====
* Removed an open file handle leak when pecan renders errors for Jinja2 and
  Genshi templates (https://github.com/pecan/pecan/issues/30).
* Resolved a bug which caused log output to be duplicated in projects created
  with `pecan create` (https://github.com/pecan/pecan/issues/39).

1.0.3
=====
* Fixed a bug in `pecan.hooks.HookController` for newer versions of Python3.4
  (https://github.com/pecan/pecan/issues/19).

1.0.2
=====
* Fixed an edge case in `pecan.util.getargspec` that caused the incorrect
  argspec to be returned in certain situations when using Python 2.6.
* Added a `threading.lock` to the file system monitoring in `pecan serve
  --reload` to avoid extraneous server reloads.

1.0.1
====
* Fixed a bug wherein the file extension for URLs with a trailing slash
  (`file.html` vs `file.html/`) were not correctly guessed, thus resulting in
  incorrect Content-Type headers.
* Fixed a subtle bug in `pecan.config.Configuration` attribute/item assignment
  that caused some types of configuration changes to silently fail.

1.0.0
=====
* Replaced pecan's debugger middleware with an (optional) dependency on the
  `backlash` package.  Developers who want to debug application-level
  tracebacks interactively should `pip install backlash` in their development
  environment.
* Fixed a Content-Type related bug: when an explicit content_type is specified
  as an argument to `pecan.expose()`, it is now given precedence over the
  application-level default renderer.
* Fixed a bug that prevented the usage of certain RFC3986-specified characters
  in path segments.
* Fixed a bug in `pecan.abort` which suppressed the original traceback (and
  prevented monitoring tools like NewRelic from working as effectively).

0.9.0
=====
* Support for Python 3.2 has been dropped.
* Added a new feature which allows users to specify custom path segments for
  controllers.  This is especially useful for path segments that are not
  valid Python identifiers (such as path segments that include certain
  punctuation characters, like `/some/~path~/`).
* Added a new configuration option, `app.debugger`, which allows developers to
  specify an alternative debugger to `pdb` (e.g., `ipdb`) when performing
  interactive debugging with pecan's `DebugMiddleware`.
* Changed new quickstart pecan projects to default the `pecan` log level to
  `DEBUG` for development.
* Fixed a bug that prevented `staticmethods` from being used as controllers.
* Fixed a decoding bug in the way pecan handles certain quoted URL path
  segments and query strings.
* Fixed several bugs in the way pecan handles Unicode path segments (for
  example, now you can define pecan routes that contain emoji characters).
* Fixed several bugs in RestController that caused it to return `HTTP 404 Not
  Found` rather than `HTTP 405 Method Not Allowed`.  Additionally,
  RestController now returns valid `Allow` headers when `HTTP 405 Method Not
  Allowed` is returned.
* Fixed a bug which allowed special pecan methods (`_route`, `_lookup`,
  `_default`) to be marked as generic REST methods.
* Added more emphasis in pecan's documentation to the need for `debug=False` in
  production deployments.

0.8.3
=====
* Changed pecan to more gracefully handle a few odd request encoding edge
  cases.  Now pecan applications respond with an HTTP 400 (rather than an
  uncaught UnicodeDecodeError, resulting in an HTTP 500) when:
    - HTTP POST requests are composed of non-Unicode data
    - Request paths contain invalid percent-encoded characters, e.g.,
      ``/some/path/%aa/``
* Improved verbosity for import-related errors in pecan configuration files,
  especially those involving relative imports.

0.8.2
=====
* Fixes a bug that breaks support for multi-value query string variables (e.g.,
  `?check=a&check=b`).

0.8.1
=====
* Improved detection of infinite recursion for PecanHook and pypy.  This fixes
  a bug discovered in pecan + pypy that could result in infinite recursion when
  using the PecanHook metaclass.
* Fixed a bug that prevented @exposed controllers from using @staticmethod.
* Fixed a minor bug in the controller argument calculation.

0.8.0
=====
 * For HTTP POSTs, map JSON request bodies to controller keyword arguments.
 * Improved argspec detection and leniency for wrapped controllers.
 * When path arguments are incorrect for RestController, return HTTP 404, not 400.
 * When detecting non-content for HTTP 204, properly catch UnicodeDecodeError.
 * Fixed a routing bug for generic subcontrollers.
 * Fixed a bug in generic function handling when context locals are disabled.
 * Fixed a bug that mixes up argument order for generic functions.
 * Removed `assert` for flow control; it can be optimized away with `python -O`.

0.7.0
=====
* Fixed an edge case in RestController routing which should have returned an
  HTTP 400 but was instead raising an exception (and thus, HTTP 500).
* Fixed an incorrect root logger configuration for quickstarted pecan projects.
* Added `pecan.state.arguments`, a new feature for inspecting controller call
  arguments.
* Fixed an infinite recursion error in PecanHook application.  Subclassing both
  `rest.RestController` and `hooks.HookController` resulted in an infinite
  recursion error in hook application (which prevented applications from
  starting).
* Pecan's tests are now included in its source distribution.

0.6.1
=====
* Fixed a bug which causes pecan to mistakenly return HTTP 204 for non-empty
  response bodies.

0.6.0
=====
* Added support for disabling the `pecan.request` and `pecan.response`
  threadlocals at the WSGI application level in favor of explicit reference
  passing.  For more information, see :ref:`contextlocals`.
* Added better support for hook composition via subclassing and mixins.  For
  more information, see :ref:`attaching_hooks`.
* Added support for specifying custom request and response implementations at
  the WSGI application level for people who want to extend the functionality
  provided by the base classes in `webob`.
* Pecan controllers may now return an explicit `webob.Response` instance to
  short-circuit Pecan's template rendering and serialization.
* For generic methods that return HTTP 405, pecan now generates an `Allow`
  header to communicate acceptable methods to the client.
* Fixed a bug in adherence to RFC2616: if an exposed method returns no response
  body (or namespace), pecan will now enforce an HTTP 204 response (instead of
  HTTP 200).
* Fixed a bug in adherence to RFC2616: when pecan responds with HTTP 204 or
  HTTP 304, the `Content-Type` header is automatically stripped (because these
  types of HTTP responses do not contain body content).
* Fixed a bug: now when clients request JSON via an `Accept` header, `webob`
  HTTP exceptions are serialized as JSON, not their native HTML representation.
* Fixed a bug that broke applications which specified `default_renderer
  = json`.

0.5.0
=====
* This release adds formal support for pypy.
* Added colored request logging to the `pecan serve` command.
* Added a scaffold for easily generating a basic REST API.
* Added the ability to pass arbitrary keyword arguments to
  `pecan.testing.load_test_app`.
* Fixed a recursion-related bug in the error document middleware.
* Fixed a bug in the `gunicorn_pecan` command that caused `threading.local`
  data to leak between eventlet/gevent green threads.
* Improved documentation through fixes and narrative tutorials for sample pecan
  applications.

0.4.5
=====
* Fixed a trailing slash bug for `RestController`s that have a `_lookup` method.
* Cleaned up the WSGI app reference from the threadlocal state on every request
  (to avoid potential memory leaks, especially when testing).
* Improved pecan documentation and corrected intersphinx references.
* pecan supports Python 3.4.

0.4.4
=====
* Removed memoization of certain controller attributes, which can lead to
  a memory leak in dynamic controller lookups.

0.4.3
=====
* Fixed several bugs for RestController.
* Fixed a bug in security handling for generic controllers.
* Resolved a bug in `_default` handlers used in `RestController`.
* Persist `pecan.request.context` across internal redirects.

0.4.2
=====
* Remove a routing optimization that breaks the WSME pecan plugin.

0.4.1
=====
* Moved the project to `StackForge infrastructure
  <http://docs.openstack.org/infra/system-config/stackforge.html>`_, including Gerrit code review,
  Jenkins continuous integration, and GitHub mirroring.
* Added a pecan plugin for the popular `uwsgi server
  <https://uwsgi-docs.readthedocs.io>`_.
* Replaced the ``simplegeneric`` dependency with the new
  ``functools.singledispatch`` function in preparation for  Python 3.4 support.
* Optimized pecan's core dispatch routing for notably faster response times.

0.3.2
=====
* Made some changes to simplify how ``pecan.conf.app`` is passed to new apps.
* Fixed a routing bug for certain ``_lookup`` controller configurations.
* Improved documentation for handling file uploads.
* Deprecated the ``pecan.conf.requestviewer`` configuration option.

0.3.1
=====
* ``on_error`` hooks can now return a Pecan Response objects.
* Minor documentation and release tooling updates.

0.3.0
=====
* Pecan now supports Python 2.6, 2.7, 3.2, and 3.3.

0.2.4
=====
* Add support for ``_lookup`` methods as a fallback in RestController.
* A variety of improvements to project documentation.

0.2.3
=====
* Add a variety of optimizations to ``pecan.core`` that improve request
  handling time by approximately 30% for simple object dispatch routing.
* Store exceptions raised by ``abort`` in the WSGI environ so they can be
  accessed later in the request handling (e.g., by other middleware or pecan
  hooks).
* Make TransactionHook more robust so that it isn't as susceptible to failure
  when exceptions occur in *other* pecan hooks within a request.
* Rearrange quickstart verbiage so users don't miss a necessary step.

0.2.2
=====
* Unobfuscate syntax highlighting JavaScript for debian packaging.
* Extract the scaffold-building tests into tox.
* Add support for specifying a pecan configuration file via the
  ``PECAN_CONFIG``
  environment variable.
* Fix a bug in ``DELETE`` methods in two (or more) nested ``RestControllers``.
* Add documentation for returning specific HTTP status codes.

0.2.1
=====

* Include a license, readme, and ``requirements.txt`` in distributions.
* Improve inspection with ``dir()`` for ``pecan.request`` and ``pecan.response``
* Fix a bug which prevented pecan applications from being mounted at WSGI
  virtual paths.

0.2.0
=====

* Update base project scaffolding tests to be more repeatable.
* Add an application-level configuration option to disable content-type guessing by URL
* Fix the wrong test dependency on Jinja, it's Jinja2.
* Fix a routing-related bug in ``RestController``.  Fixes #156
* Add an explicit ``CONTRIBUTING.rst`` document.
* Improve visibility of deployment-related docs.
* Add support for a ``gunicorn_pecan`` console script.
* Remove and annotate a few unused (and py26 alternative) imports.
* Bug fix: don't strip a dotted extension from the path unless it has a matching mimetype.
* Add a test to the scaffold project buildout that ensures pep8 passes.
* Fix misleading output for ``$ pecan --version``.

0.2.0b
======

* Fix a bug in ``SecureController``.  Resolves #131.
* Extract debug middleware static file dependencies into physical files.
* Improve a test that can fail due to a race condition.
* Improve documentation about configation format and ``app.py``.
* Add support for content type detection via HTTP Accept headers.
* Correct source installation instructions in ``README``.
* Fix an incorrect code example in the Hooks documentation.
* docs: Fix minor typo in ``*args`` Routing example.
