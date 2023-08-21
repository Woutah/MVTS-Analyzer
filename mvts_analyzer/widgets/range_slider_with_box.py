"""
Implements RangeSliderWithBox - A range slider with a box corresponding to the current value of the slider
"""
import copy  # Copy limitedrange
import logging
import typing

from PySide6 import QtCore, QtWidgets

from mvts_analyzer.utility import GuiUtility
from mvts_analyzer.widgets.datastructures import LimitedValue

log = logging.getLogger(__name__)




class RangeSliderWithBox(QtWidgets.QWidget):
	"""
	Range slider with a box corresponding to the current value of the slider
	"""
	valueEdited = QtCore.Signal(object)

	def __init__(
			self,
	      	limited_value = LimitedValue(),
			text_converter : typing.Callable = str,
			text_parser : typing.Callable = int,
			reset_on_parse_fail = False,
			**kwargs
		):
		super(RangeSliderWithBox, self).__init__(**kwargs)

		self._layout = QtWidgets.QHBoxLayout(self)
		self._slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
		self._text_box = QtWidgets.QLineEdit()
		self._text_converter = text_converter #Converts value-->text
		self._text_parser = text_parser #Convert text-->value
		self._reset_on_parse_fail = reset_on_parse_fail

		#Connect change to update function
		self._slider.valueChanged.connect(self._slider_changed)
		# self._text_box.editingFinished.connect(lambda: self._text_box_changed)
		self._text_box.editingFinished.connect(lambda: self._text_box_changed(self._text_box.text()))

		# self._text_box.editingFinished.connect(lambda: self.valueBoxEdited(self._text_box.text()))

		#Add box + slider to layout
		self._layout.addWidget(self._slider, 90)
		self._layout.addWidget(self._text_box, 10)

		self._limited_value = limited_value

		self._slider.setMinimum(0)
		self._slider.setMaximum(100)
		self._slider.setValue(50)
		self.show()


	def _slider_changed(self, new_val : int):
		self._slider.blockSignals(True)
		if (self._limited_value is not None
				and self._limited_value.max_val is not None
				and self._limited_value.min_val is not None):
			#NOTE: the following assumes the constructor is able to parse the value #type:ignore
			self._limited_value.val = type(self._limited_value.max_val)((new_val / 100.0 *
				(self._limited_value.max_val - self._limited_value.min_val) + self._limited_value.min_val))  #type:ignore
			log.debug(f"Slider changed to : {new_val}/100 -> {self._limited_value.val}")
		# self._update_all()
		self._update_textbox()
		self._slider.blockSignals(False)
		self.valueEdited.emit(self._limited_value.val)


	def _text_box_changed(self, new_text):
		print(new_text)
		result = GuiUtility.safe_parse_new(new_text, cast_using=self._text_parser)

		log.info(f"text_box changed to: {result}")
		if result[0] is True or not self._reset_on_parse_fail:
			self._limited_value.val = result[1]
		# self._update_textbox()
		# self._update_all()
		self._update_slider()
		self.valueEdited.emit(self._limited_value.val)



	def _update_all(self):
		self._update_textbox()
		self._update_slider()

	def _update_textbox(self):
		self.blockSignals(True)
		self._text_box.blockSignals(True) #Make sure text box update does not trigger signal cascade
		if self._limited_value.val is None:
			self._text_box.setText("-")
		else:
			self._text_box.setText(self._text_converter(self._limited_value.val))
		self._text_box.blockSignals(False)
		self.blockSignals(False)

	def _update_slider(self):
		self.blockSignals(True)
		self._slider.blockSignals(True)
		bounded_val = self._limited_value.find_bounded(self._limited_value.val) #TODO: not neccessary if min/max checked
		if (bounded_val is None
				or self._limited_value is None
				or self._limited_value.min_val is None
				or self._limited_value.max_val is None):
			self._slider.setValue(50)
		else:
			self._slider.setValue(int(
					(bounded_val - self._limited_value.min_val)/(self._limited_value.max_val - self._limited_value.min_val) * 100.0
				) #type:ignore #We already checked for None
			)
		self.blockSignals(False)
		self._slider.blockSignals(False)

	def set_all(self, limited_value : LimitedValue):
		self._limited_value = copy.copy(limited_value)
		self._update_all()
