import os
from modulecache.invalidators import VersioneerInvalidator,\
    FileChangeInvalidator
from nose.tools import assert_equal
from modulecache.backends import PickleBackend
from modulecache.base import source_file_directory


def test_basic():
    '''
    The two modules share a cache which can never be invalidated.  Therefore, even though they define 
    different values in their source code, the second import simply imports the cache from the first 
    and the two values are the same.
    '''
    from .dummy_modules import module1
    from .dummy_modules import module2
    try:
        assert_equal(module1.value, module2.value)
    finally:
        if os.path.exists('testcache.pkl'):
            os.remove('testcache.pkl')

def test_versioneer():
    filename = os.path.join(source_file_directory(), 'testcache.pkl')
    suppress = list(globals().keys())
    try:
        with PickleBackend(filename, suppress) as cache,  \
            VersioneerInvalidator(cache, {'version':1, 'dirty':False}):
            value = 1
        with PickleBackend(filename, suppress) as cache,  \
            VersioneerInvalidator(cache, {'version':1, 'dirty':False}):
            value = 2
        assert_equal(value, 1)
        with PickleBackend(filename, suppress) as cache,  \
            VersioneerInvalidator(cache, {'version':2, 'dirty':False}):
            value = 2
        assert_equal(value, 2)
        with PickleBackend(filename, suppress) as cache,  \
            VersioneerInvalidator(cache, {'version':2, 'dirty':False}):
            value = 3
        assert_equal(value, 2)
        with PickleBackend(filename, suppress) as cache,  \
            VersioneerInvalidator(cache, {'version':2, 'dirty':True}):
            value = 3
        assert_equal(value, 3)
    finally:
        if os.path.exists(filename):
            os.remove(filename)

def test_file_change():
    cachefilename = os.path.join(source_file_directory(), 'testcache.pkl')
    path = 'testfilechange'
    suppress = list(globals().keys())
    try:
        with open(path, 'wt') as outfile:
            outfile.write('1')
        with PickleBackend(cachefilename, suppress) as cache, FileChangeInvalidator(cache, path):
            value = 'a'
        assert_equal(value, 'a')
        with PickleBackend(cachefilename, suppress) as cache, FileChangeInvalidator(cache, path):
            value = 'b'
        assert_equal(value, 'a')
        with open(path, 'wt') as outfile:
            outfile.write('2')
        with PickleBackend(cachefilename, suppress) as cache, FileChangeInvalidator(cache, path):
            value = 'b'
        assert_equal(value, 'b')
    finally:
        if os.path.exists(cachefilename):
            os.remove(cachefilename)
        if os.path.exists(path):
            os.remove(path)

if __name__ == '__main__': 
    import sys
    import nose
    module_name = sys.modules[__name__].__file__
    
    result = nose.run(argv=[sys.argv[0], 
                            module_name, 
                            '-s', '-v'])