Pecan
=====

A WSGI object-dispatching web framework, designed to be lean and fast with few
dependencies.

.. image:: https://badge.fury.io/py/pecan.png
    :target: https://pypi.python.org/pypi/pecan/
    :alt: Latest PyPI version

Installing
----------

::

    $ pip install pecan

...or, for the latest (unstable) tip::

    $ git clone https://github.com/pecan/pecan.git
    $ cd pecan && python setup.py install

Running Tests
-------------

::

    $ python setup.py test

...or, to run all tests across all supported environments::

    $ pip install tox && tox

Viewing Documentation
---------------------
`Available online <https://pecan.readthedocs.io>`_, or to build manually::

    $ cd docs && make html
    $ open docs/build/html/index.html

...or::

    $ cd docs && make man
    $ man docs/build/man/pecan.1

Contributing
------------
For information on contributing to Pecan, please read our `Contributing
Guidelines <https://github.com/pecan/pecan/blob/master/CONTRIBUTING.rst>`_.

Bugs should be reported at:

https://github.com/pecan/pecan/issues/new

Additional Help/Support
-----------------------
Most Pecan interaction is done via the `pecan-dev Mailing List
<https://groups.google.com/forum/#!forum/pecan-dev>`_ and the #pecanpy channel
on `FreeNode <http://freenode.net/>`_ IRC.
