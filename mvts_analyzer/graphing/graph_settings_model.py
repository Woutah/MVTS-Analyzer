"""
Implements:
GraphSettingsModelData - The actual data behind the displayed graph
GraphSettingsModel - A Qt-Wrapper around GraphSettingsModelData that emits signals when data changes so the UI can be
	updated
"""

from __future__ import annotations

import datetime
import json
import logging
import typing

import matplotlib
import matplotlib.pyplot
from PySide6 import QtCore

from mvts_analyzer.widgets.datastructures import LimitedRange, LimitedValue

log = logging.getLogger(__name__)
matplotlib.use('Qt5Agg')
#pylint: disable=missing-function-docstring


class GraphSettingsModelData():
	"""
	Contains the plot-settings-data (which is not saved to file) e.g. what columns to plot, what color to plot
	them in, etc.
	"""
	def __init__(self) -> None:
		super().__init__()  #TODO: Not sure why but this is needed when inheriting in inheriting from both this and QObject
		log.debug("Initializing plotsettings")



		self._fft_transparency : float = 1.0
		self._fft_toggle : bool = False
		self.fft_brightness_limval : LimitedValue = LimitedValue(0.0, 1.0, 0.5)
		# self.fft_brightness_limval.changed.connect(self.changed) #Connect changes

		self.fft_quality_limval : LimitedValue = LimitedValue(0.1, 1.0, 1.0)


		self._fft_color_map= matplotlib.pyplot.colormaps()[0] #type: ignore #NOTE: submodule not picked up by vscode?
		# self._fft_color_map_options = matplotlib.pyplot.colormaps()
		self._fft_color_map_options = [ "viridis", "BlueYellowRed", "inferno", "magma", "plasma", "cividis", "gnuplot"]

		self._fft_column = "" #TODO: make choice?
		self._fft_line_range : LimitedRange = LimitedRange(
			None,
			None,
			None,
			None
		)

		self._labeler_toggle = False

		self._normalization_toggle = False
		self._font_size_limval : LimitedValue = LimitedValue( 4, 30, 10) #Font sizes for plotting

		# self.plot_domain_limrange = LimitedRange(0, 10, 0, 10)
		self._plot_domain_limrange : LimitedRange = LimitedRange(
										datetime.datetime(2020, 1, 1, 1, 0, 0),
										datetime.datetime(2021, 1, 1, 1, 0, 0),
										datetime.datetime(2020, 1, 1, 1, 0, 0),
										datetime.datetime(2021, 1, 1, 1, 0, 0),
									)



		self._plot_list : typing.List[str] = []
		self.plot_list_default : typing.List[str]= ["Depth(m)"]

		self._plotted_labels_list = []

		self._x_axis : str = "DateTime"
		self._plot_type : str = "Line"
		self._default_x_axis : str = "DateTime"
		self._plot_font_size : int = 10

		self.label_column_presets : typing.List[str] = []
		self.label_column_options_presets : typing.Dict[str, typing.List[str]] = {}


		self.default_all_column_sorting : typing.List[str] = [ #For dropdown menu
			'DateTime'
		]


		self._plot_color_method : str = "Based On Column"
		self.plot_color_method_options : typing.List[str] = ["Based On Column", "Based On Labels"]
		self._plot_color_column : str = ""

		self.plot_filters= []
		#When selecting data, how many millisecond gaps should also be selected
		# (e.g. t=1, t=3, then if GapFillMs=1000, t=2 would also be selected)
		self._selection_gap_fill_ms_limval : LimitedValue = LimitedValue( 0, 10000, 0)

	def reset_all_settings_to_default(self): #Reset all to default
		self.copy_attrs(GraphSettingsModelData())

	@staticmethod
	def column_sorter(comp : tuple, default_sorting : list):
		"""A sorter which can be passed to the sorted() method (e.g.
			sorted(alist, key=lambda x: column_sorter(x, default_sorting)))
			Sorts first by [default_sorting]. then alphabetically.

			E.g:
			default_sorting = [b, c, d]
			sorted([b, a, c], key=lambda x: column_sorter(x, default_sorting))

			Will result in:
			[b, c, a]

		Args:
			curcol (str): The current column for which a sorting-score should be calculated
			default_sorting (typing.Iterable): The default sorting
		"""

		try:
			sort_val = default_sorting.index(comp)
		except ValueError:
			sort_val = 100000

		return (sort_val, comp)

		# if a == b: #If both not in default_sorting
		# 	return comp[1] < comp[2]


	def copy_attrs(self, data : GraphSettingsModelData):
		"""Copy all attributes from data to self"""
		self.__dict__.update(data.__dict__)


class GraphSettingsModel(GraphSettingsModelData, QtCore.QObject):
	#Note: The order of inheritance is important here -> In pyqt5 the order is different than pyside6
	"""
	Qt-Wrapper around GraphSettingsModelData that emits signals when data changes
	"""


	changed = QtCore.Signal(object)
	dfColumnsChanged = QtCore.Signal(object) #When columns change

	fftColumnChanged = QtCore.Signal(object)
	fftToggleChanged = QtCore.Signal(object)
	fftLineRangeChanged = QtCore.Signal(object) #When fftLineRange (Which lines of fft should be plotted) changes
	fftBrightnessChanged = QtCore.Signal(object)
	fftQualityChanged = QtCore.Signal(float)

	fftColorMapChanged = QtCore.Signal(object)

	fontSizeChanged = QtCore.Signal(object)

	labelerToggleChanged = QtCore.Signal(object)
	normalizationToggleChanged = QtCore.Signal(object)
	plotDomainLimrangeChanged = QtCore.Signal(object)
	plotListChanged = QtCore.Signal(object)
	# plotListOptionsChanged = QtCore.Signal(object)

	plottedLabelsChanged = QtCore.Signal(object)
	viewDomainChanged = QtCore.Signal(object)
	xAxisChanged = QtCore.Signal(object)
	plotTypeChanged = QtCore.Signal(str)


	plotColorMethodChanged = QtCore.Signal(str, str) #Type ("Based On Column" / "Based On Labels")

	selectionGapFillMsChanged = QtCore.Signal(int)


	# def __init__(self):
	# 	super().__init__()

	@property
	def plot_color_method(self) -> str:
		return self._plot_color_method

	@plot_color_method.setter
	def plot_color_method(self, new_value : str):
		log.debug(f"Plot coloring type set to {new_value}")
		if new_value != self._plot_color_method:
			self._plot_color_method = new_value
			self.changed.emit(self)
			self.plotColorMethodChanged.emit(self._plot_color_method, self._plot_color_column)
	@property
	def plot_color_column(self) -> str:
		return self._plot_color_column

	@plot_color_column.setter
	def plot_color_column(self, new_value : str):
		log.debug(f"Plot coloring column set to {new_value}")
		if new_value != self._plot_color_column:
			self._plot_color_column = new_value
			self.changed.emit(self)
			self.plotColorMethodChanged.emit(self._plot_color_method, self._plot_color_column)


	@property
	def fft_toggle(self) -> bool:
		return self._fft_toggle

	@fft_toggle.setter
	def fft_toggle(self, new_value : bool):
		log.debug(f"Fft toggled to {new_value}")
		if new_value != self._fft_toggle:
			self._fft_toggle = new_value
			self.changed.emit(self)
			self.fftToggleChanged.emit(self._fft_toggle)


	@property
	def fft_column(self) -> str | None:
		return self._fft_column

	@fft_column.setter
	def fft_column(self, new_col : typing.Optional[str]):
		if new_col != self._fft_column:
			log.debug(f"FFT column now {new_col}")
			# self._fft_toggle = new_value
			self._fft_column = new_col
			self.changed.emit(self)
			self.fftColumnChanged.emit(self._fft_toggle)

	@property
	def fft_transparency(self) -> float:
		return self._fft_transparency


	@property
	def fft_line_range_left(self) -> int:
		return self._fft_line_range.left_val #type: ignore

	@fft_line_range_left.setter
	def fft_line_range_left(self, new_left : int):
		if self.fft_line_range_left is not new_left:
			self._fft_line_range.left_val = new_left
			self.fftLineRangeChanged.emit(self._fft_line_range)
			self.changed.emit(self)

	@property
	def fft_line_range_right(self) -> int:
		return self._fft_line_range.right_val #type: ignore

	@fft_line_range_right.setter
	def fft_line_range_right(self, new_right : int):
		if self.fft_line_range_right is not new_right:
			self._fft_line_range.right_val = new_right
			self.fftLineRangeChanged.emit(self._fft_line_range)
			self.changed.emit(self)

	@property
	def fft_line_range(self):
		return self._fft_line_range

	@fft_line_range.setter
	def fft_line_range(self, new_range : LimitedRange):
		if self.fft_line_range is not new_range:
			self._fft_line_range = new_range
			self.fftLineRangeChanged.emit(self._fft_line_range)
			self.changed.emit(self)

	@property
	def fft_line_range_max(self) -> int:
		return self._fft_line_range.max_val #type: ignore




	@property
	def fft_brightness(self) -> float:
		return self.fft_brightness_limval.val #type: ignore #Is set using float, so returns float


	@fft_brightness.setter
	def fft_brightness(self, new_brightness : float):
		if self.fft_brightness_limval.val is not new_brightness:
			self.fft_brightness_limval.val = new_brightness
			self.fftBrightnessChanged.emit(self.fft_brightness_limval)
			self.changed.emit(self)

	@property
	def fft_quality(self) -> float:
		return self.fft_quality_limval.val #type: ignore #Is set using float, so returns float


	@fft_quality.setter
	def fft_quality(self, new_quality : float):
		if self.fft_quality_limval.val is not new_quality:
			log.debug(f"Quality is now {new_quality}")
			self.fft_quality_limval.val = new_quality
			self.fftQualityChanged.emit(self.fft_quality_limval.val)
			self.changed.emit(self)

	@property
	def font_size(self) -> float:
		return self._font_size_limval.val #type: ignore #Is set using float, so returns float


	@font_size.setter
	def font_size(self, new_fontsize : float):
		if self._font_size_limval.val is not new_fontsize:
			self._font_size_limval.val = new_fontsize
			self.fontSizeChanged.emit(self._font_size_limval)
			self.changed.emit(self)

	@property
	def fft_color_map(self) -> str:
		return self._fft_color_map

	@fft_color_map.setter
	def fft_color_map(self, new_color_map : str):
		#TODO: check if color map exists? if not --> error
		if new_color_map != self._fft_color_map:
			self._fft_color_map = new_color_map
			self.fftColorMapChanged.emit(self._fft_color_map)
			self.changed.emit(self)


	@property
	def fft_color_map_options(self) -> typing.List[str]:
		return self._fft_color_map_options

	@fft_color_map_options.setter
	def fft_color_map_options(self, new_colormap_options : typing.List[str]):
		if new_colormap_options != self._fft_color_map_options:
			self._fft_color_map_options = new_colormap_options
			self.fftColorMapChanged.emit(self._fft_color_map_options)
			self.changed.emit(self)

	@property
	def labeler_toggle(self) -> bool:
		return self._labeler_toggle

	@labeler_toggle.setter
	def labeler_toggle(self, new_value : bool):
		if self._labeler_toggle != new_value:
			self._labeler_toggle = new_value
			self.labelerToggleChanged.emit(self._labeler_toggle)
			self.changed.emit(self)

	@property
	def normalization_toggle(self) -> bool:
		return self._normalization_toggle

	@normalization_toggle.setter
	def normalization_toggle(self, new_value : bool):
		if self._normalization_toggle != new_value:
			log.debug(new_value)
			self._normalization_toggle = new_value
			self.normalizationToggleChanged.emit(self._normalization_toggle)
			self.changed.emit(self)

	@property
	def plot_domain_limrange(self) -> typing.Any:
		return self._plot_domain_limrange

	@plot_domain_limrange.setter
	def plot_domain_limrange(self, new_limrange):
		if self._plot_domain_limrange != new_limrange:
			self._plot_domain_limrange = new_limrange
		# self.plotDomainChanged.emit([self.plot_domain_limrange.left_val, self.plot_domain_limrange.right_val])
			log.debug(f"Model plot domain changed to: {self._plot_domain_limrange}")
			self.plotDomainLimrangeChanged.emit(self._plot_domain_limrange)


	@property
	def plot_domain_left(self):
		return self.plot_domain_limrange.left_val

	@plot_domain_left.setter
	def plot_domain_left(self, new_left):
		if self.plot_domain_limrange.left_val != new_left:
			self.plot_domain_limrange.left_val = new_left
			self.plotDomainLimrangeChanged.emit(self._plot_domain_limrange)

	@property
	def plot_domain_right(self):
		return self.plot_domain_limrange.right_val

	@plot_domain_right.setter
	def plot_domain_right(self, new_right):
		if self.plot_domain_limrange.right_val != new_right:
			self.plot_domain_limrange.right_val = new_right
			self.plotDomainLimrangeChanged.emit(self._plot_domain_limrange)



	@property
	def plot_list(self) -> typing.List[str]:
		return self._plot_list

	@plot_list.setter
	def plot_list(self, new_plotlist : typing.List[str]):
		log.debug(f"Trying to set model plotlist to {new_plotlist}")
		if self._plot_list != new_plotlist:
			log.debug(f"Setting model plotlist to {new_plotlist}")
			self._plot_list = new_plotlist
			self.plotListChanged.emit(self._plot_list)
			self.changed.emit(self)

	@property
	def plotted_labels_list(self) -> typing.List[str]:
	# def plotted_labels_list(self) -> typing.List[str]:
		return self._plotted_labels_list

	@plotted_labels_list.setter
	def plotted_labels_list(self, new_plotlist : typing.List[str]):
		log.debug(f"Trying to set model plotted_label_list to {new_plotlist}")
		if self._plotted_labels_list != new_plotlist:
			log.debug(f"Setting model plotted_label_list to {new_plotlist}")
			self._plotted_labels_list = new_plotlist
			self.plottedLabelsChanged.emit(self._plotted_labels_list)
			self.changed.emit(self)



	@property
	def x_axis(self):
		return self._x_axis

	@x_axis.setter
	def x_axis(self, new_axis_name):
		if new_axis_name != self.x_axis: #if changed
			self._x_axis = new_axis_name
			self.xAxisChanged.emit(self.x_axis)
			self.changed.emit(self)


	@property
	def plot_type(self):
		return self._plot_type

	@plot_type.setter
	def plot_type(self, new_plot_type):
		log.info(f"Trying to change plottype in model to: {new_plot_type}")
		if new_plot_type != self.plot_type: #if changed
			self._plot_type = new_plot_type
			self.plotTypeChanged.emit(self._plot_type)
			self.changed.emit(self)

	@property
	def selection_gap_fill_ms(self) -> int:
		return self._selection_gap_fill_ms_limval.val #type: ignore

	@selection_gap_fill_ms.setter
	def selection_gap_fill_ms(self, new_gap_fill_ms : int):
		if new_gap_fill_ms != self._selection_gap_fill_ms_limval.val: #if changed
			self._selection_gap_fill_ms_limval.val = new_gap_fill_ms
			self.selectionGapFillMsChanged.emit(self._selection_gap_fill_ms_limval.val)
			self.changed.emit(self)

	# ========================================= Other functions ============================================
	# def update_settings_using_df(self):


	@staticmethod
	def json_default(value):
		if isinstance(value, datetime.date):
			return dict(year=value.year, month=value.month, day=value.day)
		else:
			return value.__dict__

	def save_as_json(self, path):
		# json.dumps(self.__dict__)
		with open(path, "w", encoding="utf-8") as file:
			json.dump(self,file, default=self.json_default, indent=4)

		log.info(f"Saved plot options to {path}")
