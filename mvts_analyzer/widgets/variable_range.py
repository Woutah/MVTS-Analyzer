"""
A variable range - can be either numeric or datetime and dynamically switches between the two based on
the set values
"""

import datetime
import logging
from numbers import Number

import numpy as np
from PySide6 import QtCore, QtGui, QtWidgets

from mvts_analyzer.widgets import datastructures
from mvts_analyzer.widgets.datetime_range import DateTimeRange
from mvts_analyzer.widgets.range_sliders_with_boxes import \
    RangeSlidersWithBoxes

log = logging.getLogger(__name__)

# class VariableRange(QtWidgets.QWidget):
class VariableRange(QtWidgets.QStackedWidget):
	"""A variable range - can be either numeric or datetime and dynamically switches between the two based on
	the set values
	"""

	rangeEdited = QtCore.Signal(object) #[datetime, datetime]
	rangeChanged = QtCore.Signal(object) #[datetime, datetime]

	def __init__(self,
			range_slider_with_boxes : RangeSlidersWithBoxes,
			date_time_range : DateTimeRange,
			none_msg="Please select x-axis",
			text_parser_dict = None,
			**kwargs):
		if text_parser_dict is None:
			text_parser_dict = {}
		log.debug("Initializing variablerange")
		super(VariableRange, self).__init__(**kwargs)

		my_font=QtGui.QFont()
		my_font.setItalic(True)
		self.none_msg_lbl = QtWidgets.QLabel()
		self.none_msg_lbl.setText(none_msg)
		self.none_msg_lbl.setFont(my_font)

		self.range_slider_with_boxes = range_slider_with_boxes
		self.date_time_range = date_time_range

		self.text_parser_dict = text_parser_dict

		self.addWidget(self.none_msg_lbl) #Index 0 = None
		self.addWidget(self.range_slider_with_boxes) #Index 1 = numeric
		self.addWidget(self.date_time_range) #Index 2 = Datetime

		self.range_slider_with_boxes.rangeEdited.connect(self.rangeEdited)
		self.date_time_range.rangeEdited.connect(self.rangeEdited)

		self.range_slider_with_boxes.rangeChanged.connect(self.rangeChanged)
		self.date_time_range.rangeChanged.connect(self.rangeChanged)

		self.setCurrentIndex(0)
		self.show()

	def set_all(self, limited_range : datastructures.LimitedRange):
		"""Copy the data from another limited range to this one"""
		if limited_range is None:
			log.warning("Cannot display limited range - None is passed")
			self.setCurrentIndex(0)
			return
		new_type = limited_range.get_type()
		log.debug(f"Newtype of limited range ({limited_range}) is: {new_type} ")
		if new_type is datetime.datetime:
			self.setCurrentIndex(2)
			# log.debug("Now entering set all!!")
			self.date_time_range.set_all(limited_range) #Set new range
		elif isinstance(new_type, Number) or np.issubdtype(new_type, np.number):
			self.setCurrentIndex(1)
			self.range_slider_with_boxes.set_all(limited_range) #Set new range
			if new_type in self.text_parser_dict.keys():
				self.range_slider_with_boxes.set_text_parser(self.text_parser_dict[new_type])
			else:
				self.range_slider_with_boxes.set_text_parser(new_type)
		else:
			self.setCurrentIndex(0)

		log.debug("Done setting all")
