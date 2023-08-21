"""
Implements RenameLabelWindow - A window in which we can quickly select annotations in a column and quickly rename
them to something else.
"""
import logging
import typing

from PySide6 import QtCore, QtWidgets

from mvts_analyzer.graphing.graph_data import GraphData
from mvts_analyzer.ui.rename_label_window_ui import Ui_RenameLabelWindow

log = logging.getLogger(__name__)

class RenameLabelWindow():
	"""Widget/window used for renaming labels within a column of a dataframe"""

	def __init__(self, graph_data_model : GraphData, parent=None) -> None:
		self.ui = Ui_RenameLabelWindow() #pylint: disable=invalid-name
		self.graph_data_model = graph_data_model
		self.window = QtWidgets.QMainWindow(parent=parent)
		self.ui.setupUi(self.window)
		self.ui.returnMsgLabel.setText("")
		self.graph_data_model.dfChanged.connect(lambda *_: self.reload_all_options())
		self.window.show()


		self.ui.cancelBtn.pressed.connect(self.window.close)
		self.ui.renameBtn.pressed.connect(self.attempt_rename)

		self.reload_all_options()
		self.ui.columnOptionsCombobox.currentTextChanged.connect(self.column_selection_changed)


		#To make sure animation is not garbage collected
		self.effect = None
		self.animation = None

	def column_selection_changed(self, new_selection : str):
		"""On column selection changed, reload the rename options
		
		Args:
			new_selection (str): The new column selection	
		"""
		log.debug(f"Column selection changed to {new_selection}")
		self.reload_rename_options()


	def attempt_rename(self):
		"""
		Get the current settings from UI and attempt to rename the labels
		"""
		col = self.ui.columnOptionsCombobox.currentText()
		from_lbl = self.ui.fromCombobox.currentText()
		to_lbl = self.ui.toComboBox.currentText()

		log.info(f"Trying to rename {col}, {from_lbl} --> {to_lbl}")

		success, msg = self.graph_data_model.rename_lbls(col, {from_lbl:to_lbl})
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


	def get_rename_options(self) -> typing.List[str]:
		"""
		Returns a list of the rename-options for the current column selection (annotations already present in col)
		"""
		curtext = self.ui.columnOptionsCombobox.currentText()
		options = []
		try:
			if self.graph_data_model.df is None:
				return []
			options = self.graph_data_model.df[curtext].unique()
			options = [str(i) for i in options]
		except KeyError:
			pass

		return options #type: ignore

	def reload_rename_options(self):
		"""
		Updates the UI-comboboxes to reflect the possible annotations for the currently selected column
		"""
		self.ui.fromCombobox.blockSignals(True)
		options = self.get_rename_options()
		if options is None or len(options) == 0:
			self.ui.fromCombobox.setEnabled(False)
			self.ui.toComboBox.setEnabled(False)
			self.set_combobox_options(self.ui.toComboBox, options)
		else:
			self.ui.fromCombobox.setEnabled(True)
			self.ui.toComboBox.setEnabled(True)
			self.set_combobox_options(self.ui.fromCombobox, options)
			self.set_combobox_options(self.ui.toComboBox, options)


		self.ui.fromCombobox.blockSignals(False)

	def reload_column_options(self):
		"""
		Updates the UI column-selection combobox to reflect the label-columns in the dataframe
		"""
		self.ui.columnOptionsCombobox.blockSignals(True)
		self.set_combobox_options(self.ui.columnOptionsCombobox, self.graph_data_model.get_lbl_columns())
		self.ui.columnOptionsCombobox.blockSignals(False)
		# self.set_combobox_options(self.ui.fromCombobox, self.)

	def reload_all_options(self):
		"""
		Updates all comboboxes in the UI according to the dataframe
		"""
		self.reload_column_options()
		self.reload_rename_options()



	#========= Setting combobox options ===============
	def set_combobox_options(self, combobox : QtWidgets.QComboBox, new_options : typing.List):
		"""
		Convenience function to add the passed options-list to the passed combobox after clearing it
		Args:
			combobox (QtWidgets.QComboBox): The combobox to set the options for
			new_options (typing.List): The new options to set
		"""
		log.debug(f"Setting combobox to {new_options}")
		cur_choice = combobox.currentText()
		combobox.blockSignals(True)
		combobox.clear()
		combobox.addItems(new_options)
		if cur_choice in new_options: #If choice still available
			combobox.setCurrentText(cur_choice)
		combobox.blockSignals(False)
