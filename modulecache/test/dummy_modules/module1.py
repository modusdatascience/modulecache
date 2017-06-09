from modulecache.backends import PickleBackend
from modulecache.invalidators import AlwaysValid
from modulecache.base import containing_directory
import os

with PickleBackend(os.path.join(containing_directory(), 'testcache.pkl')) as cache, AlwaysValid(cache):
    value = 1
