import inspect
import os


class ModuleCacheValid(Exception):
    '''
    Exception raised by invalidators to invalidate a module cache.
    '''

class NoCache(object):
    '''
    Signals that a cache does not exists
    '''
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return True
        else:
            return NotImplemented

nocache = NoCache()

def containing_directory():
    return os.path.abspath(os.path.dirname(inspect.stack()[1][0].f_globals['__file__']))

def path_of_caller():
    return os.path.abspath(inspect.stack()[1][0].f_globals['__file__'])