# coding: utf-8
from __future__ import absolute_import, print_function
from setuptools import setup
import os.path
import cucutags


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as inf:
        return "\n" + inf.read().replace("\r\n", "\n")

setup(
    name='cucutags',
    py_modules=['cucutags'],
    version=str(cucutags.__version__),
    description='Generates ctags for BDD .feature/behave steps',
    author=u'Matěj Cepl',
    author_email='mcepl@redhat.com',
    url='https://gitorious.org/cucutags/cucutags/',
    long_description=read("README"),
    test_suite='test',
    keywords=['BDD', 'behave', 'ctags', 'tags'],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Testing"
    ],
    requires=["parse"]
)
