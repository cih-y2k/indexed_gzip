#!/usr/bin/env python
#
# test_zran.py - Python wrapper around ctest_zran.pyx.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

from . import ctest_zran

def setup_module():         ctest_zran.setup_module()
def teardown_module():      ctest_zran.teardown_module()

def test_init():            ctest_zran.test_init()
def test_init_file_modes(): ctest_zran.test_init_file_modes()
def test_seek_and_tell():   ctest_zran.test_seek_and_tell()
