"""
Manages linking the view to the model and vice versa.
This enables the use of multiple views with the same model.
"""

import io
import logging

import matplotlib
import numpy as np
import pandas as pd
from PySide6 import QtCore, QtGui, QtWidgets

from mvts_analyzer.graphing.graph_data import GraphData
from mvts_analyzer.graphing.graph_settings_model import GraphSettingsModel
from mvts_analyzer.graphing.graph_settings_view import GraphSettingsView
from mvts_analyzer.utility import GuiUtility

import typing

from mvts_analyzer.graphing.plotter.plot_wrapper import QPlotter
from mvts_analyzer.utility import DfUtility
from mvts_analyzer.widgets.datastructures import LimitedRange
from mvts_analyzer.windows.load_type_selection_window import (
    DuplicatePolicy, LoadTypeSelectionDialog, MainLoadType)

log = logging.getLogger(__name__)

#pylint: disable=protected-access #Controller accesses protected members of model and view
#pylint: disable=invalid-name #Naming for function names less strict

class GraphSettingsViewWindow(QtWidgets.QMainWindow):
	"""Small class that opens a view with the passed datamodel + settingsmodel and cleans up afterwards
	otherwise logic will be executed even when the view is closed, this makes sure the plotter,
	graph-view and controller are removed

	"""
	def __init__(self,
				graph_data_model : GraphData,
				graph_settings_model : GraphSettingsModel,
				parent: typing.Optional[QtWidgets.QWidget] = None,
				flags: typing.Union[QtCore.Qt.WindowFlags, QtCore.Qt.WindowType] = QtCore.Qt.WindowFlags(), #type:ignore
				deleteOnClose = True
			) -> None:
		super().__init__(parent, flags)

		self.graph_data_model = graph_data_model
		if graph_data_model is None:
			self.graph_data_model = GraphData()

		self.graph_settings_model = graph_settings_model
		if graph_settings_model is None:
			self.graph_settings_model = GraphSettingsModel()

		if deleteOnClose:
			self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose) #Prevent plot-connections-calls after del
		self.plotter = QPlotter(self.graph_data_model, self.graph_settings_model)
		self.graph_view = GraphSettingsView(self.plotter) # Create View (using created plotter)
		self.graph_controller = GraphSettingsController(
			self.graph_data_model, self.graph_settings_model, self.graph_view, self.plotter
		)
		self.setCentralWidget(self.graph_view)

		self.graph_controller.view_reload()


class GraphSettingsController():
	"""
	The controller class - manages the communication between view and model and enables the use of multiple views
	with the same model.
	"""
	def __init__(self,
			data_model: GraphData,
			model : GraphSettingsModel,
			view : GraphSettingsView,
			plotter : QPlotter,
			 *args,
			**kwargs
		):
		super(GraphSettingsController, self).__init__(*args, **kwargs)
		log.debug("Now initializing GraphSettingsController")


		self.data_model = data_model
		self.plotter = plotter
		self.model = model
		self.view = view

		self.labeler_window_view = self.view.plot_settings.labeler_window_view

		self.view.plot_settings.inner_settings.fft_brightness_slider.set_all(limited_value=self.model.fft_brightness_limval)
		# self.view.plot_settings.inner_settings.plot_domain_sliders.set_all(limited_range=self.model.plot_domain_limrange)
		self.view.plot_settings.inner_settings.plot_domain_widget.set_all(limited_range=self.model.plot_domain_limrange)


		self.connections = []

		#=======================================
		#== View -> Controller (buttons etc.) ==
		#=======================================
		sv_out = self.view.plot_settings
		sv_out.updateSignal.connect(lambda *_ : self.plotter_replot())
		sv_out.replotViewSignal.connect(self.set_xlim_to_view) #First set xlim
		sv_out.replotViewSignal.connect(self.plotter_replot) #Then replot (maybe not neccesary)
		sv_out.saveDfSignal.connect(self.save_df_popup)
		sv_out.fftZoomViewSignal.connect(self.set_fft_lim_to_view)


		#======================================
		#========= Model -> View ==============
		#==== (Track & delete when done) ======
		#======================================
		sm = self.model
		sm.fftToggleChanged.connect(self.process_model_fft_toggle)
		sm.fftLineRangeChanged.connect(self.process_model_fft_line_range)
		sm.fftBrightnessChanged.connect(self.process_model_fft_brightness)
		sm.fftColorMapChanged.connect(self.process_model_fft_color_map)
		sm.fontSizeChanged.connect(self.process_model_font_size)
		sm.plotDomainLimrangeChanged.connect(self.process_model_plot_domain)
		sm.plotListChanged.connect(self.process_model_plot_list)
		sm.xAxisChanged.connect(self.process_model_x_axis)
		sm.plotTypeChanged.connect(self.process_model_plot_type)
		sm.dfColumnsChanged.connect(self.process_model_fft_column_options) #Update fft_column options
		sm.plotColorMethodChanged.connect(self.process_model_plotColorMethod)
		sm.selectionGapFillMsChanged.connect(self.process_model_selectionGapFillMs)

		#============ Data -> view callbacks ==========

		# self.data_model.fileSourceChanged.connect(self.process_model_file_source)
		self.data_model.dfChanged.connect(self.process_data_dfChanged)

		#======================================
		#========= View -> Model ==============
		#======================================
		sv_inner = self.view.plot_settings.inner_settings
		sv_inner.fftToggleBtnChanged.connect(self.process_view_fftToggleBtn)
		sv_inner.fftColumnSelectorChanged.connect(self.process_view_fftColumn)
		sv_inner.fftQualityChanged.connect(self.process_view_fftQuality)
		sv_inner.fftBrightnessChanged.connect(self.process_view_fftBrightness)
		sv_inner.fftLineRangeChanged.connect(self.process_view_fftLineRange)
		sv_inner.fftColorMapChanged.connect(self.process_view_fftColorMap)
		sv_inner.fontSizeChanged.connect(self.process_view_fontSize)
		sv_inner.labelerToggleChanged.connect(self.process_view_labelerToggle)
		sv_inner.normalizationToggleChanged.connect(self.process_view_normalizationToggle)
		sv_inner.plotDomainChanged.connect(self.process_view_plotDomain)
		sv_inner.plotListChanged.connect(self.process_view_plotList)
		sv_inner.plottedLabelsChanged.connect(self.process_view_plottedLabels)
		sv_inner.xAxisChanged.connect(self.process_view_xAxisChanged)
		sv_inner.plotTypeChanged.connect(self.process_view_plotTypeChanged)
		sv_inner.plot_colors_column_ComboBox.currentTextChanged.connect(lambda x: self.process_view_plotColorColumn())
		sv_inner.plot_colors_method_ComboBox.currentIndexChanged.connect(self.process_view_plotColorMethod)
		sv_inner.plot_select_gapfill_slider_with_box.valueEdited.connect(self.process_view_selectionGapFillMs)

		#=========== View --> View =============
		sv_inner.plot_colors_method_ComboBox.currentIndexChanged.connect(
			lambda x: sv_inner.plot_colors_StackedWidget.setCurrentIndex(int(x)))
		sv_inner.plot_colors_method_ComboBox.currentIndexChanged.connect(
			self.process_view_plotColorColumn)


		#=================== Labeler window <--> Model ===============
		self.labeler_window_view.setLabelBtnPressed.connect(self.process_labeler_label_btn_pressed)
		self.labeler_window_view.columnOptionChanged.connect(self.process_labeler_column_option_changed)
		self.view.actionCopy_Figure_To_Clipboard.triggered.connect(self.copy_plot_to_clipboard)
		self.process_data_dfChanged()
		self.view_reload()


	#=================================================================
	#===================== Labeler Window --> Model ==================
	#=================================================================
	def process_labeler_label_btn_pressed(self, column, label):
		"""Sets the label of current selection to the currently selected label"""
		log.debug(f"Trying to set column {column} to label {label}")

		if column is not None and len(column) > 0:
			if label is not None \
					and (len(label) == 0
							or label.lower() == 'none'
							or label.lower() == 'nan'
							or label.lower() == '<na>'
						): #Be sure to rename all types of nan to actual nonevalue #TODO: is this the best solution
				label = None #TODO: maybe do this in process_labeler_columnOptionChanged instead?

			if(self.data_model.set_selection_lbls(column, label)):
				log.info(f"Succesfully set column: {column} to label: {label} of current selection (consisting of {len(self.data_model._df_selection)} entries)")
				self.process_labeler_column_option_changed(self.labeler_window_view.col_dropdown.currentText()) #Refresh current selection
				return
		log.info(f"Could not set column: {column} to label: {label} of current selection (make sure points are selected)")

	def process_labeler_column_option_changed(self, new_column):
		log.debug(f"Setting labeler column to {new_column}")
		options = []
		if new_column is not None and self.data_model.df is not None:
			if new_column in self.data_model.df.columns:
				options = self.data_model.df[new_column].unique()
			log.debug(f"Labeler column {new_column} contains labels: {options}")
		else:
			log.debug(f"Labeler column {new_column} contains no labels")

		if new_column in self.model.label_column_options_presets.keys():
			options = list(set(list(options) + self.model.label_column_options_presets[new_column]))

		options = [str(i) for i in options]

		self.labeler_window_view.set_lbl_lbl_options(options)



	#=================================================================
	#====================== View --> model ===========================
	#=================================================================
	def process_view_fftToggleBtn(self, new_val : bool):
		"""
		View --> Model
		Fft toggle button changed
		Args:
			new_val (bool): The new checked state of the fft toggle button
		"""
		self.model.fft_toggle = new_val

	def process_view_fftBrightness(self, new_val : float):
		"""
		View --> Model
		Fft brightness slider changed
		Args:
			new_val (float): The new value of the fft brightness slider
		"""

		self.model.fft_brightness = new_val

	def process_view_fftQuality(self, new_val : float):
		"""
		View --> Model
		Fft quality slider changed
		Args:
			new_val (float): The new value of the fft quality slider
		"""
		self.model.fft_quality = new_val

	def process_view_fftColumn(self, new_column : str):
		"""
		View --> Model
		Fft column changed
		Args:
			new_column (str): The new column to be used for fft
		"""
		self.model.fft_column = new_column

	def process_view_fftLineRange(self, new_left_right : typing.List[int]):
		"""
		View --> Model
		Fft line range changed
		Args:
			new_left_right (typing.List[int]): The new left and right values of the fft line range
		"""
		self.model.fft_line_range_left = new_left_right[0]
		self.model.fft_line_range_right = new_left_right[1]

	def process_view_fftColorMap(self, new_map : str):
		"""
		View --> Model
		Fft colormap changed
		Args:
			new_map (str): The new colormap to be used for fft
		"""
		self.model.fft_color_map = new_map

	def process_view_labelerToggle(self, new_val : bool):
		"""
		View --> Model
		Labeler toggle changed
		Args:
			new_val (bool): The new checked state of the labeler toggle button
		"""
		self.model.labeler_toggle = new_val

	def process_view_fontSize(self, new_val : bool):
		self.model.font_size = new_val

	def process_view_normalizationToggle(self, new_val : bool):
		self.model.normalization_toggle = new_val

	def process_view_plotDomain(self, new_val):

		# log.debug(f"Model received : {new_val}")
		left, right = new_val #unpack left and right datetime
		self.model.plot_domain_limrange.left_val = left
		self.model.plot_domain_limrange.right_val = right
		# log.debug(f"Plotdomain model changed to : {self.model.plot_domain_limrange}")


	def process_view_plotList(self, plotlist):
		self.model.plot_list = plotlist

	def process_view_plottedLabels(self, plotlist):
		self.model.plotted_labels_list = plotlist

	# def process_view_viewDomainSlider(self, new_val):
	# 	# self.model.plot_domain_left =
	# 	print(new_val)

	# def process_view_viewDomainBoxes(self, new_val):
	# 	print(new_val)

	def process_view_xAxisChanged(self, new_xaxis : str):
		"""Set the new x-axis by name (pass column name) - if column is not found, x-axis is set to empty string, updates domains afterwards

		Args:
			new_xaxis (str): Name of the new column to be used as x-axis
		"""
		if new_xaxis not in self.data_model._df :
			# raise NameError(f"{new_axis_name}") #TODO: empty should be allowed
			log.debug(f"Trying to set datamodel axis to {new_xaxis} but column was not found, resetting to ' '")
			self.model.x_axis = ""
		else:
			self.model.x_axis = new_xaxis
				# def _update_domains(self):
		new_xlimrange = self.data_model.get_col_limrange(self.model.x_axis)
		self.model.plot_domain_limrange = new_xlimrange
		log.debug(f"Updated x limrange to {new_xlimrange}")

		# self._update_domains()



	def process_view_plotTypeChanged(self, new_val : str):
		self.model.plot_type = new_val


	def process_view_plotColorMethod(self, new_index : int):
		self.model.plot_color_method = self.model.plot_color_method_options[new_index]

	def process_view_plotColorColumn(self):
		cb = self.view.plot_settings.inner_settings.plot_colors_column_ComboBox
		self.model.plot_color_column = cb.currentText()

	def process_view_selectionGapFillMs(self, new_selection_gap_fill_ms : int):
		# self.view.plot_settings.inner_settings.
		self.model.selection_gap_fill_ms = new_selection_gap_fill_ms


	#======================  Outer settings --> model/plotter ===========================

	def save_plot_as(self, path):
		log.debug(f"Saving figure to {path}")





	def copy_plot_to_clipboard(self):
		try:
			with io.BytesIO() as buffer:
				self.plotter.canvas.figure.savefig(buffer)
				QtWidgets.QApplication.clipboard().setImage(QtGui.QImage.fromData(buffer.getvalue()))
				log.debug("Succesfully copied current canvas to clipboard")
		except Exception as err:
			log.warning(f"Could not copy figure to clipboard: {err}")


	def append_df_popup(self, df : pd.DataFrame, dt_column_df = "DateTime"):
		log.info("Now validating and trying to append df ")

		if not self.data_model.validate_df(df, inplace_try_fix=True):
			log.warning(f"Error when validating dataframe... Could not append it.")
			GuiUtility.create_qt_warningbox(f"Error when validating dataframe... Could not append it.", "Could not append data")
			return

		if dt_column_df in df.columns: #If datetime specified
			maxval = df.max(axis=0)["DateTime"] # get most recent entry
			minval = df.min(axis=0)["DateTime"] # get oldest entry
			minval = minval.to_pydatetime(minval)
			maxval = maxval.to_pydatetime(maxval)
			loadspec_diag = LoadTypeSelectionDialog(min_db_entrydate=minval, max_dbentry_date=maxval)
		else:
			loadspec_diag = LoadTypeSelectionDialog()

		loadspec_diag.setMinimumSize(500,0)
		loadspec_diag.exec()
		loadspecs = loadspec_diag.get_selection() #Get appending specifications
		if loadspecs.cancelled:
			log.warning("Cancelled append_df popup, discarding database and continuing...")
			return



		# fromtime = loadspecs.from_time.replace(tzinfo=local_timezone) #Assume filled time is local time
		# totime = loadspecs.to_time.replace(tzinfo=local_timezone)

		if dt_column_df in df.columns:
			mask = (df[dt_column_df] >=  loadspecs.from_time) & (df[dt_column_df] <= loadspecs.to_time)
			df = df[mask]
		self.data_model.load_existing_df(
			df, loadspecs.main_load_type == MainLoadType.APPEND,
			loadspecs.duplicate_policy == DuplicatePolicy.OVERWRITE
		)


	def append_df_from_file(self):
		log.info("Now trying to append a df from file...")

		fname = QtWidgets.QFileDialog.getOpenFileName(None, 'Open file',
				self.data_model.file_source, "Pickled dataframes or Excel Sheets (*.pkl *.*, *.xlsx)")
		success, msg, df = DfUtility.load_dataframe_using_file_extension(fname[0])
		if not success:
			GuiUtility.create_qt_warningbox(msg, "Error")
			return

		self.append_df_popup(df=df)





	def load_df_popup(self):
		"""
		Show a popup to load a dataframe from file
		"""
		fname = QtWidgets.QFileDialog.getOpenFileName(None, 'Open file', #type: ignore
				self.data_model.file_source, "Pickled dataframes or Excel Sheets (*.pkl *.*, *.xlsx)")

		try:
			if len(fname[0]) == 0 or fname[0] is None:
				#If nothing selected -> just return
				return
				
			self.data_model.load_from_file(fname[0])
		except Exception as ex:
			GuiUtility.create_qt_warningbox(str(ex), "Error")
			return


	def _save_df_base(self, fname : str, save_function : typing.Callable):
		"""Base function for saving dataframes - takes in the filepath and save function and creates a warning box on failure

		Args:
			fname (str): The full file path where to save the file (includes the file extension)
			save_function (callable): the function which will be called to save the dataframe. 
				Should be of form: [save_function(fname : str)] and should return a tuple with success and
				a return message
		"""
		if fname is not None and len(fname[0]) > 0:
			log.info(f"Trying to save to path {fname}")
			success, retval = save_function(fname[0])
			if not success:
				GuiUtility.create_qt_warningbox(retval, "Error")
		else:
			log.error(f"Could not save under name: {fname}")

	def save_df_popup(self):
		"""
		Show a popup to save the dataframe to file.
		"""
		log.debug(self.data_model.file_source.rsplit("\\", 1)[0])
		try:
			curpath = self.data_model.file_source.rsplit("\\", 1)[0] + \
				"\\"+ self.data_model.file_source.rsplit("\\")[-1].rsplit(".", 1)[0] + " - Copy.pkl"
		except Exception as ex: #pylint: disable=broad-exception-caught
			curpath = "."
		fname, _ = QtWidgets.QFileDialog.getSaveFileName(None, 'Save Location', #type: ignore
			curpath, "Pickled dataframe (*.pkl) ;; Excel sheet (*.xlsx)")
		self._save_df_base(fname=fname, save_function=self.data_model.save_df)

	def save_df_selection_only_popup(self):
		percentage = 0
		dflen = len(self.data_model._df)
		if dflen != 0:
			percentage = int((len(self.data_model._df_selection)) / dflen * 100)

		fname, _ = QtWidgets.QFileDialog.getSaveFileName(None, 'Save selection', #type: ignore
			self.data_model.file_source.rsplit("\\", 1)[0] + \
				"\\"+ self.data_model.file_source.rsplit("\\")[-1].rsplit(".", 1)[0] + \
				f" - Subselection ({percentage}%).pkl", "Pickled dataframe (*.pkl) ;; Excel sheet (*.xlsx)")
		self._save_df_base(fname=fname, save_function=self.data_model.save_df_selection)

	def save_df_not_hidden_only_popup(self):
		log.debug(self.data_model.file_source.rsplit("\\", 1)[0])
		percentage = 0
		dflen = len(self.data_model._df)
		if dflen != 0:
			percentage = int((dflen - len(self.data_model.hidden_datapoints)) / dflen * 100)
		fname = QtWidgets.QFileDialog.getSaveFileName(None, 'Save Not-Hidden Datapoints Only',
			self.data_model.file_source.rsplit("\\", 1)[0] + "\\"+ self.data_model.file_source.rsplit("\\")[-1].rsplit(".", 1)[0] + f" - Subselection ({percentage}%).pkl", "Pickled dataframe (*.pkl) ;; Excel sheet (*.xlsx)")
		self._save_df_base(fname=fname, save_function=self.data_model.save_df_not_hidden_only)

	def plotter_replot(self):
		print("Controller received signal to replot, passing on to plot_wrapper")
		self.plotter.replot()#self.data_model, self.model)

	def set_xlim_to_view(self):
		log.info(f"Setting xlim to current view: {self.plotter.canvas.ax_dict['main'].get_xlim()}")
		cur_xlim = self.plotter.canvas.ax_dict['main'].get_xlim()

		cur_type = self.data_model.get_column_type(self.model.x_axis)

		left, right = cur_xlim
		print(f"{cur_type} vs limrange: {self.model.plot_domain_limrange}")
		if isinstance(cur_type, pd.Timestamp) or isinstance(cur_type, np.datetime64) or pd.api.types.is_datetime64_any_dtype(cur_type):  #Pd.timestamp to datetime
			log.debug("Converting from datetime")
			if left is not None:
				left = matplotlib.dates.num2date(left).replace(tzinfo=None)
			if right is not None:
				right = matplotlib.dates.num2date(right).replace(tzinfo=None)

		self.model.plot_domain_left = left
		self.model.plot_domain_right = right


	def set_fft_lim_to_view(self):

		cur_ylim = self.plotter.canvas.ax_dict['main'].get_ylim()
		bottom, top = cur_ylim
		bottom = max(0.0, bottom) #Make sure bounded by 0/1
		top = min(1.0, top)

		#Set appropriate ranges
		if self.model.fft_line_range is not None and self.model.fft_line_range.max_val is not None and self.model.fft_line_range.min_val is not None:
			self.model.fft_line_range_left = type(self.model.fft_line_range.max_val) (self.model.fft_line_range.min_val + bottom * self.model.fft_line_range.max_val)
			self.model.fft_line_range_right = type(self.model.fft_line_range.max_val) (self.model.fft_line_range.min_val + top * self.model.fft_line_range.max_val)


	#=================================================================
	#======================  DataModel --> Model (Settings) ==========
	#=================================================================
	#Update ranges in settings when dataframe changes
	def process_data_label_columns_options(self): #If data label columns change

		label_columns = self.data_model.get_lbl_columns()

		#======= Plotted labels ======
		self.view.plot_settings.inner_settings.plotted_labels_selection_list.set_options(label_columns) #Plotted label columns

		newlabelist = []
		for label in self.model.plotted_labels_list: #Only available labels remain
			if label in self.data_model._df.columns:
				newlabelist.append(label)
		self.model.plotted_labels_list = newlabelist

		#========= Labeler =========
		labeling_options = list(set(self.data_model.get_lbl_columns() + self.model.label_column_presets)) #add options

		self.labeler_window_view.set_lbl_column_options(labeling_options) #Set label column options
		log.debug(f"Setting label column options to: {self.data_model.get_lbl_columns()}")


		#======== Plot color (column) =========
		plot_color_columns = [i for i in label_columns if i is not None and len(i) > 0]


		cb = self.view.plot_settings.inner_settings.plot_colors_column_ComboBox
		cb.blockSignals(True)
		cb.clear()
		cb.addItems(plot_color_columns) #First set selection options
		if self.model.plot_color_column not in plot_color_columns: #If plot color column not in option list -> try to select first usable column
			if plot_color_columns is None or len(plot_color_columns) == 0:
				self.model.plot_color_column = None #If no columns -> set to None
			else:
				self.model.plot_color_column = plot_color_columns[0] #Or to first available

		cb.blockSignals(False)


	# def process_model_plot_list_options(self):
	# 	# print(f"now passing on {options} to view")
	# 	log.debug(f"Setting column options to: {self.data_model.get_column_names()}")
	# 	self.view.plot_settings.inner_settings.plot_selector_list.set_options(self.data_model.get_column_names())
	# 	# combobox = self.view.plot_settings.inner_settings.plots1_combobox

	def process_data_x_axis_options(self):
		cb = self.view.plot_settings.inner_settings.x_axis_combobox
		log.debug(f"Setting view x-axis options to {self.data_model.get_column_names()}")
		cols = self.data_model.get_column_names()
		cols = sorted(cols, key=lambda x: self.model.column_sorter(x, self.model.default_all_column_sorting))
		cb.blockSignals(True)
		cb.clear() #Clear items
		cb.addItems([""] + cols)
		cb.blockSignals(False)


	def process_data_dfChanged(self): #TODO: create more specialized dfChanged methods (e.g. columnsChanged, labelColumnsChanged etc. )
		log.info(f"Now updating settings using data from changed df")

		#========== FFT ===========
		fft_columns = self.data_model.get_fft_columns()
		log.debug(f"FFT columns : {fft_columns}")
		if self.model.fft_column is not None and self.model.fft_column != "" and self.model.fft_column not in fft_columns.keys():
			self.model.fft_column = None #Reset fft column if it does not exist in new data

		# self.model.fft_line_range = self.data_model.update_fft_line_range(self.model.fft_column)
		try:
			linecount = fft_columns[self.model.fft_column]
			# self.model.fft_line_range.find_bounded(0, linecount)
			# self.model.fft_line_range.max_val = linecount
			# self.model.fft_line_range.min_val = 0
			self.model.fft_line_range = LimitedRange(
				0, linecount, self.model.fft_line_range.left_val, self.model.fft_line_range.right_val
			)
			# self.model.fft_line_range_left = 0
			# self.model.fft_line_range_right = linecount

		except KeyError as exe: #If bounds unknown
			self.model.fft_line_range = LimitedRange()
			pass

		#========== Plotcolumns ===========
		all_cols = self.data_model.get_column_names()
		all_cols_sorted = sorted(all_cols, key=lambda x: self.model.column_sorter(x, self.model.default_all_column_sorting))
		self.view.plot_settings.inner_settings.plot_selector_list.set_options(all_cols_sorted) #Set new options
		new_plot_list = []
		if self.data_model._df is not None: #If dataframe exists --> only load existing columns -> otherwise reset
			for cur_plotted in self.model.plot_list:
				if cur_plotted in self.data_model._df.columns:
					new_plot_list.append(cur_plotted)
			if len(new_plot_list) == 0: #If no columns -> reroll to default (where possible)
				for newname in self.model.plot_list_default:
					if newname in self.data_model._df.columns:
						new_plot_list.append(newname)

		self.plot_list = new_plot_list



		#=========== x-axis =========
		self.process_data_x_axis_options()

		if self.model.x_axis not in list(self.data_model.get_column_names()): #Reset X_axis if it does not exist in new column list
			log.debug("Changing x-axis...")
			if self.model._default_x_axis not in list(self.data_model.get_column_names()):
				self.model.x_axis = None
			else:
				self.model.x_axis = self.model._default_x_axis

		new_x_limrange = self.data_model.get_col_limrange(self.model.x_axis) #Get new xmin/xmax
		# if self.model.plot_domain_left < new_x_limrange.min_val
		self.model.plot_domain_limrange.copy_limits(new_x_limrange)
		if self.model.plot_domain_left == self.model.plot_domain_right:  #If new range does not overlap with old range -> set to min/max of new
			self.model.plot_domain_left = new_x_limrange.min_val
			self.model.plot_domain_right = new_x_limrange.max_val
		# self.model._plot_dom


		# self.process_labeler_columnOptionChanged(labeling_options)

		self.process_data_label_columns_options()

		# self.view.plot_settings.inner_settings.plot_colors_column_ComboBox.set_options(newlabelist)

		#============== Update everything ===========
		self.view_reload()



	#=================================================================
	#======================  Model --> View ==========================
	#=================================================================
	def view_reload(self):
		"""
		Reload the whole view based on the model
		"""
		log.info("Now refreshing view based on model")
		#NOTE: always keey _options() before their respective item, otherwise it is possible that the appropriate
		#  option cannot be selected
		self.process_model_fft_toggle()
		self.process_model_fft_column_options() #Do this before fft_column otherwise option not in combobox
		self.process_model_fft_column()
		self.process_model_fft_line_range()
		self.process_model_fft_brightness()
		self.process_model_fft_quality()
		self.process_model_fft_color_map_options()
		self.process_model_fft_color_map()
		self.process_model_font_size()
		self.process_model_plot_list()
		self.process_model_plotted_label_columns()
		self.process_model_x_axis()
		self.process_model_plot_type()
		self.process_model_plot_domain()
		self.process_model_color_method()
		self.process_model_selectionGapFillMs()




	def process_model_color_method(self):
		"""
		Model --> View
		Process the model change in color method
		"""
		inner = self.view.plot_settings.inner_settings
		inner.plot_colors_method_ComboBox.setCurrentText(self.model.plot_color_method)
		# log.debug(f"Kaas updating to: {self.model.plot_color_method}")
		inner.plot_colors_column_ComboBox.setCurrentText(self.model.plot_color_column)

	def process_model_fft_toggle(self):
		"""
		Model --> View
		Process the model change in fft toggle
		"""
		checkbox_fft_toggle = self.view.plot_settings.inner_settings.fft_toggle_btn
		checkbox_fft_toggle.setCheckState(
			QtCore.Qt.CheckState.Checked if self.model.fft_toggle else QtCore.Qt.CheckState.Unchecked
		)


	def process_model_fft_column(self):
		"""
		Model --> View
		Process the model change in fft column
		"""
		combo_box = self.view.plot_settings.inner_settings.fft_column_combobox
		combo_box.setCurrentText(self.model.fft_column)

	def process_model_fft_line_range(self):
		"""
		Model --> View
		Process the model change in fft line range
		"""
		rs = self.view.plot_settings.inner_settings.fft_lines_range_slider
		line_range = self.model.fft_line_range
		rs.blockSignals(True)
		rs.set_all(line_range)
		rs.blockSignals(False)

	def process_model_fft_brightness(self):
		"""
		Model --> View
		Process the model change in fft brightness
		"""
		slider_box_widget = self.view.plot_settings.inner_settings.fft_brightness_slider
		slider_box_widget.set_all(self.model.fft_brightness_limval)

	def process_model_fft_quality(self):
		"""
		Model --> View
		Process the model change in fft quality
		"""
		slider_box_widget = self.view.plot_settings.inner_settings.fft_quality_slider
		slider_box_widget.set_all(self.model.fft_quality_limval)

	def process_model_fft_color_map_options(self):
		"""
		Model --> View
		Process the model change in fft color map options
		"""

		combo_box = self.view.plot_settings.inner_settings.fft_color_map_dropdown
		combo_box.clear() #remove options
		combo_box.addItems(self.model.fft_color_map_options)

	def process_model_fft_color_map(self):
		"""
		Model --> View
		Process the model change in fft color map
		"""
		combo_box = self.view.plot_settings.inner_settings.fft_color_map_dropdown
		combo_box.setCurrentText(self.model.fft_color_map)

	def process_model_font_size(self):
		"""
		Model --> View
		Process the model change in font size
		"""
		slider_box_widget = self.view.plot_settings.inner_settings.font_size_selector
		slider_box_widget.set_all(self.model._font_size_limval) #TODO: prive, not very neat --> unprivate?



	def process_model_plot_domain(self):
		"""
		Model --> View
		Process the model change in plot domain
		"""

		log.debug(f"Processing model change in domain : {self.model.plot_domain_limrange}")
		domain_widget = self.view.plot_settings.inner_settings.plot_domain_widget
		# domain_widget.set_text([str(self.model.plot_domain_left), str(self.model.plot_domain_right)])

		domain_widget.set_all(self.model.plot_domain_limrange)

	def process_model_plot_list(self):
		"""
		Model --> View
		Process the model change in plot list
		"""

		self.view.plot_settings.inner_settings.plot_selector_list.set_selections(
			self.model.plot_list, reset_boxcount=False)
		log.debug(f"Setting plot_list in view to {self.model.plot_list}")


	def process_model_plotted_label_columns(self):
		"""
		Model --> View
		Process the model change in plotted label columns
		"""
		plotted_columns = self.model.plotted_labels_list
		self.view.plot_settings.inner_settings.plotted_labels_selection_list.set_selections(
			plotted_columns, reset_boxcount=False)


	# def process_model_file_source(self):
		# self.view.plot_settings.inner_settings.file_source_selector.set_cur_path(self.data_model.file_source)


	# def process_model_dfChanged(self):
	# 	log.debug("Df changed")
	# 	self.labeler_window_view.col_dropdown.set_options(list(set(self.data_model.get_lbl_columns() + self.model.label_column_presets))) #Set label column options

	# 	self.process_labeler_columnOptionChanged(self.labeler_window_view.col_dropdown.selection)#Also update possible columns
	# 	# self.process_model_plo
	# 	self.process_model_label_plotting_options()
	# 	self.process_model_x_axis_options()

	def process_model_plot_type(self):
		self.view.plot_settings.inner_settings.plot_type_combobox.setCurrentText(self.model._plot_type)
		# if self.df.dtypes[x_ax] ==
		log.debug(f"Setting plotting type to: {self.model._plot_type}")


	def process_model_x_axis(self):
		log.debug(f"Setting current xaxis text to: {self.model.x_axis}")
		cb = self.view.plot_settings.inner_settings.x_axis_combobox
		cb.blockSignals(True)
		cb.setCurrentText(self.model.x_axis)
		cb.blockSignals(False)
		# if self.df.dtypes[x_ax] ==

		# cols = self.data_model._df.columns if is None : [] ? columns
		# self.view.plot_settings.inner_settings.x_axis.set = self.data_model.get_column_names()

		# log.debug(f"Setting plot view x-axis to: {x_ax}")
		# if pd.api.types.is_string_dtype(self.model.df[x_ax]):
		# 	raise NotImplementedError("Can't handle x-axis of type string")
		# elif pd.api.types.is_numeric_dtype(self.model.df[x_ax]):
		# 	raise NotImplementedError("Can't handle x-axis of type numeric")
		# elif pd.api.types.is_datetime64_any_dtype(self.model.df[x_ax]):
		# 	print("Now selecting x_axis of type datetime")
		# else:
		# 	raise NotImplementedError(f"Can't handle x-axis of type {type(self.model.df[x_ax])}")
		# self.view.v


	# def process_model_label_column_options(self):

	def process_model_fft_column_options(self):
		fft_cols_lines = self.data_model.get_fft_columns()

		cb = self.view.plot_settings.inner_settings.fft_column_combobox
		cb.blockSignals(True)
		cb.clear() #Clear items
		cb.addItems([""] + list(fft_cols_lines.keys()))
		log.debug(f"FFT column options are: {[''] + list(fft_cols_lines.keys())}")
		cb.blockSignals(False)

	def process_model_plotColorMethod(self, color_method : str, color_column : str) -> None:
		inner = self.view.plot_settings.inner_settings
		inner.plot_colors_method_ComboBox.setCurrentText(color_method)
		inner.plot_colors_column_ComboBox.setCurrentText(color_column)

	def process_model_selectionGapFillMs(self) -> None:
		slider_box_widget = self.view.plot_settings.inner_settings.plot_select_gapfill_slider_with_box
		slider_box_widget.set_all(self.model._selection_gap_fill_ms_limval) #TODO: prive, not very neat --> unprivate?


	#================================ Combination events ====================================
	def process_model_dfColumnsChanged(self): #When column changes
		self.process_model_x_axis_options()



	def reset_plot_settings(self):
		self.model.reset_all_settings_to_default()
		self.process_data_dfChanged()

	def reset_plot_domain(self):
		self.model.plot_domain_left = self.model.plot_domain_limrange.min_val
		self.model.plot_domain_right = self.model.plot_domain_limrange.max_val





	#=====================================
	#===========Staticmethods ============
	#=====================================
	@staticmethod
	def open_view_window( graph_data_model : GraphData = None, graph_settings_model : GraphSettingsModel = None, parent : QtCore.QObject= None):
		new_win = GraphSettingsViewWindow(graph_data_model, graph_settings_model, parent=parent)
		new_win.show()
		return new_win




	# 	assert(graph_settings_model is None or type(graph_settings_model) == type(GraphSettingsModel))
	# 	self.view_window = QtWidgets.QMainWindow(self)
	# 	r = QtGui.QGuiApplication.primaryScreen().geometry()
	# 	r.setSize(QtCore.QSize( 0.6* r.width(),0.6* r.height()))
	# 	self.view_window.setGeometry(r)

	# 	graph_settings_model = GraphSettingsModel()
	# 	if graph_settings_model is not None:
	# 		graph_settings_model.copy_attrs(self.graph_settings_model)
	# 		# graph_settings_model = GraphSettingsView(plotter) # Create View (using created plotter)
	# 		# graph_settings. =
	# 	# graph_data_model = GraphData(**graph_model_args)
	# 	plotter = QPlotter(self.graph_data_model, graph_settings_model)
	# 	graph_view = GraphSettingsView(plotter) #Create model
	# 	graph_controller = GraphSettingsController(self.graph_data_model, graph_settings_model, graph_view, plotter)
	# 	self.view_window.setCentralWidget(graph_view)
	# 	self.view_window.show()
	# 	self.view_window.onde

	# 	return graph_settings_model, graph_view, plotter

