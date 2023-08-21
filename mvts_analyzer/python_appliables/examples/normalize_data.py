"""
This examples normalizes the numeric columns in the currently loaded dataframe

=======================================
Note that we use a more complex function signature here. We can choose between a simple python script 
(see print_something.py) in which we can access the dataframe using self.df/self.df_selection or we can use a 
function with the following signature:

def apply(model : GraphData, settings_model : GraphSettingsModel, main_window : QtWidgets.QMainWindow = None)

Which will be called with the current GraphDataModel, the GraphSettingsModel and the MainWindow.
Note that we will have to use the set_df method to update the dataframe in the GraphDataModel.

Using this signature allows us to use type-hinting compared to the simple python script in which the context
is not known.
"""
from mvts_analyzer.graphing.graph_data import GraphData
from mvts_analyzer.graphing.graph_settings_model import GraphSettingsModel
from PySide6 import QtWidgets
import typing

def apply(
		model : GraphData,
		settings_model : GraphSettingsModel,
		main_window : typing.Optional[QtWidgets.QMainWindow] = None
	):
	"""Example apply-function that normalizes the numeric columns in the currently loaded dataframe"""
	# model.df = 
	df = model.df
	if df is None:
		raise ValueError("No dataframe loaded")

	for col in df.columns:
		#min-max normalization
		if df[col].dtype == "float64" or df[col].dtype == "int64":
			df[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())
	model.set_df(df)