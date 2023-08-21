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
    entry_points={
        'console_scripts': [
            'MVTS-Analyzer=mvts_analyzer.main:main',
            'mvts-analyzer=mvts_analyzer.main:main',
            'mvtsa=mvts_analyzer.main:main'
		],
	},
	install_requires=[ #Generated using pipreqs
								#			Python 3.10 	
        'keyboard>=0.13.5',		 #0.13.5 	= Tested working
		'matplotlib>=3.7.2',	 #3.7.2 	= Tested working
		'numpy>=1.15.0',		 #1.25.2 	= Tested working
		'pandas>=2.0.3',		 #2.0.3 	= Tested working
		'PySide6>=6.5.2',		 #6.5.2 	= Tested working
		'scikit_learn>=1.3.0',	 #1.3.0		= Tested working
		'scikit-image>=0.15',		 #0.21 		= Tested working
	]
)
