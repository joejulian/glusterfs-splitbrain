import os
from setuptools import setup, find_packages

def read(fname):
  return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "splitmount",
    version = "0.0.1",
    author = "Joe Julian",
    author_email = "me@joejulian.name",
    description = ( "Admin tool to aid in the recovery of split-brain file entries in GlusterFS" ),
    license = "GPLv3",
    keywords = "gluster glusterfs split brain split-brain heal",
    url = "https://github.com/joejulian/glusterfs-splitbrain",
    long_description = read('README.md'),
    classifiers=[
      "Development Status :: 3 - Alpha",
      "Intended Audience :: System Administrators",
      "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
      "Topic :: Utilities",
      ],
    entry_points = {
      'console_scripts': [
        'splitmount = splitmount.splitmount:main'
        ],
      },
    packages = find_packages(),
    )

