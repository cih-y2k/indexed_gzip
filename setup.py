#!/usr/bin/env python
"""Setup script for indexed_gzip.

If an environment variable called `INDEXED_GZIP_TESTING` is defined, the
Cython modules are compiled with line-tracing enabled, via the Cython
`linetrace` directive, and the `CYTHON_TRACE_NOGIL` macro.

See
https://cython.readthedocs.io/en/latest/src/reference/compilation.html#compiler-directives
for more details.
"""

import sys
import os
import glob
import os.path as op
import shutil

from setuptools import setup
from setuptools import Extension
from setuptools import Command


# Custom 'clean' command
class Clean(Command):

    user_options = []

    def initialize_options(self):
        pass
    def finalize_options(self):
        pass

    def run(self):

        base    = op.dirname(__file__)
        igzbase = op.join(base, 'indexed_gzip')

        shutil.rmtree(op.join(base, 'build'),
                      ignore_errors=True)
        shutil.rmtree(op.join(base, 'dist'),
                      ignore_errors=True)
        shutil.rmtree(op.join(base, 'indexed_gzip.egg-info'),
                      ignore_errors=True)
        shutil.rmtree(op.join(base, '.eggs'),
                      ignore_errors=True)
        shutil.rmtree(op.join(base, '__pycache__'),
                      ignore_errors=True)
        shutil.rmtree(op.join(igzbase, '__pycache__'),
                      ignore_errors=True)
        shutil.rmtree(op.join(igzbase, 'tests', '__pycache__'),
                      ignore_errors=True)

        files = [
            '*.so',
            '.coverage.*',
            op.join(igzbase, 'indexed_gzip.c'),
            op.join(igzbase, '*.pyc'),
            op.join(igzbase, '*.so'),
            op.join(igzbase, 'tests', '*.so'),
            op.join(igzbase, 'tests', '*.pyc'),
            op.join(igzbase, 'tests', 'ctest_zran.c'),
            op.join(igzbase, 'tests', 'ctest_indexed_gzip.c')]

        for f in files:
            for g in glob.glob(f):
                try:            os.remove(g)
                except OSError: pass


with open(op.join(op.dirname(__file__), 'README.md'), 'rt') as f:
    readme = f.read().strip()


# Platform information
python2 = sys.version_info[0] == 2
noc99   = python2 or (sys.version_info[0] == 3 and sys.version_info[1] <= 4)
windows = sys.platform.startswith("win")
testing = 'INDEXED_GZIP_TESTING' in os.environ


# If cython is present, we'll compile
# the pyx files from scratch. Otherwise,
# we'll compile the pre-generated c
# files (which are assumed to be present).
have_cython = True
have_numpy  = True

try:
    from Cython.Build import cythonize
except Exception:
    have_cython = False

# We need numpy to compile the test modules
try:
    import numpy as np
except Exception:
    have_numpy = False

# compile flags
include_dirs = ['indexed_gzip']
lib_dirs = []
libs = []
extra_compile_args = []
compiler_directives = {}
define_macros = []

# If numpy is present, we need
# to include the headers
if have_numpy:
    include_dirs.append(np.get_include())

if windows:
    ZLIB_HOME = os.environ.get("ZLIB_HOME", "c:/Program Files (x86)/GnuWin32")
    include_dirs.append(os.path.join(ZLIB_HOME, "include"))
    libs.append('zlib')
    lib_dirs.append(os.path.join(ZLIB_HOME, "lib"))

    # For stdint.h which is not included in the old Visual C
    # compiler used for Python 2
    if python2:
        include_dirs.append('compat')

    # Some C functions might not be present when compiling against
    # older versions of python
    if noc99:
        extra_compile_args += ['-DNO_C99']
else:
    libs.append('z')
    extra_compile_args += ['-Wall', '-pedantic', '-Wno-unused-function']

if testing:
    compiler_directives['linetrace'] = True
    define_macros += [('CYTHON_TRACE_NOGIL', '1')]

# Compile from cython files if
# possible, or compile from c.
if have_cython: pyx_ext = 'pyx'
else:           pyx_ext = 'c'

# The indexed_gzip module
igzip_ext = Extension(
    'indexed_gzip.indexed_gzip',
    [op.join('indexed_gzip', 'indexed_gzip.{}'.format(pyx_ext)),
     op.join('indexed_gzip', 'zran.c')],
    libraries=libs,
    library_dirs=lib_dirs,
    include_dirs=include_dirs,
    extra_compile_args=extra_compile_args,
    define_macros=define_macros)

# Optional test modules
test_exts = [
    Extension(
        'indexed_gzip.tests.ctest_indexed_gzip',
        [op.join('indexed_gzip', 'tests',
                 'ctest_indexed_gzip.{}'.format(pyx_ext))],
        libraries=libs,
        library_dirs=lib_dirs,
        include_dirs=include_dirs,
        extra_compile_args=extra_compile_args,
        define_macros=define_macros)
]

if not windows:
    # Uses POSIX memmap API so won't work on Windows
    test_exts.append(Extension(
        'indexed_gzip.tests.ctest_zran',
        [op.join('indexed_gzip', 'tests', 'ctest_zran.{}'.format(pyx_ext)),
         op.join('indexed_gzip', 'zran.c')],
        libraries=libs,
        library_dirs=lib_dirs,
        include_dirs=include_dirs,
        extra_compile_args=extra_compile_args,
        define_macros=define_macros))

# If we have numpy, we can compile the tests
if have_numpy: extensions = [igzip_ext] + test_exts
else:          extensions = [igzip_ext]


# Cythonize if we can
if have_cython:
    extensions = cythonize(extensions, compiler_directives=compiler_directives)


# find the version number
def readVersion():
    version  = {}
    initfile = op.join(op.dirname(__file__), 'indexed_gzip', '__init__.py')
    with open(initfile, 'rt') as f:
        for line in f:
            if line.startswith('__version__'):
                exec(line, version)
                break
    return version.get('__version__')


setup(
    name='indexed_gzip',
    packages=['indexed_gzip', 'indexed_gzip.tests'],
    version=readVersion(),
    author='Paul McCarthy',
    author_email='pauldmccarthy@gmail.com',
    description='Fast random access of gzip files in Python',
    long_description=readme,
    url='https://github.com/pauldmccarthy/indexed_gzip',
    license='zlib',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: zlib/libpng License',
        'Programming Language :: C',
        'Programming Language :: Cython',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: System :: Archiving :: Compression',
    ],

    cmdclass={'clean' : Clean},

    ext_modules=extensions,

    tests_require=['pytest', 'numpy', 'coverage', 'pytest-cov'],
    test_suite='tests',
)
