

# from mvts_analyzer.windows.custom_widgets.ApplyPythonWindow.ApplyPythonWindow_ui import Ui_ApplyPythonWindow as ui
from re import U
import traceback
from mvts_analyzer.utility import GuiUtility
from mvts_analyzer.ui.apply_python_window_ui import Ui_ApplyPythonWindow
from mvts_analyzer.graphing.graph_data import GraphData
import PySide6
import logging
log = logging.getLogger(__name__)
from res.Paths import Paths
import pandas as pd
import typing
import os

from PySide6 import QtCore, QtGui, QtWidgets

class ApplyPythonWindow(QtWidgets.QMainWindow, object):

	
	def __init__(self, GraphDataModel : GraphData, *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)
		log.debug("Creating apply pythonwindow")
		self.GraphDataModel = GraphDataModel

		# self.window = QtWidgets.QMainWindow(*args, **kwargs) #Create window
		self.ui = Ui_ApplyPythonWindow()
		self.ui.setupUi(self)
		

		self.ui.CancelButton.clicked.connect(self.clicked_cancel)
		# self.ui.actionSaveAs.triggered.connect(self.save_code_popup)
		self.ui.actionOpenFromFile.triggered.connect(self.open_from_file_popup)
		self.ui.actionSaveAs.triggered.connect(self.save_to_file_popup)
		self.ui.actionSave.triggered.connect(self.save_if_path_known)
		self.ui.ExecuteButton.pressed.connect(lambda *_: self.execute_code(False))
		self.ui.ExecuteAndUpdateButton.pressed.connect(lambda *_: self.execute_code(True))

		self.show() #Start showing window
		
		self._cur_save_path = ""

	@property
	def cur_save_path(self):
		return self._cur_save_path

	@cur_save_path.setter
	def cur_save_path(self, new_path : str):
		self._cur_save_path = new_path
		if new_path is None or len(new_path) == 0:
			self.ui.actionSave.setEnabled(False) #If no path is known --> button inactive
		else:
			self.ui.actionSave.setEnabled(True)


	def execute_code(self, force_update_afterwards : bool):
		# df = self.GraphDataModel.df
		model = self.GraphDataModel
		success, msg = model.apply_python_code(self.python_code, force_update_afterwards=force_update_afterwards)

		if not success:
			GuiUtility.create_qt_warningbox(msg)


	@property
	def python_code(self):
		return self.ui.pythonCodeTextEdit.toPlainText()

	@python_code.setter
	def python_code(self, new_code : str):
		self.ui.pythonCodeTextEdit.setText(new_code)


	def open_from_file_popup(self):
		log.info("Opening python code from file")
		fname = PySide6.QtWidgets.QFileDialog.getOpenFileName(None, 'Open file', 
				Paths.DatabasePythonDefaultAppliablesPath, "Python Dataframe Appliable code (*.py)")
		log.debug("Picked file: {}".format(fname))
		self.open_from_file(fname[0])


	def open_from_file(self, path : str):
		log.info(f"Now loading from file {path}")
		if path is None or path == "":
			return 
		
		try:
			with open(path) as pythonfile:	
				self.python_code = pythonfile.read() #Load pythonfile
			self.cur_save_path = path
		except FileNotFoundError:
			GuiUtility.create_qt_warningbox("File not found", f"Could not find file {path}")
	
	def save_if_path_known(self) -> None:
		"""Only saves if path is known
		"""
		if self.cur_save_path is not None and len(self.cur_save_path) > 0:
			self.save_to_file(self.cur_save_path)

	def save_to_file_popup(self):
		
		fname = PySide6.QtWidgets.QFileDialog.getSaveFileName(None, 'Save As...',
			os.path.join(Paths.DatabasePythonUsermadeAppliablesPath, self.cur_save_path), "Python file (*.py)")
		if fname is not None and len(fname[0]) > 0:
			log.info(f"Trying to save to path {fname}")
			self.save_to_file(fname[0])
		else:
			log.error(f"Could not save under name: {fname}")


	def save_to_file(self, path : str):
		log.info(f"Now trying to save python code to {path}")
		try: 
			with open(path, "w") as pythonfile:
				log.debug(f"Writing to file: {self.python_code}")
				pythonfile.write(str(self.python_code))		
				self.cur_save_path = path
		except Exception as err:
			log.error(f"Could not write to file: {err}")


	def clicked_execute(self):
		log.info("Clicked execute, now executing code")
		raise NotImplementedError
	

	def clicked_cancel(self):
		log.info("Clicked cancel, closing pythoncode window...")
		self.close()
		

if __name__ == "__init__":
	log.debug("Running test:")
	






		