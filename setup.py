#!/usr/bin/env python

import setuptools

setuptools.setup (
    name = 'pymads',
    version = '0.5',
    packages = [
        'pymads',
        'pymads.filters',
        'pymads.sources',
        'pymads.tests',
    ],
    zip_safe = True,
    entry_points = {
        'console_scripts': [
            'pymads = pymads.pymads:main',
        ],
    },
    maintainer  = 'Philip Horger',
    maintainer_email = 'philip@roaming-initiative.com',
    description = 'A fork of the pymds authoritative DNS server, designed for asynchronous lookup without domain restrictions.',
    license = 'LGPL',
    keywords = 'dns authoritativednsserver geodns dnsloadbalancer',
    url = 'https://github.com/campadrenalin/pymads',
)
