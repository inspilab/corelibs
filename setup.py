import os
from setuptools import setup
from distutils import util
from setuptools import setup, Extension, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()

setup(
    name='corelibs',
    version='1.0.0',
    packages=[
        'corelibs',
        'corelibs.pubsub',
    ],
    description='Core Libs',
    long_description=README,
    author='inspitrip',
    author_email='hai@inspitrip.com',
    url='git@github.com:inspilab/corelibs.git',
    license='MIT',
    install_requires=[
        'redis==3.2.1',
        'raven==6.9.0'
    ]
)
