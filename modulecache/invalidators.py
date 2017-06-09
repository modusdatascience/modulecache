from abc import ABCMeta, abstractmethod
from .base import ModuleCacheValid
from modulecache.base import nocache

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
    
#     def _check(self, metadata, moduledata):
#         try:
#             mymeta = metadata[self.identity]
#         except KeyError:
#             raise ModuleCacheInvalid()
#         self._check(self, mymeta, moduledata)

class AlwaysValid(ModuleCacheInvalidator):
    def _check(self, metadata, moduledata):
        raise ModuleCacheValid()
    
    def new_metadata(self, moduledata):
        pass

class VersioneerInvalidator(ModuleCacheInvalidator):
    def __init__(self, backend, versioneer_info):
        ModuleCacheInvalidator.__init__(self, backend)
        self.versioneer_info = versioneer_info

    def _check(self, metadata, moduledata):
        if not self.versioneer_info['dirty'] and metadata['version'] == self.versioneer_info['version']:
            raise ModuleCacheValid()
    
    def new_metadata(self, moduledata):
        return self.versioneer_info
