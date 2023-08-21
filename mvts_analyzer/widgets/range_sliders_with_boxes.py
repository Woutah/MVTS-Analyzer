"""
Implements RangeSliderWithBoxes - A range slider with two boxes corresponding to the current value of the range
"""
import copy
import logging

from PySide6 import QtCore, QtWidgets

from mvts_analyzer.widgets import datastructures
from mvts_analyzer.utility.GuiUtility import safe_parse_new

from .range_slider import QRangeSlider

log = logging.getLogger(__name__)


def default_txt_converter(x):
	"""Default text converter - rounds to 2 decimals"""
	if x is None:
		return "None"

	return str(round(x, 2)) #Assumes


class RangeSlidersWithBoxes(QtWidgets.QWidget):
	"""
	A range-slider with boxes on either side corresponding to the current value of the slider
	"""
	rangeEdited = QtCore.Signal(object)
	rangeChanged = QtCore.Signal(object)

	def __init__(self,
			limited_range=datastructures.LimitedRange(),
			text_converter = default_txt_converter,
			text_parser = int,
			reset_on_parse_fail=True,
			**kwargs
		):
		super(RangeSlidersWithBoxes, self).__init__(**kwargs)

		self.main_layout = QtWidgets.QVBoxLayout()
		self.text_box_layout = QtWidgets.QHBoxLayout()
		self._slider = QRangeSlider()
		self._text_boxes = [QtWidgets.QLineEdit(), QtWidgets.QLineEdit()]
		self._reset_on_parse_fail = reset_on_parse_fail
		self._slider.setMax(100)
		self._slider.setMin(0)
		self._slider.setRange(0, 100)
		self._text_converter= text_converter
		self._text_parser = text_parser
		self._limited_range = limited_range

		self._slider.startValueChanged.connect(
			lambda: self._left_slider_changed(self._slider.getRange()[0])
		)
		self._slider.endValueChanged.connect(
			lambda: self._right_slider_changed(self._slider.getRange()[1])
		)

		self._text_boxes[0].editingFinished.connect(
			lambda *_: self._text_box_changed( self._text_boxes[0].text(), self._text_boxes[1].text())
		)
		self._text_boxes[1].editingFinished.connect(
			lambda *_: self._text_box_changed( self._text_boxes[0].text(), self._text_boxes[1].text())
		)




		#Add box + slider + box to layout
		self.text_box_layout.addWidget(self._text_boxes[0], 50)
		self.text_box_layout.addWidget(self._text_boxes[1], 50)
		self.main_layout.addLayout(self.text_box_layout)
		self.main_layout.addWidget(self._slider)

		#Set layout
		self.setLayout(self.main_layout)
		self._slider.setEnabled(True)
		self.show()
		self._update_all()

	def set_text_parser(self, text_parser):
		self._text_parser = text_parser


	def _update_slider(self):
		bounded_left, bounded_right = self._limited_range.find_bounded(
			self._limited_range.left_val, self._limited_range.right_val
		) #Find bounded
		self._slider.blockSignals(True)

		log.debug(f"Slider {bounded_left}<->{bounded_right}")
		if (bounded_left is None
				or bounded_right is None
				or self._limited_range.min_val is None
				or self._limited_range.max_val is None):
			self._slider.setEnd(100.0)
		else:
			self._slider.setEnd(
				round(
					100.0 * (bounded_right - self._limited_range.min_val)
					/ (self._limited_range.max_val - self._limited_range.min_val)
				)
			)
			self._slider.setStart(round(100.0 * ((bounded_left - self._limited_range.min_val)
					/ (self._limited_range.max_val - self._limited_range.min_val))))

		self._slider.blockSignals(False)


	def _update_boxes(self):
		# self.blockSignals(True)
		self._text_boxes[0].blockSignals(True)
		self._text_boxes[1].blockSignals(True)
		log.debug(self._limited_range.left_val)
		self._text_boxes[0].setText(self._text_converter(self._limited_range.left_val))
		self._text_boxes[1].setText(self._text_converter(self._limited_range.right_val))
		self._text_boxes[0].blockSignals(False)
		self._text_boxes[1].blockSignals(False)
		# self.blockSignals(False)


	def _update_all(self):
		self._update_slider()
		self._update_boxes()


	def _left_slider_changed(self, left: int):
		"""When left-slider is moved, update the boxes and emit the rangeEdited signal
		Args:
			left (int): the new value of the left slider
		"""
		log.debug(f"Left slider moved to {left / 100.0}")
		if (self._limited_range is not None 
      			and self._limited_range.max_val is not None 
				and self._limited_range.min_val is not None):
			#Case to same type as user-provided limrange (float/int/double etc.)
			self._limited_range.left_val =type(self._limited_range.min_val)(left / 100.0 *
				(self._limited_range.max_val - self._limited_range.min_val) + self._limited_range.min_val)

		log.debug(f"New slider values: {self._limited_range}")
		self._update_boxes()
		self.rangeEdited.emit( (self._limited_range.left_val, self._limited_range.right_val))

	def _right_slider_changed(self, right: int):
		"""
		When the right-slider is moved. Updates the boxes and emit the rangeEdited signal

		Args:
			right (int): The new value of the right slider
		"""
		log.debug(f"Right slider moved to {right / 100.0} & {right/100}")
		if (self._limited_range is not None 
      			and self._limited_range.max_val is not None 
				and self._limited_range.min_val is not None):
			self._limited_range.right_val = type(self._limited_range.max_val)(
				right / 100.0 * (self._limited_range.max_val - self._limited_range.min_val) + self._limited_range.min_val
			) #Cast to same type as user-provided limrange (float/int/double etc.)

		log.debug(f"New slider values: {self._limited_range}")
		# self._update_all()
		self._update_boxes()
		self.rangeEdited.emit( (self._limited_range.left_val, self._limited_range.right_val))


	def _text_box_changed(self, left, right):
		"""Call when the textboxes change value - updates the slider and emits the rangeEdited signal"""
		#LEFT
		left_result = safe_parse_new(left, cast_using=self._text_parser)
		if left_result[0] is True or not self._reset_on_parse_fail:
			self._limited_range.left_val = left_result[1]

		#right
		right_result = safe_parse_new(right, cast_using=self._text_parser)
		if right_result[0] is True or not self._reset_on_parse_fail:
			self._limited_range.right_val = right_result[1]
		self._update_slider()
		self.rangeEdited.emit( (self._limited_range.left_val, self._limited_range.right_val))



	def set_all(self, limited_range : datastructures.LimitedRange):
		"""
		Sets the current range of the slider and boxes
		"""
		log.debug(f"Setting rangeslider with boxes to: {limited_range}")
		self._limited_range = copy.copy(limited_range)
		self._update_boxes()
		self._update_slider()
		self.rangeChanged.emit((self._limited_range.left_val, self._limited_range.right_val))
		log.debug(f"Setting rangeslider resulted in: {self._limited_range}")

