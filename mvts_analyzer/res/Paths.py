

"""Hold a class to manage all paths to config files etc. Return the paths in its pathdict relative to Paths.py
"""

import os
import inspect
import logging
log = logging.getLogger(__name__)
from dataclasses import dataclass


class _PathsMeta(type):
	"""Metaclass that adds the current-file in front of all relative paths in this class.
	In this case, all strings are considered relative paths, and are converted to absolute paths. 

	Args:
		type (_type_): _description_
	"""
	def __getattribute__(cls, __name: str) -> any:
		"""Override __getattribute__ to return the path of the given property

		Args:
			__name (str): name of the property
		Returns:
			Any: the path of the property
		"""
		base = object.__getattribute__(cls, __name)
		#Check if _ or __ (private or dunder) and return if so
		if __name.startswith("_") or __name.startswith("__") or type(base) != str:
			return base
		curpath = inspect.getabsfile(inspect.currentframe()).rsplit(os.sep, 2) #TODO: make this more robust, currently only works if the file is in a folder 2 levels deep from actual relfolder
		# print(f"Base: {base}, curpath: {curpath}")
		base=base.split("/")
		return os.path.join(curpath[0], *base)
		

class Paths(metaclass=_PathsMeta): #Inherit from metaclass use __getattribute__ method without instance

	DatabasePythonUsermadeAppliablesPath =			"/Data/SavedPythonAppliables"
	DatabasePythonDefaultAppliablesPath =			"/Utility/PythonSubtools"
	FiguresBasePath =								"/etc"
	DefaultReportFilePath =							"/Utility/ReportMaker/Templates/DefaultReportTemplate.docx"
	DefaultReportOverviewFilePath =					"/Utility/ReportMaker/Templates/DefaultReportOverviewTemplate.docx"
	DocumentsPath =					 				os.path.expanduser("~") #Documents directory TODO: not really in format of previous, does seem to fare okay though
	LocalDataPath =					 				"/data"
	OutputPath =					 				"/output"
	UnitTestDfWithOverlappingIdsFilePath =			"/UnitTests/ExampleData/labeled_df_Depth_Load_Datetime_Label_LateralId+overlappingIds.pkl"
	UnitTestDfFilePath =							"/UnitTests/ExampleData/labeled_df_Depth_Load_Datetime_Label_LateralId.pkl"
	DarkStyleSheetFilePath =						"/res/stylesheets/pyqt5-dark-theme.stylesheet"
	NormalStyleSheetFilePath =						"/res/stylesheets/pyqt5-normal_theme.stylesheet"
	MachineLearningSettingsPath =					"/Settings/MachineLearning"
	CalculatedLoadWindowSettingsPath =				"/Settings/CalculatedLoadWindow"


if __name__ == "__main__":
	print("start")

	for key,item in Paths.__dict__.items():
		if not key.startswith("_"):
			print(f"{Paths.__getattribute__(key)}")
			# print(f"{key}: {item}")
	