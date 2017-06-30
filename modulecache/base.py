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

def source_file_path(level=1):
    modpath = inspect.stack()[level][0].f_globals['__file__']

    # Turn pyc files into py files if we can
    if modpath.endswith('.pyc') and os.path.exists(modpath[:-1]):
        modpath = modpath[:-1]
    
    # Sort out symlinks
    modpath = os.path.realpath(modpath)
    return modpath

def source_file_directory(level=1):
    return os.path.abspath(os.path.dirname(source_file_path(level+1)))
    