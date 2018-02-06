from abc import ABCMeta, abstractmethod
from modulecache.base import ModuleCacheValid, nocache
import pickle
import inspect
from toolz.dicttoolz import dissoc, valfilter, itemmap
from toolz.functoolz import complement, flip
from types import ModuleType
import traceback
from itertools import starmap

class ModuleCacheBackend(object):
    __metaclass__ = ABCMeta
    '''
    Every subclass has a way to store and retrieve metadata and moduledata objects.  The metadata object is a 
    dict where keys are invalidator identities and values are whatever information that invalidator needs to 
    determine if a cache is still valid.  The moduledata object is a dict where keys are variable names and values
    are variable values.  The moduledata will be used to construct the included variables from the cache in the 
    case that the cache is valid.  If the cache is invalid, a new cache will be created on exit.
    '''
    baseline_suppress = ['__builtins__', '__file__', '__package__', '__name__', '__doc__', ]
    def __init__(self, suppress=[]):
        self.user_suppress = list(suppress)
    
    @abstractmethod
    def _get_from_cache(self):
        '''
        Attempt to get metadata and moduledata from cache backend.  Return (nocache, {}) if no cache exists yet.
        '''
        pass
    
    @abstractmethod
    def _put_in_cache(self, metadata, moduledata):
        '''
        Write metadata and moduledata to cache backend.
        '''
        pass
    
    @abstractmethod
    def _check_cachability(self, name, obj):
        pass
    
    def __enter__(self):
        self._metadata, self._moduledata = self._get_from_cache()
        return self
    
    @property
    def suppress(self):
        return set(self.baseline_suppress + self.user_suppress)
    
    @property
    def metadata(self):
#         if self._metadata == nocache:
#             raise ModuleCacheInvalid()
        return self._metadata
    
    @property
    def moduledata(self):
        return self._moduledata
        
    def register(self, invalidator):
        self.invalidator = invalidator
        
    def __exit__(self, exc_type, exc_value, exc_traceback):
        if isinstance(exc_value, ModuleCacheValid) or \
            exc_type is ModuleCacheValid or \
            exc_value is ModuleCacheValid:
            inspect.stack()[1][0].f_globals.update(self.moduledata)
            return True
        elif exc_value is None:
            new_moduledata = valfilter(complement(flip(isinstance)(ModuleType)), 
                                       dissoc(inspect.stack()[1][0].f_globals, *self.suppress))
            
            # Check that all objects can be cached
            for _ in starmap(self._check_cachability, new_moduledata.items()): pass
            
            new_metadata = self.invalidator.new_metadata(new_moduledata)
            self._put_in_cache(new_metadata, new_moduledata)
            return True
        else:
            return False
            
class PickleBackend(ModuleCacheBackend):
    def __init__(self, filename, suppress=[], opener=open):
        self.filename = filename
        self.opener = opener
        ModuleCacheBackend.__init__(self, suppress)
        
    def _get_from_cache(self):
        try:
            with self.opener(self.filename, 'rb') as infile:
                metadata, moduledata = pickle.load(infile)
            return metadata, moduledata
        except (IOError, EOFError, ValueError):
            return nocache, {}
        
    def _put_in_cache(self, metadata, moduledata):
        with self.opener(self.filename, 'wb') as outfile:
            pickle.dump((metadata, moduledata), outfile)
        
    def _check_cachability(self, name, obj):
        try:
            pickle.dumps(obj)
        except:
            traceback.print_exc()
            raise TypeError('Variable %s containing object of type %s can\'t be pickled.' % (name, type(obj).__name__))
