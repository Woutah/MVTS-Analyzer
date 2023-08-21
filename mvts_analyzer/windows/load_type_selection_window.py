"""
Implements:
LoadTypeSelectionDialog - A dialog to select the load type (overwrite or append) and the time range to load

And helper classes:
LoadSpecifications - A small datastructure to manage the loading type
MainLoadType - Enum for the main load type (e.g. Append or OverWerwrite)
DuplicatePolicy - Enum for the duplicate policy (e.g. Keep original or overwrite)

"""
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from PySide6 import QtCore, QtWidgets

from mvts_analyzer.widgets.datastructures import LimitedRange
from mvts_analyzer.widgets.datetime_range import DateTimeRange

log = logging.getLogger(__name__)

ABSOLUTE_MIN_DATE = datetime(1900, 1, 1)
ABSOLUTE_MAX_DATE = datetime(3000, 1, 1)

class MainLoadType(Enum):
	"""What method to use when loading the data"""
	APPEND = 0
	OVERWRITE = 1

class DuplicatePolicy(Enum):
	"""What to do with duplicate entries in the data when loading"""
	KEEP_ORIGINAL = 0
	OVERWRITE = 1

@dataclass
class LoadSpecifications():
	"""
	Small datastructure to manage the loading type
	"""
	main_load_type : MainLoadType = MainLoadType.APPEND
	cancelled : bool = False
	from_time : datetime = datetime(2000, 1, 1)
	to_time :  datetime = datetime(2200, 1, 1)
	duplicate_policy : DuplicatePolicy = DuplicatePolicy.KEEP_ORIGINAL


class LoadTypeSelectionDialog(QtWidgets.QDialog):
	"""
	A dialog to select the load type (overwrite or append) and the time range to load
	"""
	def __init__(self,
			min_db_entrydate : datetime = datetime(1900, 1, 1),
			max_dbentry_date : datetime = datetime(3000, 1, 1)
		):
		super().__init__()

		self.min_date = min_db_entrydate
		self.max_date = max_dbentry_date

		self.setWindowTitle("Load settings")
		self.main_layout = QtWidgets.QVBoxLayout()

		self.return_specification = LoadSpecifications()


		#========== Main Load type =============
		self.main_load_type_layout = QtWidgets.QHBoxLayout()

		self.main_load_type_widget = QtWidgets.QComboBox()
		self.main_load_type_widget.addItems(["Append", "Overwrite"])
		self.main_load_type_widget.currentTextChanged.connect(self._main_load_type_changed)
		self.overwrite_warning = QtWidgets.QLabel("'overwrite' discards the currently loaded database")
		self.main_load_type_widget.setToolTip("Should the whole database be overwritten? or should the new data be "
			"appended to the currently loaded data")
		self.overwrite_warning.setStyleSheet("color: red;")
		self.overwrite_warning.setVisible(False) #Append is default options --> no warning

		self.main_load_type_layout.addWidget(QtWidgets.QLabel("Load type:"), 50)
		self.main_load_type_layout.addWidget(self.main_load_type_widget, 50)
		self.main_load_type_layout.addWidget(self.overwrite_warning, 10)


		self.main_layout.addLayout(self.main_load_type_layout)


		#======== Date Selection ============
		self.datelayout = QtWidgets.QHBoxLayout()
		self.load_rangetype_widget = QtWidgets.QComboBox()
		self.load_rangetype_widget.addItems(
			["All available", "Time range", "Time range from latest database entry", "Last 10 minutes", "Last hour"])
		self.load_rangetype_widget.currentTextChanged.connect(self._rangetype_changed)
		self.datelayout.addWidget(QtWidgets.QLabel("Load from/until settings"), 50)
		self.datelayout.addWidget(self.load_rangetype_widget, 50)
		self.load_rangetype_widget.setToolTip("Which daterange will be requested all data in this time range will be "
			"added to the database")

		self.main_layout.addLayout(self.datelayout)


		self.datetimerange_widget = DateTimeRange()
		self.datetimerange_widget.set_all(LimitedRange(min_val=min_db_entrydate, max_val=max_dbentry_date))
		self.datetimerange_widget.rangeEdited.connect(lambda *_: self._timerange_changed())
		self.datetimerange_widget.setVisible(False) #Hide by default
		self.main_layout.addWidget(self.datetimerange_widget)

		#========== Main Load type =============
		self.duplicate_policy_layout = QtWidgets.QHBoxLayout()
		self.duplicate_policy_widget = QtWidgets.QComboBox()
		self.duplicate_policy_widget.addItems(["Keep Original", "Overwrite"])
		self.duplicate_policy_widget.currentTextChanged.connect(self._duplicate_policy_changed)
		self.duplicate_policy_widget.setToolTip(
			"What to do with duplicate entries (e.g. datapoint that already exist in the database), either take "
			"existing or overwrite. Will only apply this policy to columns where both entries are not None "
			"(in this case the first not-None value is taken)")
		self.duplicate_policy_layout.addWidget(QtWidgets.QLabel("Duplicate entry policy:"), 50)
		self.duplicate_policy_layout.addWidget(self.duplicate_policy_widget, 50)

		self.main_layout.addLayout(self.duplicate_policy_layout)



		self.main_layout.addLayout(self.main_load_type_layout)
		self.setLayout(self.main_layout)


		buttons = QtWidgets.QDialogButtonBox(
			QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel,
			QtCore.Qt.Orientation.Horizontal, self)


		self.main_layout.addWidget(buttons)

		buttons.accepted.connect(self._confirm_pressed)
		buttons.rejected.connect(self._cancel_pressed)

	def _duplicate_policy_changed(self, new_type):
		if new_type == "Keep Original":
			self.return_specification.duplicate_policy = DuplicatePolicy.KEEP_ORIGINAL
		if new_type == "Overwrite":
			self.return_specification.duplicate_policy = DuplicatePolicy.OVERWRITE


	def _timerange_changed(self):
		curdt = self.datetimerange_widget.get_date_time()
		self.return_specification.from_time = curdt[0] #type: ignore
		self.return_specification.to_time = curdt[1] #type: ignore

	def _rangetype_changed(self, new_type : str):
		if new_type == "All available":
			self.return_specification.from_time = ABSOLUTE_MIN_DATE
			self.return_specification.to_time = ABSOLUTE_MAX_DATE
			self.datetimerange_widget.setVisible(False)
		elif new_type == "Time range":
			self.datetimerange_widget.setVisible(True)
			self.datetimerange_widget.set_all(LimitedRange(min_val=self.min_date, max_val=self.max_date))
			self._timerange_changed()
		elif new_type == "Time range from latest database entry":
			self.datetimerange_widget.setVisible(True)
			self.datetimerange_widget.set_all(LimitedRange(min_val=self.max_date, max_val=datetime(2100, 1, 1)))
			self._timerange_changed()
		elif new_type == "Last 10 minutes":
			self.datetimerange_widget.setVisible(False)
			self.return_specification.from_time = datetime.now()- timedelta(minutes=10)
			self.return_specification.to_time = datetime(2200, 1, 1)
		elif new_type == "Last hour":
			self.datetimerange_widget.setVisible(False)
			self.return_specification.from_time = datetime.now()- timedelta(hours=1)
			self.return_specification.to_time = datetime(2200, 1, 1)





	def _main_load_type_changed(self, new_type : str):
		if new_type == "Append":
			self.return_specification.main_load_type = MainLoadType.APPEND
			self.overwrite_warning.setVisible(False)
		if new_type == "Overwrite":
			self.return_specification.main_load_type = MainLoadType.OVERWRITE
			self.overwrite_warning.setVisible(True)


	def _confirm_pressed(self):
		log.debug("Confirm pressed")
		self.return_specification.cancelled = False
		self.accept()
		self.close()



	def _cancel_pressed(self):
		log.debug("Cancel pressed")
		self.return_specification.cancelled = True
		self.reject()
		self.close()

	def get_selection(self):
		"""Return the load-specifications datastructure"""
		return self.return_specification
