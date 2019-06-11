# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

try:
    long_description = open("README.rst").read()
except IOError:
    long_description = ""

setup(
    name="facelesscloud",
    version="1.2.0",
    description="FacelessCloud is a client to spawn Instances/VM servers with cryptocurrency paiement method.",
    license="This is a free software. Anyone is free to copy, modify, publish, use, compile, sell or distribute this software. Do what ever the fuck you want.",
    author="Faceless Cloud",
    packages=find_packages(),
    long_description=long_description,
    url="https://github.com/facelesscloud/facelesscloud-python3-client.git",
    install_requires=[
        'requests>',
        'pyqrcode',
        'aaargh',
        'sshpubkeys',
        'simplejson'
    ],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    entry_points={
        'console_scripts': [
            'facelesscloud=facelesscloud.cli:main',
        ],
    }
)
