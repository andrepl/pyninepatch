#!/usr/bin/env python
 
from setuptools import setup, find_packages
import sys, os
 
version = '0.1'
 
setup(name='ninepatch',
    version=version,
    description="9-Patch Image Renderer",
    long_description="""Python module and command line tool to render android-style 9-patch images.""",
    classifiers=[],
    keywords='ninepatch 9-patch',
    author='Andre LeBlanc',
    author_email='andrepleblanc@gmail.com',
    url='https://github.com/andrepl/pyninepatch',
    license='BSD',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "PIL"
        ],
    py_modules=['ninepatch'],
    entry_points={
        "console_scripts": [
            'myexecutable = ninepatch:main',
        ],
    }
)
