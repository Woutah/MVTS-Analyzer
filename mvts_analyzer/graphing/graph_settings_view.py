"""
Contains the Plotsettings-view classes for the GUI without buttons etc.
Not created using a .ui file due to the fact that we want to display the widgets in a tree-view.
Might be better to create a custom model/view with widgets for each type.
"""
import logging

from PySide6 import QtCore, QtGui, QtWidgets

from mvts_analyzer.graphing.plotter.plot_wrapper import QPlotter
from mvts_analyzer.widgets import (combobox_list, datetime_range,
                                   range_slider_with_box,
                                   range_sliders_with_boxes, variable_range)
from mvts_analyzer.widgets.collapsible_groupbox import \
    CollapsibleGroupBoxLayout
from mvts_analyzer.windows.labeler_window import LabelerWindowView

#pylint: disable=invalid-name #Allow camelcase for Qt objects

log = logging.getLogger(__name__)

class PlotSettingsInnerView(QtWidgets.QTreeWidget):
	"""
	Only the settings without buttons etc.
	Not created using a .ui file due to the fact that we want to display the widgets in a tree-view.
	Might be better to create a custom model/view with widgets for each type.
	"""

	fftToggleBtnChanged = QtCore.Signal(bool)
	fftBrightnessChanged = QtCore.Signal(float)
	fftQualityChanged = QtCore.Signal(float)
	fftColumnSelectorChanged = QtCore.Signal(str)
	fftLineRangeChanged = QtCore.Signal(object) #[newleft, newright]
	fftTransparencyChanged = QtCore.Signal(float)
	fftColorMapChanged = QtCore.Signal(str)

	labelerToggleChanged = QtCore.Signal(bool)
	normalizationToggleChanged = QtCore.Signal(bool)

	plotDomainChanged = QtCore.Signal(object) #Emits [min, max] of sliders
	plotListChanged = QtCore.Signal(object)
	plottedLabelsChanged = QtCore.Signal(object)

	fontSizeChanged = QtCore.Signal(object)
	viewDomainSliderChanged = QtCore.Signal(object)
	viewDomainBoxesChanged = QtCore.Signal(object) #[str, str]

	xAxisChanged = QtCore.Signal(str)
	plotTypeChanged = QtCore.Signal(str)
	selectionGapFillMsChanged = QtCore.Signal(int)



	def __init__(self, *args, **kwargs):
		super(PlotSettingsInnerView, self).__init__(*args, **kwargs)
		self.setWindowTitle('Treeview')
		self.resize(700, 1200)
		self.setColumnWidth(0, 150)
		self.setHeaderLabels(["Name", "Value"])


		#=============== FFT ======================
		self.fft_header = QtWidgets.QTreeWidgetItem(self.invisibleRootItem())
		self.fft_header.setText(0, "Fourier")
		self.fft_header.setExpanded(False)


		self.fft_toggle = QtWidgets.QTreeWidgetItem(self.fft_header)
		self.fft_toggle.setText(0, "On/Off")
		self.fft_toggle_btn = QtWidgets.QCheckBox()
		self.fft_toggle_btn.stateChanged.connect(lambda: self.fftToggleBtnChanged.emit(self.fft_toggle_btn.isChecked()))
		self.fft_toggle.treeWidget().setItemWidget(self.fft_toggle, 1, self.fft_toggle_btn)



		self.fft_column_header = QtWidgets.QTreeWidgetItem(self.fft_header)
		self.fft_column_header.setText(0, "FFT Column")
		self.fft_column_combobox = QtWidgets.QComboBox()
		self.fft_column_combobox.currentTextChanged.connect(self.fftColumnSelectorChanged)
		self.fft_column_header.treeWidget().setItemWidget(self.fft_column_header, 1, self.fft_column_combobox)


		self.fft_lines_range_tree_item = QtWidgets.QTreeWidgetItem(self.fft_header)
		self.fft_lines_range_tree_item.setText(0, "Lines Range")
		self.fft_lines_range_slider = range_sliders_with_boxes.RangeSlidersWithBoxes()
		self.fft_lines_range_slider.rangeEdited.connect(self.fftLineRangeChanged)
		self.fft_lines_range_tree_item.treeWidget().setItemWidget(
			self.fft_lines_range_tree_item, 1, self.fft_lines_range_slider)

		self.fft_brightness = QtWidgets.QTreeWidgetItem(self.fft_header)
		self.fft_brightness_slider = range_slider_with_box.RangeSliderWithBox(text_parser=float)
		self.fft_brightness.treeWidget().setItemWidget(self.fft_brightness, 1, self.fft_brightness_slider)
		self.fft_brightness_slider.valueEdited.connect(lambda x: self.fftBrightnessChanged.emit(float(x)))
		self.fft_brightness.setText(0, "Brightness")

		self.fft_quality = QtWidgets.QTreeWidgetItem(self.fft_header)
		self.fft_quality_slider = range_slider_with_box.RangeSliderWithBox(
			text_parser=float, text_converter=lambda x: str(round(x, 2)))
		self.fft_quality.treeWidget().setItemWidget(self.fft_quality, 1, self.fft_quality_slider)
		self.fft_quality_slider.valueEdited.connect(lambda x: self.fftQualityChanged.emit(float(x)))
		self.fft_quality.setText(0, "Quality")

		self.fft_color_map = QtWidgets.QTreeWidgetItem(self.fft_header)
		self.fft_color_map_dropdown = QtWidgets.QComboBox()
		self.fft_color_map.treeWidget().setItemWidget(self.fft_color_map, 1, self.fft_color_map_dropdown)
		self.fft_color_map_dropdown.currentTextChanged.connect(self.fftColorMapChanged) #TODO: check
		self.fft_color_map.setText(0, "Color Map")

		#============== Plot domain ==============
		self.plot_domain = QtWidgets.QTreeWidgetItem(self.invisibleRootItem())
		self._plot_domain_dt_widget = datetime_range.DateTimeRange(enforce_limits=False)
		self._plot_domain_num_widget = range_sliders_with_boxes.RangeSlidersWithBoxes()

		self.plot_domain_widget = variable_range.VariableRange(self._plot_domain_num_widget, self._plot_domain_dt_widget)

		self.plot_domain.treeWidget().setItemWidget(self.plot_domain, 1, self.plot_domain_widget)
		self.plot_domain_widget.rangeEdited.connect(self.plotDomainChanged)

		self.plot_domain.setText(0, "Plot Domain")

		#============== Plotlist ============
		self.plots_header = QtWidgets.QTreeWidgetItem(self.invisibleRootItem())
		self.plots_header.setText(0, "Plot Columns")
		self.plots_header.setExpanded(True)


		self.plot_footer = QtWidgets.QTreeWidgetItem(self.plots_header)
		self.plot_selector_list = combobox_list.ComboboxList()
		self.plot_selector_list.set_widgetcount(4)
		self.plot_selector_list.selectionsChanged.connect(self.plotListChanged)
		self.plot_footer.treeWidget().setItemWidget(self.plot_footer, 1, self.plot_selector_list)

		#TODO: If we don't fold/unfold, size doesn't propagate correctly - do this in a better way
		self.plot_selector_list.widgetCountChanged.connect(lambda: self.plots_header.setExpanded(False))
		self.plot_selector_list.widgetCountChanged.connect(
			lambda: QtCore.QTimer.singleShot(1, lambda: self.plots_header.setExpanded(True)))

		#============= Plotted Labels List ===============
		self.plotted_labels_header = QtWidgets.QTreeWidgetItem(self.invisibleRootItem())
		self.plotted_labels_header.setText(0, "Label Columns")
		self.plotted_labels_header.setExpanded(True)


		self.plotted_labels_footer = QtWidgets.QTreeWidgetItem(self.plotted_labels_header)
		self.plotted_labels_selection_list = combobox_list.ComboboxList()
		self.plotted_labels_selection_list.set_widgetcount(2)
		self.plotted_labels_selection_list.selectionsChanged.connect(self.plottedLabelsChanged)
		self.plotted_labels_footer.treeWidget().setItemWidget(
			self.plotted_labels_footer, 1, self.plotted_labels_selection_list)

		#TODO: If we don't fold/unfold, size doesn't propagate correctly - do this in a better way
		self.plotted_labels_selection_list.widgetCountChanged.connect(lambda: self.plotted_labels_header.setExpanded(False))
		self.plotted_labels_selection_list.widgetCountChanged.connect(
			lambda: QtCore.QTimer.singleShot(1, lambda: self.plotted_labels_header.setExpanded(True)))



		#============= Font size ============
		self.font_size_tree_item = QtWidgets.QTreeWidgetItem(self.invisibleRootItem())
		self.font_size_selector = range_slider_with_box.RangeSliderWithBox(text_parser=int, text_converter=str)
		self.font_size_selector.valueEdited.connect(self.fontSizeChanged)
		self.font_size_tree_item.treeWidget().setItemWidget(self.font_size_tree_item, 1, self.font_size_selector)
		self.font_size_tree_item.setText(0, "Font Size")

		#============== X-axis =============
		self.x_axis = QtWidgets.QTreeWidgetItem(self.invisibleRootItem())
		self.x_axis_combobox = QtWidgets.QComboBox()
		self.x_axis_combobox.currentTextChanged.connect(self.xAxisChanged)
		self.x_axis.treeWidget().setItemWidget(self.x_axis, 1, self.x_axis_combobox)
		self.x_axis.setText(0, "X-Axis")

		#============== Plot Type (Scatter/Line) ===========
		self.plot_type_tree_item = QtWidgets.QTreeWidgetItem(self.invisibleRootItem())
		# plot_type_combobox = QtWidgets.QTreeWidgetItem(plot_type)
		self.plot_type_tree_item.setText(0, "Plot Type")
		self.plot_type_combobox = QtWidgets.QComboBox()
		self.plot_type_combobox.addItems(["Line", "Scatter"])
		self.plot_type_combobox.currentTextChanged.connect(self.plotTypeChanged)
		self.plot_type_tree_item.treeWidget().setItemWidget(self.plot_type_tree_item, 1, self.plot_type_combobox)


		#============== Coloring Type =======================
		self.plot_colors_tree_item = QtWidgets.QTreeWidgetItem(self.invisibleRootItem())
		self.plot_colors_tree_item.setText(0, "Plot Colors")

		self.plot_colors_VLayout = QtWidgets.QHBoxLayout()

		self.plot_colors_method_ComboBox = QtWidgets.QComboBox()
		self.plot_colors_method_ComboBox.addItems(["Based On Column", "Based On Labels"])
		self.plot_colors_VLayout.addWidget(self.plot_colors_method_ComboBox)


		self.plot_colors_StackedWidget = QtWidgets.QStackedWidget()
		self.plot_colors_VLayout.addWidget(self.plot_colors_StackedWidget)


		self.plot_colors_column_emptylabel =  QtWidgets.QLabel()
		self.plot_colors_StackedWidget.addWidget(self.plot_colors_column_emptylabel)

		self.plot_colors_column_ComboBox =  QtWidgets.QComboBox()
		self.plot_colors_column_ComboBox.addItems(["None"])
		self.plot_colors_StackedWidget.addWidget(self.plot_colors_column_ComboBox)

		self.plot_colors_widget = QtWidgets.QWidget()
		self.plot_colors_widget.setLayout(self.plot_colors_VLayout)

		self.plot_colors_tree_item.treeWidget().setItemWidget(self.plot_colors_tree_item, 1, self.plot_colors_widget)


		#=========== Selection ====================
		self.plot_select_gapfill_ms_tree_item = QtWidgets.QTreeWidgetItem(self.invisibleRootItem())
		self.plot_select_gapfill_ms_tree_item.setText(0, "Selection Threshold (ms)")
		self.plot_select_gapfill_slider_with_box = range_slider_with_box.RangeSliderWithBox(
			text_parser=int, text_converter=str)
		self.plot_select_gapfill_ms_tree_item.treeWidget().setItemWidget(
			self.plot_select_gapfill_ms_tree_item, 1, self.plot_select_gapfill_slider_with_box)


		#=========== Shortcuts / actions ==============












class PlotSettings(QtWidgets.QWidget):
	"""
	The outer plotsettings - includes the scrollable inside as well as the update/save buttons on the top/bottom
	"""
	fftZoomViewSignal = QtCore.Signal()
	replotViewSignal = QtCore.Signal()
	replotViewSignal = QtCore.Signal()
	updateSignal = QtCore.Signal()
	saveDfSignal = QtCore.Signal()
	toggleLabelerSignal = QtCore.Signal()

	def __init__(self, *args, **kwargs):
		super(PlotSettings, self).__init__(*args, **kwargs)
		self.settings_layout = QtWidgets.QVBoxLayout(self)

		#===============Config-tree-gui====================
		# self.config_gui = config_gui.ConfigTree(self.plot_data.config)
		# print(f"Child found: {self.config_gui.findChild(conf_base.ConfBase, 'view/xlim')}")
		self.inner_settings = PlotSettingsInnerView()

		#=============== Labeler ============
		# self.labeler_groupbox = QtWidgets.QGroupBox("Labeler")
		self.labeler_groupbox = CollapsibleGroupBoxLayout("Labeler")
		# self.labeler_groupbox.setCheckable(False)
		self.labeler_groupbox.setSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Maximum)
		self.labeler_groupbox.setContentsMargins(0, 0, 0, 0)
		self.labeler_groupbox.setStyleSheet('QGroupBox  {border: 0.5px solid #8b909a;}')

		# self.labeler_layout = QtWidgets.QHBoxLayout()

		self.labeler_window_view = LabelerWindowView()
		self.labeler_groupbox.addWidget(self.labeler_window_view)
		# self.labeler_groupbox.setLayout(self.labeler_layout)
		# self.labeler_window_view.setSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Maximum)

		#=============Update-bar===================
		self.update_button = QtWidgets.QPushButton(text="Update")
		# self.update_button.clicked.connect(self.on_update_click)
		self.update_button.clicked.connect(self.updateSignal)

		#, QtCore.QSize(), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On)
		self.update_button.setIcon(QtGui.QIcon(":/Icons/icons/Tango Icons/actions/view-refresh.svg"))
		self.replot_view_button = QtWidgets.QPushButton(text="Replot View (X)")
		self.replot_view_button.clicked.connect(self.replotViewSignal)
		self.replot_view_button.setIcon(QtGui.QIcon(":/Icons/icons/Custom Icons/toview.svg"))

		self.fft_zoom_button = QtWidgets.QPushButton(text="Replot View (Vertical range FFT)")
		self.fft_zoom_button.clicked.connect(self.fftZoomViewSignal)
		self.fft_zoom_button.setIcon(QtGui.QIcon(":/Icons/icons/Custom Icons/fftview.svg"))

		self.sub_btn_layout = QtWidgets.QHBoxLayout()
		self.btn_layout = QtWidgets.QVBoxLayout()

		self.sub_btn_layout.addWidget(self.replot_view_button)
		self.sub_btn_layout.addWidget(self.fft_zoom_button)

		self.btn_layout.addLayout(self.sub_btn_layout)
		self.btn_layout.addWidget(self.update_button)

		#===========Adding everything to layout===========
		self.settings_layout.addWidget(self.inner_settings)
		self.settings_layout.addWidget(self.labeler_groupbox)
		self.settings_layout.addLayout(self.btn_layout)

		self.setLayout(self.settings_layout)





class GraphSettingsView(QtWidgets.QWidget):
	"""
	The graph-settings view - most outer widget that contains the plotter and the settings and divides the available
	space using a splitter
	"""
	xlimChangedSignal = QtCore.Signal()
	# def __init__(self, plot_data, matplot_plotter, *args, **kwargs):
	def __init__(self, plotter : QPlotter, *args, **kwargs):
		super(GraphSettingsView, self).__init__(*args, **kwargs)
		log.debug("initializing GraphSettings view")

		#################GUI##################
		self.main_layout = QtWidgets.QVBoxLayout(self)


		#=================Layout Splitter (plot left + settings right)=================
		self.plot_splitter = QtWidgets.QSplitter(self)
		self.plot_splitter.setOrientation(QtCore.Qt.Orientation.Horizontal)
		self.main_layout.addWidget(self.plot_splitter)

		# #================= Plot adder =============
		self.plot_adder_layout = QtWidgets.QHBoxLayout()
		self.main_layout.addLayout(self.plot_adder_layout)

		################################## Matplotlib plot layout (left) #########################################
		self.plotter = plotter
		self.plot_splitter.addWidget(self.plotter)


		#################################### Plot Settings layout  ###############################################
		self.plot_settings = PlotSettings()
		self.plot_splitter.addWidget(self.plot_settings)

		self.setLayout(self.main_layout)



		#==========Some shortcuts ===========
		self.actionCopy_Figure_To_Clipboard = QtGui.QAction(plotter)
		self.actionCopy_Figure_To_Clipboard.setObjectName("actionCopy_Figure_To_Clipboard")
		self.actionCopy_Figure_To_Clipboard.setShortcut("Ctrl+C")
		self.addAction(self.actionCopy_Figure_To_Clipboard)

		self.actionCopy_Figure_To_Clipboard.triggered.connect(lambda x : "Trying to copy figure in graphsettingsview")
