# """
# The main window from which all other windows can be accessed
# """
import importlib
import importlib.util
import logging
import os
import sys
import traceback

import matplotlib
from PySide6 import QtCore, QtGui, QtWidgets
from res.Paths import Paths

from mvts_analyzer.graphing.graph_data import GraphData
from mvts_analyzer.graphing.graph_settings_controller import \
    GraphSettingsController
from mvts_analyzer.graphing.graph_settings_model import GraphSettingsModel
from mvts_analyzer.graphing.graph_settings_view import GraphSettingsView
from mvts_analyzer.graphing.plotter.plot_wrapper import QPlotter
from mvts_analyzer.ui.main_window_ui import Ui_MainWindow
from mvts_analyzer.utility.GuiUtility import create_qt_warningbox
from mvts_analyzer.windows.apply_python_window import ApplyPythonWindow
from mvts_analyzer.windows.merge_column_window import MergeColumnWindow
from mvts_analyzer.windows.rename_label_window import RenameLabelWindow

matplotlib.use('Qt5Agg')
log = logging.getLogger(__name__)

class MainWindow(QtWidgets.QMainWindow):
	def __init__(self, graph_model_args = {}, *args, **kwargs):
		super(MainWindow, self).__init__(*args, **kwargs)
		log.debug("Initializing main window")

		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)

		#Launch in (semi) fullscreen mode
		#=========graph_tab=================

		self.graph_view_windows = []

		self.plot_widget = QtWidgets.QWidget( #the main plot tab
			# self.main_tab_widget,
			objectName="plot_widget"
		)
		self.graph_data_model = GraphData(**graph_model_args)
		self.graph_settings_model = GraphSettingsModel() #Create model
		self.plotter = QPlotter(self.graph_data_model, self.graph_settings_model)
		self.graph_view = GraphSettingsView(self.plotter) # Create View (using created plotter)
		self.setCentralWidget(self.graph_view)
		self.graph_controller = GraphSettingsController(self.graph_data_model, self.graph_settings_model, self.graph_view, self.plotter)


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
		self.ui.actionCopy_Figure_To_Clipboard.triggered.connect(self.graph_controller.copy_plot_to_clipboard) #TODO: move to plotwrapper?
		self.ui.actionAppend_From_File.triggered.connect(self.graph_controller.append_df_from_file)
		self.ui.actionOpenMergeLabelColumnWindow.triggered.connect(self.open_merge_label_column_window)
		self.ui.actionOpen_View_Copy.triggered.connect(lambda x: self.open_view_copy())
		self.ui.actionLive_Window.triggered.connect(lambda x: self.open_live_window())


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


	def _rec_repopulate_python_appliable_menu(self, cur_path : str, cur_depth : int, cur_menu : QtWidgets.QMenu, max_depth : int = -1) -> None:

		if cur_depth > max_depth and max_depth != -1:
			return
		log.debug(f"Currently at {cur_path}")
		for cur_item in os.listdir(cur_path):
			path = os.path.join(cur_path, cur_item)
			if os.path.isdir(path) and cur_item != "__pycache__": #Skip __pycache__ folder
				new_menu = QtWidgets.QMenu(cur_menu) #Folder = Action menu
				new_menu.setTitle(cur_item)
				action = new_menu.menuAction()
				# self.menu_actions.append()
				self._rec_repopulate_python_appliable_menu(os.path.join(cur_path, cur_item), cur_depth=cur_depth+1, cur_menu=new_menu)
				cur_menu.addAction(new_menu.menuAction())
			else:
				if len(cur_item.rsplit(".", 1)) < 2 or cur_item.rsplit(".", 1)[1] != "py": #Skip non-python cur_items
					continue
				name = cur_item.rsplit(".", 1)[0]
				newaction = QtGui.QAction(name)
				self.menu_actions.append(newaction)
				cur_menu.addAction(newaction)
				newaction.triggered.connect(lambda *_, path=path, name=name: self.run_python_appliable(path, name))



	def recreate_python_appliable_menu(self):
		appliables_dir = Paths.DatabasePythonDefaultAppliablesPath
		self.menu_actions = []
		self.ui.menuPython_File.clear()
		log.debug("Recreating python appliables thingy")

		try:
			self._rec_repopulate_python_appliable_menu(appliables_dir, cur_depth=0, cur_menu=self.ui.menuPython_File)
			self.ui.menuPython_File.addSeparator()
			newaction = QtGui.QAction("Refresh")
			self.menu_actions.append(newaction)
			self.ui.menuPython_File.addAction(newaction)
			newaction.triggered.connect(self.recreate_python_appliable_menu)
		except Exception as ex: #pylint: disable=broad-except
			log.error(f"Error when repopulating appliables: {ex}")


	def run_python_appliable(self, path, name):
		try:
			spec = importlib.util.spec_from_file_location("newmodule", path)
			module = importlib.util.module_from_spec(spec)
			# sys.modules["LoadedModule"] = module
			spec.loader.exec_module(module)

			# module = importlib.import_module(f"Operations.DefaultPythonAppliables.{name}")
			# importlib.reload(module)
			module.apply(self.graph_data_model, self.graph_settings_model, self)
		except Exception as ex:
			msg = f"Error during execution of appliable: {ex}"
			log.warning(msg)
			create_qt_warningbox(f"{msg} \n\n {traceback.format_exc()}", "Error during executiong")
			log.warning(traceback.format_exc())



	def execute_python_executable(self, path):
		code = None
		try:
			with open(path) as pythonfile:
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
		assert(graph_settings_model is None or type(graph_settings_model) == type(GraphSettingsModel))

		new_settings = GraphSettingsModel()
		new_settings.copy_attrs(self.graph_settings_model)


		new_view = self.graph_controller.open_view_window(self.graph_data_model, graph_settings_model=new_settings)
		self.graph_view_windows.append(new_view)

		# self.view_window = QtWidgets.QMainWindow(self)
		r = QtGui.QGuiApplication.primaryScreen().geometry()
		r.setSize(QtCore.QSize( 0.7* r.width(),0.7* r.height()))
		new_view.setGeometry(r)

		qtRectangle = new_view.frameGeometry()
		centerPoint = QtWidgets.QDesktopWidget().availableGeometry().center()
		qtRectangle.moveCenter(centerPoint)
		new_view.move(qtRectangle.topLeft())
		new_view.show()




	def open_label_rename_window(self):
		log.info("Opening renaming tool")
		if self.label_rename_window:
			log.info("Window already exists")
			self.open_label_rename_window.show()
			self.open_label_rename_window.activateWindow()
		else:
			self.open_label_rename_window = RenameLabelWindow(self.graph_data_model, parent=self)

	def open_merge_label_column_window(self):
		log.info("Opening column merging tool")
		if self.label_column_merge_tool:
			log.info("Window already exists")
			self.label_column_merge_tool.window.setHidden(False)
			self.label_column_merge_tool.window.show()
			self.label_column_merge_tool.window.activateWindow()
			self.label_column_merge_tool.window.raise_()
		else:
			self.label_column_merge_tool = MergeColumnWindow(self.graph_data_model, parent=self)

	# def open_live_window(self):
	# 	log.info("Opening live window!")
	# 	if self.live_window:
	# 		log.debug("It already existed, bringing to front")
	# 		return
	# 	self.live_window = LiveViewWindow()


	def open_python_window(self):
		log.info("Now opening python window")
		if self.apply_python_window:
			log.info("Winodw already exists?")
			self.apply_python_window.setHidden(False)
			self.apply_python_window.show()
			self.apply_python_window.activateWindow()
			self.apply_python_window.raise_()
		else:
			self.apply_python_window = ApplyPythonWindow(self.graph_data_model, parent=self)

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
			self.close()
			log.info("Also attempting to close all graph views!")
			for wind in self.graph_view_windows:
				try:
					wind.close()
				except Exception as err:
					log.warning(f"Error when closing graph view window: {err}")
					pass
		else:
			a0.ignore() #Else - do not close

if __name__=="__main__":
	import sys
	app = QtWidgets.QApplication(sys.argv)
	mainwin = QtWidgets.QMainWindow()



	w = MainWindow()
	w.show()
	app.exec_()
	print("Done")