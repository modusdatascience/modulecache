from setuptools import setup, find_packages
import versioneer


setup(name='modulecache',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description='Tools for caching modules for speedier imports',
      author='Jason Rudy',
      author_email='jcrudy@gmail.com',
      url='https://github.com/jcrudy/modulecache',
      packages=find_packages(),
      install_requires=['toolz'],
      tests_require=['nose']
     )