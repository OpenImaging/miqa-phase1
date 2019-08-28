#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

requirements = [
    'girder==3.0.3',
    'girder_jobs==3.0.3',
    'girder-autojoin==3.0.3'
]

setup(
    author_email='kitware@kitware.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    description='Server side functionality of MIQA',
    install_requires=requirements,
    license='Apache Software License 2.0',
    include_package_data=True,
    keywords='miqa',
    name='miqa_server',
    packages=find_packages(exclude=['test', 'test.*']),
    url='https://github.com/OpenImaging/miqa',
    version='0.3.3',
    zip_safe=False,
    entry_points={
        'girder.plugin': [
            'miqa_server = miqa_server:GirderPlugin'
        ]
    }
)
