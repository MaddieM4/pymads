#!/usr/bin/env python
# -*- mode: python; sh-basic-offset: 4; indent-tabs-mode: nil; coding: utf-8 -*-
# vim: tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8
#
# pymds setup script
# Copyright 2010, Jorge A Gallegos <kad@blegh.net>

import setuptools

setuptools.setup (
    name = 'pymads',
    version = '0.5',
    packages = [
        'pymads',
        'pymads.filters',
        'pymads.sources',
    ]
    zip_safe = True,
    entry_points = {
        'console_scripts': [
            'pymads = pymads.pymads:main',
        ],
    },
    author = 'Philip Horger',
    description = 'A fork of the pymds authoritative DNS server, designed for asynchronous lookup without domain restrictions.',
    license = 'MIT',
    keywords = 'dns authoritativednsserver geodns dnsloadbalancer',
    url = 'https://github.com/campadrenalin/pymads',
)
