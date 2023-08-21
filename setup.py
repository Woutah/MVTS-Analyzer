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
									#Python 3.10		Python 3.8
        'keyboard>=0.10.4',			#0.13.5 			0.10.5
		'matplotlib>=3.6.0',		#3.7.2 				3.6.0
		'numpy>=1.15.0',			#1.25.2 			1.15.0
		'pandas>=1.2.0',			#2.0.3				1.2.0
		'PySide6>=6.2.0',			#6.5.2				6.2.0
		# 'scikit-image>=0.15',		#0.21				0.15  #Only used for y-resolution-reduction for fft
		# 'scikit-learn>=1.3.0',	#1.3.0 #Only used fot certain data-analysis functions (not yet used in GUI)
	]
)
