from setuptools import setup, find_packages

version = '1.7.0'

#
# determine requirements
#
with open('requirements.txt') as reqs:
    requirements = [
        line for line in reqs.read().split('\n')
        if (line and not line.startswith('-'))
    ]

with open('test-requirements.txt') as reqs:
    test_requirements = [
        line for line in reqs.read().split('\n')
        if (line and not line.startswith('-'))
    ]

tests_require = requirements + test_requirements


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
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
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
    zip_safe=False,
    python_requires='>=3.8',
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
