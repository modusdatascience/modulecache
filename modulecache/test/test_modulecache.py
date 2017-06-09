import os
from modulecache.invalidators import VersioneerInvalidator
from nose.tools import assert_equal
from modulecache.base import containing_directory
from modulecache.backends import PickleBackend


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
    filename = os.path.join(containing_directory(), 'testcache.pkl')
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
        if os.path.exists('testcache.pkl'):
            os.remove('testcache.pkl')
        
if __name__ == '__main__': 
    import sys
    import nose
    module_name = sys.modules[__name__].__file__
    
    result = nose.run(argv=[sys.argv[0], 
                            module_name, 
                            '-s', '-v'])