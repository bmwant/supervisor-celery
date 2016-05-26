from setuptools import setup
from os import path
from sys import version_info

py_version = version_info[:2]

if py_version < (2, 6):
    raise RuntimeError(
        'On Python 2, supervisor-wildcards requires Python 2.6 or later')
elif (3, 0) < py_version < (3, 2):
    raise RuntimeError(
        'On Python 3, supervisor-wildcards requires Python 3.2 or later')

VERSION = (0, 1, 3)
__version__ = VERSION
__versionstr__ = '.'.join(map(str, VERSION))

long_description = ''
try:
    with open(path.join(path.dirname(__file__), 'README.rst')) as f:
        long_description = f.read().strip()
except Exception as e:
    pass


setup(
    name='supervisor-celery',
    version=__versionstr__,
    description="Implemenents start/stop/restart commands with both parallel and wildcard support for Supervisor.",
    url='http://github.com/bmwant/supervisor-celery',
    long_description=long_description,
    author='Misha Behersky',
    author_email='bmwant@gmail.com',
    license='MIT',
    packages=['supervisorcelery'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Intended Audience :: Developers",'
    ],
    test_suite='tests.run_tests.run_all',
)


