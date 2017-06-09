import os
from modulecache.invalidators import FileChangeInvalidator
from modulecache.backends import PickleBackend

# Define a recursive fibonacci function, like in school
def fib(n):
    if n == 1:
        return 1
    if n == 2:
        return 1
    else:
        return fib(n-1) + fib(n-2)

# The cache_filename will determine the storage location for the cache
cache_filename = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fibonacci_cache.pkl')

# Variables with names in suppress will not be cached
suppress = globals().keys()

# Create a "with" context to cache the objects created within.  If the cache is valid, the code within will 
# be skipped and the objects will instead be loaded from the cache.
with PickleBackend(cache_filename, suppress) as cache, FileChangeInvalidator(cache, os.path.abspath(__file__)):
    # Create a dictionary of the first 40 fibonacci numbers for some reason.  Print each number.
    # The first time this module is imported this code will run and the fibonacci numbers will print.  
    # As long as this file isn't changed, this code will not be run on subsequent imports.  However, the 
    # fib_dict dictionary will still be available, as it will be loaded from the cache stored in the
    # fibonacci_cache.pkl file.
    fib_dict = {}
    for n in range(1, 41):
        f = fib(n)
        print 'fib(%d) = %d' % (n, f)
        fib_dict[n] = f
    # I don't need f to be available when this module is imported, so delete it.
    del f

