"""The setup script."""
from setuptools import setup, find_packages


setup(
	name = "MVTS-Analyzer",
	version= "0.0.0",
	packages=find_packages('.'),
    description=("Annotation and analysis tool for Multivariate Time Series Data"),
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author="Wouter Stokman",
    url="https://github.com/Woutah/MVTS-Analyzer",
    license="LGPLv2",
    include_package_data=True,
    # install_requires=[ #Generated using pipreqs
    #     'PySide6>=6.0.0', # Qt for Python, works for 6.5.1.1
    #     'pathos>=0.3.0', #Works for 0.3.0
    #     'setuptools>=65.0.0', #Works for 65.5.0
	# 	'dill>=0.3.0', #Works for 0.3.6
	# 	'multiprocess>=0.70.00', #Works for 0.70.14
	# 	'numpydoc>=1.4.0', #Works for 1.5.0
	# 	'pycryptodome>=3.10.0', #Works for 3.18.0
    #     'pyside6-utils>=1.2.1, <1.3.0', #Works for 1.2.1
    #     'PySignal>=1.1.1' #Works for 1.1.1,
	# ]
)
