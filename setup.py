#!/usr/bin/env python

# Try catkin install
try:
   from catkin_pkg.python_setup import generate_distutils_setup
   from distutils.core import setup

   from setuptools.command.install import install as _install

   from pathlib import Path


   with open(f'{Path(__file__).parent}/requirements.txt', 'r') as f:
      pip_dependencies = f.readlines()


   d = generate_distutils_setup(
      packages=['roebots'],
      package_dir={'': 'src'}
   )

   d.update({'install_requires': pip_dependencies})

   setup(**d)
except ModuleNotFoundError:
   from pathlib    import Path
   from setuptools import setup, find_packages

   with open(f'{Path(__file__).parent}/requirements.txt', 'r') as f:
      pip_dependencies = f.readlines()

   setup(
      name='roebots',
      version='0.1.0',
      author='Adrian Röfer',
      author_email='aroefer@cs.uni-freiburg.de',
      packages=['roebots'],
      package_dir={'': 'src'},
      # scripts=['bin/script1','bin/script2'],
      url='http://pypi.python.org/pypi/roebots/',
      license='LICENSE',
      description="Adrian Röfer's convenience tools for doing robotics.",
      # long_description=open('README.txt').read(),
      install_requires=pip_dependencies
   )
