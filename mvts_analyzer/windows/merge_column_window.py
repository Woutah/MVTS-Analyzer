"""
Implements the MergeColumnWindow - The logic for the merge-column-window that allows the user to quickly
	merge and delete columns from the dataframe
"""
import logging
import typing

from PySide6 import QtCore, QtWidgets

from mvts_analyzer.graphing.graph_data import GraphData
from mvts_analyzer.ui.merge_column_window_ui import Ui_MergeColumnWindow

log = logging.getLogger(__name__)

class MergeColumnWindow():
	"""
	The merge-column-window logic, manage user input and call the graph_data_model to do the actual work
	when the user presses the rename button
	"""

	def __init__(self, data_model : GraphData, parent=None) -> None:

		self.ui = Ui_MergeColumnWindow() #pylint: disable=invalid-name
		self.data_model = data_model
		self.window = QtWidgets.QMainWindow(parent=parent)
		self.ui.setupUi(self.window)
		self.ui.returnMsgLabel.setText("")


		self.data_model.dfChanged.connect(lambda *_: self.reload_all_options())
		self.window.show()


		self.ui.newTypeComboBox.addItems(["Destination", "Source", "string", "Int64", "int64", "float", "category"])
		self.ui.cancelBtn.pressed.connect(self.window.close)
		self.ui.renameBtn.pressed.connect(self.attempt_merge)
		self.reload_all_options()


		self.effect = None
		self.animation = None


	def attempt_merge(self):
		"""
		Get the data from the UI and try to merge the columns (or delete if destination is None)
		"""
		src = self.ui.sourceColumnCombobox.currentText()
		dest = self.ui.destinationColumnCombobox.currentText()
		preserve = self.ui.preserveSourceCheckBox.isChecked()
		mergemode = self.ui.mergeModeComboBox.currentText()
		astype = self.ui.newTypeComboBox.currentText()


		log.info(f"Trying to merge {src} -> {dest}		Mode={mergemode}, preserving={preserve}")

		success, msg = self.data_model.merge_columns(src, dest, mergemode, preserve, astype=astype) #type: ignore

		self.effect = QtWidgets.QGraphicsOpacityEffect()
		self.animation = QtCore.QPropertyAnimation(self.effect, b"opacity")
		self.animation.setDuration(10000)
		self.animation.setStartValue(1)
		self.animation.setEndValue(0)

		self.ui.returnMsgLabel.setText(msg)
		if success:
			self.ui.returnMsgLabel.setGraphicsEffect(self.effect)
			self.ui.returnMsgLabel.setStyleSheet("color: green")
			self.animation.start()
		else:
			self.ui.returnMsgLabel.setText(msg)
			self.ui.returnMsgLabel.setStyleSheet("color: red")


	def reload_column_options(self):
		"""
		Reload the combobox options for the columns from the dataframe
		"""
		self.ui.sourceColumnCombobox.blockSignals(True)
		self.ui.destinationColumnCombobox.blockSignals(True)
		cols = self.data_model.get_column_names()
		self.set_combobox_options(self.ui.sourceColumnCombobox, cols)
		self.set_combobox_options(self.ui.destinationColumnCombobox, cols + [None])
		self.ui.sourceColumnCombobox.blockSignals(False)
		self.ui.destinationColumnCombobox.blockSignals(False)
		# self.set_combobox_options(self.ui.fromCombobox, self.)

	def reload_all_options(self):
		"""Reloads all combobox options"""
		self.reload_column_options()



	#========= Setting combobox options ===============
	def set_combobox_options(self, combobox : QtWidgets.QComboBox, new_options : typing.List):
		"""
		Utility function to set the options of a combobox after clearing it
		"""
		log.debug(f"Setting combobox to {new_options}")
		cur_choice = combobox.currentText()
		combobox.blockSignals(True)
		combobox.clear()
		combobox.addItems(new_options)
		if cur_choice in new_options: #If choice still available
			combobox.setCurrentText(cur_choice)
		combobox.blockSignals(False)
