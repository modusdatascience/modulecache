from abc import ABCMeta, abstractmethod
from .base import ModuleCacheValid
from modulecache.base import nocache, path_of_caller
from toolz.functoolz import flip
import inspect

class ModuleCacheInvalidator(object):
    __metaclass__ = ABCMeta
    
    def __init__(self, backend):
        self.backend = backend
        self.backend.register(self)
    
    def __enter__(self):
        mymeta = self.backend.metadata
        moduledata = self.backend.moduledata
        self.check(mymeta, moduledata)
    
    def __exit__(self, exc_type, exc_value, exc_stacktrace):
        pass
    
    def check(self, metadata, moduledata):
        if metadata != nocache:
            self._check(metadata, moduledata)
    
    @abstractmethod
    def _check(self, metadata, moduledata):
        pass
    
    @abstractmethod
    def new_metadata(self, moduledata):
        pass
    
    def __and__(self, other):
        return AllInvalidator(self, other)
    
    def __or__(self, other):
        return AnyInvalidator(self, other)
    
    def __invert__(self):
        return NotInvalidator(self)
    
#     def _check(self, metadata, moduledata):
#         try:
#             mymeta = metadata[self.identity]
#         except KeyError:
#             raise ModuleCacheInvalid()
#         self._check(self, mymeta, moduledata)


class DerivedInvalidator(ModuleCacheInvalidator):
    pass
    
class MultipleDerivedInvalidator(DerivedInvalidator):
    def __init__(self, *invalidators):
        self.invalidators = invalidators
        
    def new_metadata(self, moduledata):
        return tuple([inv.new_metadata(moduledata) for inv in self.invalidators])
    
    def _member_check(self, invalidator, metadata, moduledata):
        '''Return True for valid and False for invalid'''
        try:
            invalidator.check(metadata, moduledata)
            result = False
        except ModuleCacheValid:
            result = True
        return result
    
    def _member_checks(self, metadata, moduledata):
        return tuple(map(flip(self._member_check)(moduledata), zip(metadata, self.invalidators)))

class SingleDerivedInvalidator(DerivedInvalidator):
    def __init__(self, invalidator):
        self.invalidator = invalidator
    
    def new_metadata(self, moduledata):
        return self.invalidator.new_metadata(moduledata)
    
class AllInvalidator(MultipleDerivedInvalidator):
    '''
    Cache is valid if and only if all members say it is valid.
    '''
    def _check(self, metadata, moduledata):
        if all(self._member_checks(metadata, moduledata)):
            raise ModuleCacheValid
    
    def __and__(self, other):
        if isinstance(other, AllInvalidator):
            return AllInvalidator(self.invalidators + other.invalidators)
        else:
            return NotImplemented

class AnyInvalidator(MultipleDerivedInvalidator):
    '''
    Cache is valid if and only if any member says it is valid.
    '''
    def _check(self, metadata, moduledata):
        if any(self._member_checks(metadata, moduledata)):
            raise ModuleCacheValid
    
    def __or__(self, other):
        if isinstance(other, AnyInvalidator):
            return AnyInvalidator(self.invalidators + other.invalidators)
        else:
            return NotImplemented
    
class NotInvalidator(SingleDerivedInvalidator):
    '''
    Cache is valid if and only if member says it is not valid.
    '''
    def _check(self, metadata, moduledata):
        try:
            self.invalidator._check(metadata, moduledata)
            raise ModuleCacheValid()
        except ModuleCacheValid:
            pass
    
    def __invert__(self):
        return self.invalidator
    
class AlwaysValid(ModuleCacheInvalidator):
    def _check(self, metadata, moduledata):
        raise ModuleCacheValid()
    
    def new_metadata(self, moduledata):
        pass

class VersioneerInvalidator(ModuleCacheInvalidator):
    '''
    Use versioneer version information to invalidate the cache.
    '''
    def __init__(self, backend, versioneer_info):
        ModuleCacheInvalidator.__init__(self, backend)
        self.versioneer_info = versioneer_info

    def _check(self, metadata, moduledata):
        if not self.versioneer_info['dirty'] and metadata['version'] == self.versioneer_info['version']:
            raise ModuleCacheValid()
    
    def new_metadata(self, moduledata):
        return self.versioneer_info

class ChangeInvalidator(ModuleCacheInvalidator):
    def _check(self, metadata, moduledata):
        contents = self.new_metadata(moduledata)
        if metadata == contents:
            raise ModuleCacheValid()
        
class FileChangeInvalidator(ChangeInvalidator):
    '''
    Invalidate the cache if the specified file has changed.  Stores the entire file as metadata.
    '''
    def __init__(self, backend, path=None):
        ModuleCacheInvalidator.__init__(self, backend)
        self.path = path #if path is not None else path_of_caller()
        
    def new_metadata(self, moduledata):
        with open(self.path, 'rb') as infile:
            contents = infile.read().encode('string_escape')
        return contents
