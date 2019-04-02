import sys
import platform

from setuptools import setup, find_packages

version = '1.3.3'

#
# determine requirements
#
with open('requirements.txt') as reqs:
    requirements = [
        line for line in reqs.read().split('\n')
        if (line and not line.startswith('-'))
    ]

try:
    from functools import singledispatch  # noqa
except:
    #
    # This was introduced in Python 3.4 - the singledispatch package contains
    # a backported replacement for 2.6 through 3.4
    #
    requirements.append('singledispatch')
    try:
        from collections import OrderedDict
    except:
        requirements.append('ordereddict')


tests_require = requirements + [
    'virtualenv',
    'Jinja2',
    'gunicorn',
    'mock',
    'sqlalchemy'
]

if sys.version_info < (3, 0):
    # These don't support Python3 yet - don't run their tests
    if platform.python_implementation() != 'PyPy':
        # Kajiki is not pypy-compatible
        tests_require += ['Kajiki']
    tests_require += ['Genshi']
else:
    # Genshi added Python3 support in 0.7
    tests_require += ['Genshi>=0.7']

#
# call setup
#
setup(
    name='pecan',
    version=version,
    description="A WSGI object-dispatching web framework, designed to be "
                "lean and fast, with few dependencies.",
    long_description=None,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Software Development :: Libraries :: Application Frameworks'
    ],
    keywords='web framework wsgi object-dispatch http',
    author='Jonathan LaCour',
    author_email='info@pecanpy.org',
    url='http://github.com/pecan/pecan',
    license='BSD',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    scripts=['bin/pecan'],
    zip_safe=False,
    install_requires=requirements,
    tests_require=tests_require,
    test_suite='pecan',
    entry_points="""
    [pecan.command]
    serve = pecan.commands:ServeCommand
    shell = pecan.commands:ShellCommand
    create = pecan.commands:CreateCommand
    [pecan.scaffold]
    base = pecan.scaffolds:BaseScaffold
    rest-api = pecan.scaffolds:RestAPIScaffold
    [console_scripts]
    pecan = pecan.commands:CommandRunner.handle_command_line
    gunicorn_pecan = pecan.commands.serve:gunicorn_run
    """
)
