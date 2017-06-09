import os


def test_basic():
    '''
    The two modules share a cache which can never be invalidated.  Therefore, even though they define 
    different values in their source code, the second import simply imports the cache from the first 
    and the two values are the same.
    '''
    from .dummy_modules import module1
    from .dummy_modules import module2
    try:
        assert module1.value == module2.value
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