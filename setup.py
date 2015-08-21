#!/usr/bin/env python3
"""Planningpoker project setup."""
import os
from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()

REQUIREMENTS = [
    'aiohttp==0.17.0',
    'aiohttp-session==0.1.2',
    'aiohttp_session[pycrypto]',
]

TEST_REQUIREMENTS = [
    'pylama==6.3.4',
    'pytest==2.7.2',
    'requests==2.7.0',  # A synchronous HTTP client to use in tests.
    'mirakuru==0.5.0',  # Process executor.
]

setup(
    name='planningpoker',
    version='0.0.1',
    description='Planning poker web application',
    long_description=README,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: aiohttp',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='planning poker web app',
    author='Michał Pawłowski',
    author_email='@'.join(['unittestablecode', 'gmail.com']),
    license='MIT',
    packages=find_packages(exclude=['test']),
    install_requires=REQUIREMENTS,
    tests_require=TEST_REQUIREMENTS,
    extras_require={'tests': TEST_REQUIREMENTS},
    cmdclass={},
    entry_points={}
)
