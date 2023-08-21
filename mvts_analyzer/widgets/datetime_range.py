"""
Implements DateTimeRange - a datetime range slider with 2 datetime-boxes
"""
import copy
import datetime
import logging

from PySide6 import QtCore, QtWidgets

from mvts_analyzer.widgets import datastructures

from .range_slider import QRangeSlider

log = logging.getLogger(__name__)

class DateTimeRange(QtWidgets.QWidget):
	"""
	Datetime range with 2 datetime-boxes and a slider
	"""
	rangeEdited = QtCore.Signal(object) #[datetime, datetime]
	rangeChanged = QtCore.Signal(object)

	def __init__(self, enforce_limits = True, **kwargs):
		super(DateTimeRange, self).__init__( **kwargs)

		self._layout = QtWidgets.QVBoxLayout()
		self._text_box_layout = QtWidgets.QHBoxLayout()
		self._slider = QRangeSlider()
		# self.text_boxes = [QtWidgets.QLineEdit(), QtWidgets.QLineEdit()]

		self.text_boxes = [
			QtWidgets.QDateTimeEdit(calendarPopup=True), #type:ignore #Enables calendar popup - not in pyside doc?
			QtWidgets.QDateTimeEdit(calendarPopup=True)#type:ignore
		]

		#Only trigger callback after submitting value
		self.text_boxes[0].setKeyboardTracking(False)
		self.text_boxes[1].setKeyboardTracking(False)

		self._slider.setMax(100)
		self._slider.setMin(0)
		self._slider.setRange(0, 100)
		self._enforce_limits = enforce_limits
		self._limited_range = datastructures.LimitedRange()

		#Add box + slider + box to layout
		self._layout.addLayout(self._text_box_layout)
		self._layout.addWidget(self._slider)

		for curbox in self.text_boxes:
			self._text_box_layout.addWidget(curbox)
			curbox.dateTimeChanged.connect(self._boxes_changed)


		self._slider.endValueChanged.connect(self._slider_changed)
		self._slider.startValueChanged.connect(self._slider_changed)

		self.setLayout(self._layout)
		self._slider.setEnabled(True)
		self.show()

	def _update_all(self):
		self._update_boxes()
		self._update_slider()
		self._update_box_limits()

	def _update_boxes(self):
		if self._limited_range.min_val is None or self._limited_range.max_val is None:
			log.debug("Min or max is none")
			return


		#Temporarily block callbacks, this has to be done, otherwise the "changed" signal is emitted (it seems)
		# resulting in an infinite update loop
		self.text_boxes[0].blockSignals(True)
		self.text_boxes[1].blockSignals(True)

		# self.text_boxes[0].setMinimumDateTime()
		self.text_boxes[1].setDateTime(self._limited_range.right_val) #type: ignore
		self.text_boxes[0].setDateTime(self._limited_range.left_val) #type: ignore
		self.text_boxes[0].blockSignals(False)
		self.text_boxes[1].blockSignals(False)

	def _slider_changed(self):
		left,right = self._slider.getRange()
		left_val, right_val = None, None

		if (self._limited_range is not None
				and self._limited_range.max_val is not None
				and self._limited_range.min_val is not None):
			if left is None or right is None:
				return
			left_val = ((left / 100.0 * (self._limited_range.max_val - self._limited_range.min_val))
				+ self._limited_range.min_val)
			right_val =  ((right / 100.0 * (self._limited_range.max_val - self._limited_range.min_val))
				+ self._limited_range.min_val)

			if left_val > right_val:
				left_val = right_val

			if self._enforce_limits: #If bounded by left/right max (and enforced)
				left_val, right_val = self._limited_range.find_bounded(left_val, right_val)

			self._limited_range.left_val = left_val
			self._limited_range.right_val = right_val


		log.debug(f"Slider changed to: {left} = {left_val}, {right} = {right_val}")
		self._update_box_limits()
		self._update_boxes()
		self.rangeEdited.emit((self._limited_range.left_val, self._limited_range.right_val))

	def _update_slider(self):
		factors = self._limited_range.factors
		self.blockSignals(True)
		self._slider.blockSignals(True)
		if factors is None or factors[0] is None or factors[1] is None:
			self._slider.setRange(0, 100)
		else:
			self._slider.setRange(int(factors[0] * 100), int(factors[1] * 100))
		self._slider.blockSignals(False)
		self.blockSignals(False)

	def _boxes_changed(self):
		left, right = self.text_boxes[0].dateTime().toPython(), self.text_boxes[1].dateTime().toPython()


		log.debug(f"Boxes changed to: {left} {right}")
		if self._enforce_limits:
			left, right = self._limited_range.find_bounded(left, right)
		log.debug(f"Bounded results in : {left} - {right}")

		if left is not None:
			self._limited_range.left_val = left
		if right is not None:
			self._limited_range.right_val = right

		# self._update_all()
		self._update_box_limits()
		self._update_slider()
		self.rangeEdited.emit((self._limited_range.left_val, self._limited_range.right_val))

		log.debug(f"Limited range became: {self._limited_range}")

	def _update_box_limits(self):
		#TODO: temporarily turn off limits?
		# log.debug(f"Updating box limits using self.limited_range: {self._limited_range}")


		self.text_boxes[0].blockSignals(True)
		self.text_boxes[1].blockSignals(True)

		if self._enforce_limits:
			self.text_boxes[0].setMinimumDateTime(
				self._limited_range.min_val if self._limited_range.min_val is not None
					else datetime.datetime(2000, 1, 1) #type:ignore #Works with python datetime
			)
			self.text_boxes[1].setMaximumDateTime(
				self._limited_range.max_val if self._limited_range.max_val is not None
					else datetime.datetime(2200, 1, 1) #type:ignore #Works with python datetime
			)

		if (self._limited_range.min_val is None
				or not self._enforce_limits
				or self.text_boxes[0].dateTime() > self._limited_range.min_val):
			self.text_boxes[1].setMinimumDateTime(self._limited_range.left_val) #Make sure min >= max #type:ignore

		if (self._limited_range.max_val is None
      			or not self._enforce_limits
				or self.text_boxes[1].dateTime() < self._limited_range.max_val):
			self.text_boxes[0].setMaximumDateTime(self._limited_range.right_val) #Make sure max <= min #type:ignore

		self.text_boxes[0].blockSignals(False)
		self.text_boxes[1].blockSignals(False)

	def get_date_time(self) -> tuple[datetime.datetime | None, datetime.datetime | None]:
		"""Returns the current datetime range-tuple"""
		curdate = (self._limited_range.left_val, self._limited_range.right_val)
		return curdate

	def set_all(self, limited_range : datastructures.LimitedRange):
		"""Copy the data from another limited range to this one
		Args:
			limited_range (datastructures.LimitedRange): The limited range to copy
		"""
		log.debug(f"Setting all of datetimerange to {limited_range}")
		self.blockSignals(True)
		self._limited_range = copy.deepcopy(limited_range)
		self._update_box_limits()
		self._update_slider()
		self._update_boxes()
		self.blockSignals(False)
		self.rangeChanged.emit((self._limited_range.left_val, self._limited_range.right_val))
