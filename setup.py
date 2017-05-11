#!/usr/bin/env python
import os
import sys
from setuptools import setup

if "publish" in sys.argv[-1]:
    os.system("python setup.py sdist upload")
    sys.exit()

# Load the __version__ variable without importing the package already
exec(open('busfactor/version.py').read())

entry_points = {'console_scripts': [
        'buss = busfactor.counter:main'
]}

setup(name='busfactor',
      version=__version__,
      description="busssss",
      long_description=open('README.md').read(),
      author='DPSHELIO',
      author_email='dpshelio@espana.es',
      license='MIT',
      packages=['busfactor'],
      install_requires=['matplotlib',
                        'astropy>=1.0',
                        'tqdm',
                        'GitPython'],
      entry_points=entry_points,
      include_package_data=True,
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Intended Audience :: Science/Research",
          "Topic :: Scientific/Engineering :: Astronomy",
          ],
    )
