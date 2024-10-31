import os
from setuptools import setup, find_packages

setup(
	name='pycelerity',
	version='0.0.2',
	author='Frank Bender',
	author_email='bende263@umn.edu',
	description='A universal database driver',
	long_description=open('README.md').read(),
	long_description_content_type='text/markdown',
	url='https://github.com/frankbenderumn/pycelerity',
	packages=find_packages(),  # Automatically find packages in your project
	classifiers=[
		'Programming Language :: Python :: 3',
		'License :: OSI Approved :: MIT License',
		'Operating System :: OS Independent',
	],
	python_requires='>=3.10',  # Specify Python version requirements
)
