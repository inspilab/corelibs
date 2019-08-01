import os
from setuptools import setup
from distutils import util
from setuptools import setup, Extension, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()

setup(
    name='corelibs',
    version='1.5.6',
    packages=[
        'corelibs',
        'corelibs.pubsub',
        'corelibs.auth',
        'corelibs.middleware',
        'corelibs.log',
        'corelibs.inspitrip',
        'corelibs.inspitrip.serializers',
        'corelibs.inspitrip.views',
        'corelibs.inspitrip.models',
        'corelibs.inspitrip.services',
        'corelibs.inspitrip.services.product',
        'corelibs.inspitrip.services.location',
        'corelibs.inspitrip.services.booking',

        'corelibs.payments',
        'corelibs.payments.bank',
        'corelibs.payments.paypal',
        'corelibs.payments.stripe',
        'corelibs.payments.payoo',
    ],
    description='Core Libs',
    long_description=README,
    author='inspitrip',
    author_email='hai@inspitrip.com',
    url='git@github.com:inspilab/corelibs.git',
    license='MIT',
    install_requires=[
        'redis==3.2.1',
        'google-cloud-pubsub==0.38.0',
        'djangorestframework==3.8.2'
    ]
)
