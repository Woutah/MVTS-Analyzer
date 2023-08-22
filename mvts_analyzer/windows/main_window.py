"""
This module implements the main window from which all other windows can be accessed
"""
import importlib
import importlib.util
import logging
import os
import sys
import traceback
import typing

import matplotlib
from PySide6 import QtCore, QtGui, QtWidgets

import mvts_analyzer.res.app_resources_rc  # pylint: disable=unused-import #type: ignore
from mvts_analyzer.graphing.graph_data import GraphData
from mvts_analyzer.graphing.graph_settings_controller import \
    GraphSettingsController
from mvts_analyzer.graphing.graph_settings_model import GraphSettingsModel
from mvts_analyzer.graphing.graph_settings_view import GraphSettingsView
from mvts_analyzer.graphing.plotter.plot_wrapper import QPlotter
from mvts_analyzer.ui.main_window_ui import Ui_MainWindow
from mvts_analyzer.utility.gui_utility import create_qt_warningbox
from mvts_analyzer.windows.apply_python_window import ApplyPythonWindow
from mvts_analyzer.windows.merge_column_window import MergeColumnWindow
from mvts_analyzer.windows.rename_label_window import RenameLabelWindow

matplotlib.use('Qt5Agg')
log = logging.getLogger(__name__)

class MainWindow(QtWidgets.QMainWindow):
	"""The main window from which all the other windows can be accessed"""
	def __init__(self,
			graph_model_args = None,
			graph_settings_model_args = None,
			settings_path = None,
			python_appliables_path = None,
			**kwargs
		):

		"""
		graph_model_args (dict) : Arguments to pass to the graph data model
		graph_settings_model_args (dict) : Arguments to pass to the graph settings model 
			(e.g. what columns to show initially)
		settings_path (str) : Optional path to where the application settings should be stored, if None, use default loc
		python_appliables_path (str) : Optional path to where the python appliables are stored, if None, use default path
		"""
		super(MainWindow, self).__init__(**kwargs)
		if graph_model_args is None:
			graph_model_args = {}
		if graph_settings_model_args is None:
			graph_settings_model_args = {}
		log.debug("Initializing main window")

		self.ui = Ui_MainWindow() #pylint: disable=invalid-name
		self.ui.setupUi(self)

		#========= Settings ================
		settings_dir = settings_path
		if settings_path is not None:
			settings_dir = os.path.dirname(settings_path)
		if settings_path is None or not os.path.exists(settings_dir): #type: ignore
			log.info("Loading/Saving settings from/to default location")
			self._settings = QtCore.QSettings("MVTS-Tools", "MVTS-Analyzer")
		else:
			log.info(f"Loading settings from {settings_path}")
			self._settings = QtCore.QSettings(settings_path, QtCore.QSettings.Format.IniFormat)


		self.restoreGeometry(self._settings.value(
			"window_geometry", self.saveGeometry(), type=QtCore.QRect)) # type: ignore
		new_window_state = self._settings.value("window_state", self.windowState())
		if new_window_state != QtCore.Qt.WindowState.WindowNoState:
			self.restoreState(new_window_state) # type: ignore


		if python_appliables_path is None:
			self._python_appliables_path : typing.Optional[str] = \
				self._settings.value("python_appliables_path", None) #type: ignore
			if self._python_appliables_path is None:
				cur_path = os.path.dirname(os.path.realpath(__file__))
				self._python_appliables_path = os.path.join(cur_path, "..", "python_appliables")
		else:
			log.info(f"Loading settings from {python_appliables_path}")
			if not os.path.exists(python_appliables_path):
				raise FileNotFoundError(f"Could not find python appliables path {python_appliables_path}")
			elif not os.path.isdir(python_appliables_path):
				raise FileNotFoundError(f"Provided python appliables path {python_appliables_path} is not a directory")
		#Launch in (semi) fullscreen mode
		#=========graph_tab=================

		self.graph_view_windows = []

		self.plot_widget = QtWidgets.QWidget() #the main plot tab
		self.graph_data_model = GraphData(**graph_model_args)
		self.graph_settings_model = GraphSettingsModel(**graph_settings_model_args) #Create model
		self.plotter = QPlotter(self.graph_data_model, self.graph_settings_model)
		self.graph_view = GraphSettingsView(self.plotter) # Create View (using created plotter)
		self.setCentralWidget(self.graph_view)
		self.graph_controller = GraphSettingsController(
			self.graph_data_model, self.graph_settings_model, self.graph_view, self.plotter)


		self.menu_actions = []

		#============== Python window ================
		self.apply_python_window = None
		self.label_rename_window = None
		self.label_column_merge_tool = None

		#=============== Toolbar buttons ====================

		self.ui.actionSave_As.triggered.connect(self.graph_controller.save_df_popup)
		self.ui.actionLoad_From_File.triggered.connect(self.graph_controller.load_df_popup)
		self.ui.actionQuit.triggered.connect(self.close)
		self.ui.actionRename_Label.triggered.connect(self.open_label_rename_window)
		self.ui.actionPython_Code.triggered.connect(self.open_python_window)
		self.ui.actionSave_Figure_As.triggered.connect(self.plotter.canvas.open_save_popup)
		self.ui.actionCopy_Figure_To_Clipboard.triggered.connect(self.graph_controller.copy_plot_to_clipboard)
		self.ui.actionAppend_From_File.triggered.connect(self.graph_controller.append_df_from_file)
		self.ui.actionOpenMergeLabelColumnWindow.triggered.connect(self.open_merge_label_column_window)
		self.ui.actionOpen_View_Copy.triggered.connect(lambda x: self.open_view_copy())


		self.ui.actionHide_All_But_Selection.triggered.connect(self.graph_data_model.hide_all_datapoints_except_selection)
		self.ui.actionHide_Selection.triggered.connect(self.graph_data_model.hide_selection)
		self.ui.actionUnhide_All.triggered.connect(self.graph_data_model.unhide_all_datapoints)
		self.ui.actionSwitch_Hidden.triggered.connect(self.graph_data_model.flip_hidden)
		self.ui.actionSave_Not_Hidden_Only_As.triggered.connect(self.graph_controller.save_df_not_hidden_only_popup)

		self.ui.actionReplot.triggered.connect(self.graph_controller.plotter_replot)
		self.ui.actionReplot_View.triggered.connect(self.graph_controller.set_xlim_to_view)
		self.ui.actionReplot_View.triggered.connect(self.graph_controller.plotter_replot)
		self.ui.actionReplot_View_FFT.triggered.connect(self.graph_controller.set_fft_lim_to_view)
		self.ui.actionReplot_View_FFT.triggered.connect(self.graph_controller.plotter_replot)
		self.ui.actionReset_Domain.triggered.connect(self.graph_controller.reset_plot_domain)
		self.ui.actionReset_Domain.triggered.connect(self.graph_controller.plotter_replot)
		self.ui.actionReset_View_Settings.triggered.connect(self.graph_controller.reset_plot_settings)
		self.ui.actionReset_View_Settings.triggered.connect(self.graph_controller.plotter_replot)

		self.ui.actionSave_Selection_As.triggered.connect(self.graph_controller.save_df_selection_only_popup)

		#================ Live Window ==========
		self.live_window = None

		#================= Create Python appliable links
		self.recreate_python_appliable_menu()

	def get_python_appliables_path(self):
		"""Return the path to the python appliables folder"""
		return self._python_appliables_path

	def set_python_appliables_path(self, new_path):
		"""Set the path to the python appliables folder"""
		if new_path != self._python_appliables_path: #If change
			self._python_appliables_path = new_path
			self.recreate_python_appliable_menu() #Recreate the menu

	def save_settings(self):
		"""
		Save the app-settings to the settings file
		"""
		log.info("Saving settings")
		self._settings.setValue("window_geometry", self.saveGeometry())
		self._settings.setValue("window_state", self.saveState())
		self._settings.setValue("python_appliables_path", self._python_appliables_path)

	def _rec_repopulate_python_appliable_menu(self,
				cur_path : str,
				cur_depth : int,
				cur_menu : QtWidgets.QMenu,
				max_depth : int = -1
			) -> None:
		if cur_depth > max_depth and max_depth != -1:
			return
		log.debug(f"Currently at {cur_path}")
		for cur_item in os.listdir(cur_path):
			path = os.path.join(cur_path, cur_item)
			if os.path.isdir(path) and cur_item != "__pycache__": #Skip __pycache__ folder
				new_menu = QtWidgets.QMenu(cur_menu) #Folder = Action menu
				new_menu.setTitle(cur_item)
				self._rec_repopulate_python_appliable_menu(
					os.path.join(cur_path, cur_item), cur_depth=cur_depth+1, cur_menu=new_menu)
				cur_menu.addAction(new_menu.menuAction())
			else:
				if len(cur_item.rsplit(".", 1)) < 2 or cur_item.rsplit(".", 1)[1] != "py": #Skip non-python cur_items
					continue
				name = cur_item.rsplit(".", 1)[0]
				newaction = QtGui.QAction(name)
				self.menu_actions.append(newaction)
				cur_menu.addAction(newaction)
				newaction.triggered.connect(lambda *_, path=path, name=name: self.run_python_appliable(path))


	def popup_set_python_appliables_folder(self):
		"""
		Reloads the python appliable menu based on the selected folder
		"""
		log.debug("Popup set python appliables folder")
		new_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select folder with python appliables")
		if new_path is None or new_path == "":
			return
		self._python_appliables_path = new_path
		self.recreate_python_appliable_menu()

	def recreate_python_appliable_menu(self):
		"""
		Reloads the python appliable menu based on the selected folder
		"""
		self.menu_actions = []
		self.ui.menuPython_File.clear()
		self.ui.menuPython_File2.clear()
		log.debug("Recreating python appliables thingy")


		try:
			if self._python_appliables_path is None:
				raise ValueError("No python appliables path set")
			self._rec_repopulate_python_appliable_menu(
				self._python_appliables_path, cur_depth=0, cur_menu=self.ui.menuPython_File)
			self._rec_repopulate_python_appliable_menu(
				self._python_appliables_path, cur_depth=0, cur_menu=self.ui.menuPython_File2)
			self.ui.menuPython_File.addSeparator()
		except Exception as ex: #pylint: disable=broad-except
			log.error(f"Error when repopulating appliables: {ex}")

		set_folder_action = QtGui.QAction("Set Folder...")
		self.menu_actions.append(set_folder_action)
		icon = QtGui.QIcon(":/Icons/icons/Custom Icons/python-folder-open.svg")
		set_folder_action.setIcon(icon)
		self.ui.menuPython_File.addAction(set_folder_action)
		self.ui.menuPython_File2.addAction(set_folder_action)


		set_folder_action.triggered.connect(self.popup_set_python_appliables_folder)

		newaction = QtGui.QAction("Refresh")
		self.menu_actions.append(newaction)
		self.ui.menuPython_File.addAction(newaction)
		self.ui.menuPython_File2.addAction(newaction)
		icon = QtGui.QIcon(":/Icons/icons/Tango Icons/actions/view-refresh.svg")
		newaction.setIcon(icon)
		newaction.triggered.connect(self.recreate_python_appliable_menu)

	def run_python_appliable(self, path):
		"""Run a python appliable """
		try:
			spec = importlib.util.spec_from_file_location("newmodule", path) #Reload module each time
			if spec is None:
				raise ModuleNotFoundError("Could not load spec of python appliable (module).")
			module = importlib.util.module_from_spec(spec)
			# sys.modules["LoadedModule"] = module
			spec.loader.exec_module(module) #type: ignore

			#Check if "apply"-function exists in module
			if hasattr(module, "apply"):
				module.apply(self.graph_data_model, self.graph_settings_model, self)
			else:
				with open(path, encoding="utf-8") as pythonfile:
					code = pythonfile.read() #Load pythonfile
				self.graph_data_model.apply_python_code(code)
		except Exception as ex: #pylint: disable=broad-exception-caught
			msg = f"Error during execution of appliable: {ex}"
			log.warning(msg)
			create_qt_warningbox(f"{msg} \n\n {traceback.format_exc()}", "Error during execution")
			log.warning(traceback.format_exc())



	def execute_python_executable(self, path):
		"""Execute a python file as an executable in this context"""
		code = None
		try:
			with open(path, encoding="utf-8") as pythonfile:
				code = pythonfile.read() #Load pythonfile
		except FileNotFoundError:
			create_qt_warningbox("File not found", f"Could not find file {path}")
			return


		success, msg = self.graph_data_model.apply_python_code(code)
		msgbox = QtWidgets.QMessageBox()
		msgbox.setText(f"{msg}")
		msgbox.setWindowTitle("Code Execution")
		if success:
			msgbox.setIcon(QtWidgets.QMessageBox.Icon.Warning)
		else:
			msgbox.setIcon(QtWidgets.QMessageBox.Icon.Information)

	def open_view_copy(self, graph_settings_model = None):
		"""Open a copy of the current view in a new window"""
		assert graph_settings_model is None or not isinstance(graph_settings_model, GraphSettingsModel)

		new_settings = GraphSettingsModel()
		new_settings.copy_attrs(self.graph_settings_model)


		new_view = self.graph_controller.open_view_window(
			self.graph_data_model,
			graph_settings_model=new_settings,
			parent=self
		)
		self.graph_view_windows.append(new_view)

		# self.view_window = QtWidgets.QMainWindow(self)
		screen_rect = QtGui.QGuiApplication.primaryScreen().geometry()
		screen_rect.setSize(QtCore.QSize( int(0.7* screen_rect.width()),int(0.7* screen_rect.height())))
		new_view.setGeometry(screen_rect)

		qt_rect = new_view.frameGeometry()
		cent_point = QtGui.QGuiApplication.primaryScreen().geometry().center()
		qt_rect.moveCenter(cent_point)
		new_view.move(qt_rect.topLeft())
		new_view.show()




	def open_label_rename_window(self):
		"""Opens the label renaming tool-window"""
		log.info("Opening renaming tool")
		if self.label_rename_window:
			log.info("Window already exists")
			self.label_rename_window.window.setHidden(False)
			self.label_rename_window.window.show()
			# self.label_rename_window.window.activateWindow()
			self.label_rename_window.window.raise_()
			#Unminimize
			self.label_rename_window.window.setWindowState(
				self.label_rename_window.window.windowState()
				& ~QtCore.Qt.WindowState.WindowMinimized
				| QtCore.Qt.WindowState.WindowActive)
		else:
			self.label_rename_window = RenameLabelWindow(self.graph_data_model, parent=self)

	def open_merge_label_column_window(self):
		"""Opens the label merging tool-window"""
		log.info("Opening column merging tool")
		if self.label_column_merge_tool:
			log.info("Window already exists")
			self.label_column_merge_tool.window.setHidden(False)
			self.label_column_merge_tool.window.show()
			self.label_column_merge_tool.window.raise_()
			self.label_column_merge_tool.window.setWindowState(
				self.label_column_merge_tool.window.windowState()
				& ~QtCore.Qt.WindowState.WindowMinimized
				| QtCore.Qt.WindowState.WindowActive)
		else:
			self.label_column_merge_tool = MergeColumnWindow(self.graph_data_model, parent=self)


	def open_python_window(self):
		"""
		Opens the python-code window if it does not exist, else brings it to the front and unhides it
		"""
		log.info("Now opening python window")
		if self.apply_python_window:
			log.info("Winodw already exists?")
			self.apply_python_window.setHidden(False)
			self.apply_python_window.show()
			self.apply_python_window.raise_()
			self.apply_python_window.setWindowState(
				self.apply_python_window.windowState()
				& ~QtCore.Qt.WindowState.WindowMinimized
				| QtCore.Qt.WindowState.WindowActive)
		else:
			self.apply_python_window = ApplyPythonWindow(self.graph_data_model, main_window=self)

	def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
		"""Overload default close event for a confirmation
		"""
		# ConfirmationBox = QtGui.QMessageBox()

		quit_msg = "Are you sure you want to exit the program? All unsaved progress will be lost."
		ret = QtWidgets.QMessageBox.question(self, 'Confirm',
						quit_msg, QtWidgets.QMessageBox.StandardButton.Yes, QtWidgets.QMessageBox.StandardButton.No)


		if ret == QtWidgets.QMessageBox.StandardButton.Yes:
			log.info("Closing main window!")
			# closemain = True
			self.save_settings() #Save settings
			self.close()
			log.info("Also attempting to close all graph views!")
			for wind in self.graph_view_windows:
				wind.close()
		else:
			a0.ignore() #Else - do not close

if __name__=="__main__":
	app = QtWidgets.QApplication(sys.argv)
	mainwin = QtWidgets.QMainWindow()
	w = MainWindow()
	w.show()
	app.exec_()
	print("Done")
