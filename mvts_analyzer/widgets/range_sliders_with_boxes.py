from PySide6 import QtWidgets, QtCore
from mvts_analyzer.utility import GuiUtility
from .range_slider import QRangeSlider
from pydoc import locate

import logging
log = logging.getLogger(__name__)


from mvts_analyzer.widgets import datastructures
import copy



def default_txt_converter(x):
	if x is None:
		return "None"

	return str(round(x, 2)) #Assumes 


class RangeSlidersWithBoxes(QtWidgets.QWidget):

	# valueSliderChangedLeft = QtCore.Signal()
	# valueBoxChangedLeft = QtCore.Signal()
	# valueSliderChangedRight = QtCore.Signal()
	# valueBoxChangedRight = QtCore.Signal()

	# valueBoxChanged = QtCore.Signal([str, str])
	# valueSliderChanged = QtCore.Signal(object)

	rangeEdited = QtCore.Signal(object)
	rangeChanged = QtCore.Signal(object)

	def __init__(self, limited_range=datastructures.LimitedRange(), text_converter = default_txt_converter, text_parser = int, reset_on_parse_fail=True, *args, **kwargs):
		super(RangeSlidersWithBoxes, self).__init__(*args, **kwargs)

		self.layout = QtWidgets.QVBoxLayout()
		self.text_box_layout = QtWidgets.QHBoxLayout()
		self._slider = QRangeSlider()
		self._text_boxes = [QtWidgets.QLineEdit(), QtWidgets.QLineEdit()]
		self._reset_on_parse_fail = reset_on_parse_fail
		self._slider.setMax(100)
		self._slider.setMin(0)
		self._slider.setRange(0, 100)
		#Connect change to update function
		# self._slider.startValueChanged.connect(self.valueSliderChangedLeft)
		# self._slider.endValueChanged.connect(self.valueSliderChangedRight)
		self._text_converter= text_converter
		self._text_parser = text_parser
		self._limited_range = limited_range

		self._slider.startValueChanged.connect(
			# lambda: self._slider_changed(*self._slider.getRange())
			lambda: self._left_slider_changed(self._slider.getRange()[0])
			# lambda: self.valueSliderChanged.emit(self._slider.getRange())
		)
		self._slider.endValueChanged.connect(
			# lambda: self._slider_changed(*self._slider.getRange())
			
			lambda: self._right_slider_changed(self._slider.getRange()[1])
			# lambda: self.valueSliderChanged.emit(self._slider.getRange())
		)
		

		# self._text_boxes[0].editingFinished.connect(self.valueBoxChangedLeft)
		# self._text_boxes[1].editingFinished.connect(self.valueBoxChangedRight)
		self._text_boxes[0].editingFinished.connect(
			# lambda: self.valueBoxChanged.emit([self._text_boxes[0], self._text_boxes[1]])
			lambda *_: self._text_box_changed( self._text_boxes[0].text(), self._text_boxes[1].text())
		)
		self._text_boxes[1].editingFinished.connect(
			lambda *_: self._text_box_changed( self._text_boxes[0].text(), self._text_boxes[1].text())
		)

		


		#Add box + slider + box to layout
		self.text_box_layout.addWidget(self._text_boxes[0], 50)
		self.text_box_layout.addWidget(self._text_boxes[1], 50)
		self.layout.addLayout(self.text_box_layout)
		self.layout.addWidget(self._slider)
		

		# log.info(f"ConfRangeSliderWithBoxes initialized {self._text_boxes}")
		#Set layout
		self.setLayout(self.layout)
		self._slider.setEnabled(True)
		self.show()
		self._update_all()
		# self.update_ui()
	
	def set_text_parser(self, text_parser):
		self._text_parser = text_parser


	def _update_slider(self):
		bounded_left, bounded_right = self._limited_range.find_bounded(self._limited_range.left_val, self._limited_range.right_val) #Find bounded
		self._slider.blockSignals(True)

		log.debug(f"Slider {bounded_left}<->{bounded_right}")
		if bounded_left is None or bounded_right is None or self._limited_range.min_val is None or self._limited_range.max_val is None:
			self._slider.setEnd(100.0)
		else:
			self._slider.setEnd(round(100.0 * (bounded_right - self._limited_range.min_val) / (self._limited_range.max_val - self._limited_range.min_val)))
			self._slider.setStart(round(100.0 * ((bounded_left - self._limited_range.min_val) / (self._limited_range.max_val - self._limited_range.min_val))))

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
		log.debug(f"Left slider moved to {left / 100.0}")
		if self._limited_range is not None and self._limited_range.max_val is not None and self._limited_range.min_val is not None:
			self._limited_range.left_val =type(self._limited_range.min_val)(left / 100.0 * (self._limited_range.max_val - self._limited_range.min_val) + self._limited_range.min_val) #Case to same type as user-provided limrange (float/int/double etc.)

		log.debug(f"New slider values: {self._limited_range}")
		self._update_boxes()
		self.rangeEdited.emit( (self._limited_range.left_val, self._limited_range.right_val))

	def _right_slider_changed(self, right: int):
		log.debug(f"Right slider moved to {right / 100.0} & {right/100}")
		if self._limited_range is not None and self._limited_range.max_val is not None and self._limited_range.min_val is not None:
			self._limited_range.right_val = type(self._limited_range.max_val)(right / 100.0 * (self._limited_range.max_val - self._limited_range.min_val) + self._limited_range.min_val) #Cast to same type as user-provided limrange (float/int/double etc.)

		log.debug(f"New slider values: {self._limited_range}")
		# self._update_all()
		self._update_boxes()
		self.rangeEdited.emit( (self._limited_range.left_val, self._limited_range.right_val))

	# def _slider_changed(self, left : int, right : int):
	# 	# print(f"updating slider to {left} {right}")
	# 	log.debug(f"Sliders changed to {left / 100.0} & {right/100}")
	# 	if self._limited_range is not None and self._limited_range.max_val is not None and self._limited_range.min_val is not None:
	# 		# self._limited_range.left_val = type(self._limited_range.min_val)(left / 100.0 * (self._limited_range.max_val - self._limited_range.min_val) + self._limited_range.min_val) #Cast to same type as user-provided limrange (float/int/double etc.)
	# 		# self._limited_range.right_val = type(self._limited_range.max_val)(right / 100.0 * (self._limited_range.max_val - self._limited_range.min_val) + self._limited_range.min_val)
	# 		self._limited_range.left_val =(left / 100.0 * (self._limited_range.max_val - self._limited_range.min_val) + self._limited_range.min_val) #Case to same type as user-provided limrange (float/int/double etc.)
	# 		self._limited_range.right_val = (right / 100.0 * (self._limited_range.max_val - self._limited_range.min_val) + self._limited_range.min_val)

	# 	log.debug(f"New slider values1: {self._limited_range}")

	# 	self._update_all()
	# 	self.rangeEdited.emit( (self._limited_range.left_val, self._limited_range.right_val))
	# 	log.debug(f"New slider values2: {self._limited_range}")


	def _text_box_changed(self, left, right):
		# print(f"Parsing {left} - {right}")
		#LEFT 
		left_result = utility.safe_parse_new(left, cast_using=self._text_parser)
		if left_result[0] is True or not self._reset_on_parse_fail:
			self._limited_range.left_val = left_result[1]

		#right
		right_result = utility.safe_parse_new(right, cast_using=self._text_parser)
		if right_result[0] is True or not self._reset_on_parse_fail:
			self._limited_range.right_val = right_result[1]
		# self._update_textbox()
		# print(f"Limrange: {self._limited_range}")
		self._update_slider()
		self.rangeEdited.emit( (self._limited_range.left_val, self._limited_range.right_val))



	# def set_left(self, slider_val):
	# 	self._slider.start = slider_val
	# 	self._text_boxes[0].setText(str(slider_val))

	# def set_right(self, slider_val): 
	# 	self._slider.end = slider_val
	# 	self._text_boxes[1].setText(str(slider_val))
	



	def set_all(self, limited_range : datastructures.LimitedRange):
		log.debug(f"Setting rangeslider with boxes to: {limited_range}")

		# self._slider.setMax(limited_range.max_val)
		# self._slider.setMin(limited_range.min_val)

		self._limited_range = copy.copy(limited_range)

		# self._limited_range = limited_range #TODO IMPORTANT TODO : this results in no lagging when dragging the head around --> quite unsafe to edit this value directly so dont do this...
		
		self._update_boxes()
		# self.tempie()
		self._update_slider()
		self.rangeChanged.emit((self._limited_range.left_val, self._limited_range.right_val))
		log.debug(f"Setting rangeslider resulted in: {self._limited_range}")
		
	