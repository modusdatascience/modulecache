from modulecache.backends import PickleBackend
from modulecache.invalidators import AlwaysValid
from modulecache.base import source_file_directory
import os

with PickleBackend(os.path.join(source_file_directory(), 'testcache.pkl')) as cache, AlwaysValid(cache):
    value = 2
