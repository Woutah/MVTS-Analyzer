"""
Implements:
ApplyPythonWindow - A window with a textedit for python code to edit the dataframe during runtime.

"""
#pylint: disable=invalid-name #Allow camelcase
import logging
import os

from PySide6 import QtWidgets

from mvts_analyzer.graphing.graph_data import GraphData
from mvts_analyzer.ui.apply_python_window_ui import Ui_ApplyPythonWindow
from mvts_analyzer.utility import gui_utility
import mvts_analyzer.windows.main_window #pylint: disable=unused-import


log = logging.getLogger(__name__)

class ApplyPythonWindow(QtWidgets.QMainWindow, object):
	"""
	Window with a textedit for python code, and a button to execute it.
	"""
	# from mvts_analyzer.windows.main_window import MainWindow as MainWindow
	def __init__(self, GraphDataModel : GraphData,
	    	main_window,
			*args,
			**kwargs
		) -> None:
		super().__init__(*args, **kwargs)
		log.debug("Creating apply pythonwindow")
		self.GraphDataModel = GraphDataModel
		self.MainWindow = main_window

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
		"""Return the current save path"""
		return self._cur_save_path

	@cur_save_path.setter
	def cur_save_path(self, new_path : str):
		"""Setter for save-path. Also updates the save-button"""
		self._cur_save_path = new_path
		if new_path is None or len(new_path) == 0:
			self.ui.actionSave.setEnabled(False) #If no path is known --> button inactive
		else:
			self.ui.actionSave.setEnabled(True)


	def execute_code(self, force_update_afterwards : bool):
		"""Executes the python code in the textedit

		Args:
			force_update_afterwards (bool): If True, then the graphdata will be updated after the code is executed
				to reflect possible changes in the dataframe
		"""
		# df = self.GraphDataModel.df
		model = self.GraphDataModel
		success, msg = model.apply_python_code(self.python_code, force_update_afterwards=force_update_afterwards)

		if not success:
			gui_utility.create_qt_warningbox(msg)


	@property
	def python_code(self):
		"""Getter for the current python code in the textedit"""
		return self.ui.pythonCodeTextEdit.toPlainText()

	@python_code.setter
	def python_code(self, new_code : str):
		"""Setter for the current python code in the textedit"""
		self.ui.pythonCodeTextEdit.setText(new_code)


	def open_from_file_popup(self):
		"""Opens a filedialog to open a python file"""
		log.info("Opening python code from file")
		fname = QtWidgets.QFileDialog.getOpenFileName(None, 'Open file',  #type: ignore
				self.MainWindow.get_python_appliables_path(), "Python Dataframe Appliable code (*.py)") #type: ignore
		log.debug(f"Picked file: {fname}")
		self.open_from_file(fname[0])


	def open_from_file(self, path : str):
		"""Opens a python file from the given path

		Args:
			path (str): The path to the python file
		"""
		log.info(f"Now loading from file {path}")
		if path is None or path == "":
			return
		try:
			with open(path, encoding="utf-8") as pythonfile:
				self.python_code = pythonfile.read() #Load pythonfile
			self.cur_save_path = path
		except FileNotFoundError:
			gui_utility.create_qt_warningbox("File not found", f"Could not find file {path}")

	def save_if_path_known(self) -> None:
		"""
		Only saves if path is known
		"""
		if self.cur_save_path is not None and len(self.cur_save_path) > 0:
			self.save_to_file(self.cur_save_path)

	def save_to_file_popup(self):
		"""Opens a filedialog to save the python code to a file"""
		base_path = self.cur_save_path
		if base_path is None or len(self.cur_save_path) == 0:
			base_path = self.MainWindow.get_python_appliables_path()
		fname, _ = QtWidgets.QFileDialog.getSaveFileName(None, 'Save As...', #type: ignore
			base_path, "Python file (*.py)")
		if fname is not None and len(fname) > 0:
			log.info(f"Trying to save to path {fname}")
			self.save_to_file(fname)
		else:
			log.error(f"Could not save under name: {fname}")
			return

		cur_appliables_path = self.MainWindow.get_python_appliables_path()
		if cur_appliables_path is None or not fname.startswith(cur_appliables_path):
			folder_loc = fname.rsplit(os.sep, 1)[0].rsplit("/", 1)[0]
			msg_box = QtWidgets.QMessageBox()
			msg_box.setText("The script was not saved in the python appliables folder - do you want to change the appliables "
		   		f"folder location (currently: {cur_appliables_path}) to the saved script-location ({folder_loc})?")
			msg_box.setStandardButtons(
				QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
			)
			if msg_box.exec() == QtWidgets.QMessageBox.StandardButton.Yes:
				self.MainWindow.set_python_appliables_path(folder_loc)


	@gui_utility.catch_show_exception_in_popup_decorator(custom_error_msg="<b>Error while saving python code</b>")
	def save_to_file(self, path : str):
		"""
		Saves the python code to the given path
		Args:
			path (str): The path to save the python code to
		"""
		log.info(f"Now trying to save python code to {path}")
		with open(path, "w", encoding="utf-8") as pythonfile:
			log.debug(f"Writing to file: {self.python_code}")
			pythonfile.write(str(self.python_code))
			self.cur_save_path = path


	def clicked_cancel(self):
		"""When cancel is clicked, closes the window"""
		log.info("Clicked cancel, closing pythoncode window...")
		self.close()
