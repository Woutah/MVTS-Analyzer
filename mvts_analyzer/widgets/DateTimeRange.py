from PySide6 import QtWidgets, QtCore
from mvts_analyzer.utility import GuiUtility
from .range_slider import QRangeSlider
from pydoc import locate

import logging
log = logging.getLogger(__name__)
import datetime
import copy
from mvts_analyzer.widgets import datastructures






class DateTimeRange(QtWidgets.QWidget):
	rangeEdited = QtCore.Signal(object) #[datetime, datetime]
	rangeChanged = QtCore.Signal(object)

	def __init__(self, enforce_limits = True, *args, **kwargs):
		super(DateTimeRange, self).__init__(*args, **kwargs)

		self._layout = QtWidgets.QVBoxLayout()
		self._text_box_layout = QtWidgets.QHBoxLayout()
		self._slider = QRangeSlider()
		# self.text_boxes = [QtWidgets.QLineEdit(), QtWidgets.QLineEdit()]

		self.text_boxes = [
			QtWidgets.QDateTimeEdit(calendarPopup=True),
			QtWidgets.QDateTimeEdit(calendarPopup=True)
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
		
		# self.rangeEdited.connect(self.rangeChanged) #Edit is also a change (not other way around) TODO: more and more emits when widget uses multiple widgets (edit will emit both change and emit, which will both emit a change in next widget etc.) 

		for curbox in self.text_boxes:
			self._text_box_layout.addWidget(curbox)
			curbox.dateTimeChanged.connect(self._boxes_changed)
		

		self._slider.endValueChanged.connect(self._slider_changed)
		self._slider.startValueChanged.connect(self._slider_changed)

		# self._limited_range.changed.connect(lambda x: print("KAASASDASDSADSA")) #self.rangeEdited((x.left_val, x.right_val))) #Connect limitrange change to rangeEdited
		

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
 
		# log.debug(f"Setting datetimeboxes to (limitedrange) {self._limited_range}")
		# log.debug(f"Types: {type(self._limited_range.min_val)} {type(self._limited_range.left_val)} {type(self._limited_range.right_val)} {type(self._limited_range.max_val)}")

		# self.blockSignals(True) #Temporarily block signals
		self.text_boxes[0].blockSignals(True) #Temporarily block callbacks, this has to be done, otherwise the "changed" signal is emitted (it seems) resulting in an infinite update loop
		self.text_boxes[1].blockSignals(True)

		# self.text_boxes[0].setMinimumDateTime()
		self.text_boxes[1].setDateTime(self._limited_range.right_val)
		self.text_boxes[0].setDateTime(self._limited_range.left_val)
		# log.debug(f"After setting, the datetime in the boxes were: {self.text_boxes[0].dateTime()} { self.text_boxes[1].dateTime()}") #Make sure min >= max		
		self.text_boxes[0].blockSignals(False)
		self.text_boxes[1].blockSignals(False)
		# self.blockSignals(False) #Resume signalling

	def _slider_changed(self):
		left,right = self._slider.getRange()
		left_val, right_val = None, None

		if self._limited_range is not None and self._limited_range.max_val is not None and self._limited_range.min_val is not None:
			
			left_val = (left / 100.0 * (self._limited_range.max_val - self._limited_range.min_val)) + self._limited_range.min_val
			right_val =  (right / 100.0 * (self._limited_range.max_val - self._limited_range.min_val)) + self._limited_range.min_val

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

	def _boxes_changed(self, x=None):
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
			self.text_boxes[0].setMinimumDateTime(self._limited_range.min_val if self._limited_range.min_val is not None else datetime.datetime(2000, 1, 1))
			self.text_boxes[1].setMaximumDateTime(self._limited_range.max_val if self._limited_range.max_val is not None else datetime.datetime(2200, 1, 1))

			# if self.text_boxes[0].dateTime() > 

		if self._limited_range.min_val is None or not self._enforce_limits or self.text_boxes[0].dateTime() > self._limited_range.min_val:
			# self.text_boxes[1].setMinimumDateTime(self.text_boxes[0].dateTime()) #Make sure min >= max
			self.text_boxes[1].setMinimumDateTime(self._limited_range.left_val) #Make sure min >= max

		if self._limited_range.max_val is None or not self._enforce_limits or self.text_boxes[1].dateTime() < self._limited_range.max_val:
			self.text_boxes[0].setMaximumDateTime(self._limited_range.right_val) #Make sure max <= min

		self.text_boxes[0].blockSignals(False)
		self.text_boxes[1].blockSignals(False)

		# log.debug(f"Set box limits to {self.text_boxes[0].minimumDateTime()} -> {self.text_boxes[0].maximumDateTime()} &  {self.text_boxes[1].minimumDateTime()} -> {self.text_boxes[1].maximumDateTime()}")


	def get_date_time(self):
		curdate = [self._limited_range.left_val, self._limited_range.right_val]
		return curdate
	
	def set_all(self, limited_range : datastructures.LimitedRange):
		log.debug(f"Setting all of datetimerange to {limited_range}")
		self.blockSignals(True)
		self._limited_range = copy.deepcopy(limited_range)
		# log.debug(f"Resulted in: {self._limited_range}")
		self._update_box_limits()
		self._update_slider()
		self._update_boxes()
		self.blockSignals(False)

		self.rangeChanged.emit((self._limited_range.left_val, self._limited_range.right_val))
