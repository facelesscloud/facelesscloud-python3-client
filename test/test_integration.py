#! /usr/bin/python3
# -*- coding: utf-8 -*-

""" Pytest integration. Pipeline """

from facelesscloud import cli

FAKE_BTC_ADDRESS = '1H3QWihcQVChHgNMwsVDt9aDnQoGa35xc2'
FAKE_SSHKEY_PATH = 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC7P45ptWquJeZpFQq1JK1NkKJQ0cxbG1pMndWpG11Oq/+KOcQxD/1+SF4V5LAWLR1soxbWBrLFbR9HuRRvirhA87pYrvxNMIoadRXcxDzj7itORLDliWq+UUpkHDWODXgY78MQ1MKxgZ6tj33Rd8da684Dd98Dd4ud1QTioOJea9HxO6x4x6mMPXgFhGxUXiGydE/RQOtYL1ToM3UWrH9/YsQ/IzIoXXG+Ar8K40unQiYEjp3GlJti7d74DZG5nlko3ek/cFyMbC91twv7QuaITmQhfog1HkA/THugphFGJ91BjJPcxPH4HLTKfytAb2GaLF8g0tnhqNAstzrIXVy1 bob@hellyeah'


def test_get_function():
    region = cli.api_get('region')
    assert region.get('status') is 200
    assert region.get('result')

    operating_system = cli.api_get('os')
    assert operating_system.get('status') is 200
    assert operating_system.get('result')

    flavor = cli.api_get('flavor')
    assert flavor.get('status') is 200
    assert flavor.get('result')


def test_sshkey():
    assert cli.validate_ssh_key(FAKE_SSHKEY_PATH)


def test_spawn():
    assert cli.spawn(configfile=None, time='24', flavor='201', operating_system='167', region='2', sshkey=None, kickstart=None, force=True, currency='litecoin')
