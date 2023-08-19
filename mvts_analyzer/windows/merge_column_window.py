import logging
import typing

from PySide6 import QtCore, QtWidgets

from mvts_analyzer.graphing.graph_data import GraphData
from mvts_analyzer.graphing.graph_settings_model import GraphSettingsModel
from mvts_analyzer.ui.merge_column_window_ui import Ui_MergeColumnWindow
from mvts_analyzer.widgets.dropdown_add_option import DropdownAddOption

log = logging.getLogger(__name__)

class MergeColumnWindow():

	def __init__(self, data_model : GraphData, parent=None) -> None:
		
		self.ui = Ui_MergeColumnWindow()
		self.data_model = data_model
		self.window = QtWidgets.QMainWindow(parent=parent)
		self.ui.setupUi(self.window)
		self.ui.returnMsgLabel.setText("")
 

		# self.ui.columnOptionsCombobox.

		# self.data_model.dfColumnsChanged.connect(lambda *_: self.reload_all_options())
		
		self.data_model.dfChanged.connect(lambda *_: self.reload_all_options())
		self.window.show()


		self.ui.newTypeComboBox.addItems(["Destination", "Source", "string", "Int64", "int64", "float", "category"])
		# self.ui.newTypeComboBox

		# self.newTypeTranslationDict = {
		# 		"Keep Source"				:	"",
		# 		"string"					:	"str",
		# 		"integer (without None)"	:	"",
		# 		"integer (with None)"		:	""
		# }

		self.ui.cancelBtn.pressed.connect(self.window.close)
		self.ui.renameBtn.pressed.connect(self.attempt_merge)

		self.reload_all_options()

		# self.ui.columnOptionsCombobox.currentTextChanged.connect(self.column_selection_changed)
		pass


	def attempt_merge(self):
		src = self.ui.sourceColumnCombobox.currentText()
		dest = self.ui.destinationColumnCombobox.currentText()
		preserve = self.ui.preserveSourceCheckBox.isChecked()
		mergemode = self.ui.mergeModeComboBox.currentText()
		astype = self.ui.newTypeComboBox.currentText()


		log.info(f"Trying to merge {src} -> {dest}		Mode={mergemode}, preserving={preserve}")

		success, msg = self.data_model.merge_columns(src, dest, mergemode, preserve, target_type=astype)

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


	# def reload_rename_options(self):
	# 	self.set_column_options(self.model.get_lbl_columns)

	# def reload_column_options(self):
	# 	self.set_column_options(self.model.get_lbl_columns)

	def get_rename_options(self):
		curtext = self.ui.columnOptionsCombobox.currentText() 
		options = []
		try: 
			options = self.model.df[curtext].unique()
		except KeyError as err:
			pass
	
		return options
		

		# if curtext in self.model.get_column_names:
		# 	self.model.

	def reload_column_options(self):
		self.ui.sourceColumnCombobox.blockSignals(True)
		self.ui.destinationColumnCombobox.blockSignals(True)
		# lbls = self.model.get_lbl_columns()
		cols = self.data_model.get_column_names()
		self.set_combobox_options(self.ui.sourceColumnCombobox, cols)
		self.set_combobox_options(self.ui.destinationColumnCombobox, cols + [None])		
		self.ui.sourceColumnCombobox.blockSignals(False)
		self.ui.destinationColumnCombobox.blockSignals(False)
		# self.set_combobox_options(self.ui.fromCombobox, self.)
		
	def reload_all_options(self):
		self.reload_column_options()



	#========= Setting combobox options ===============
	def set_combobox_options(self, combobox, new_options : typing.List):
		log.debug(f"Setting combobox to {new_options}")
		cur_choice = combobox.currentText()
		combobox.blockSignals(True)
		combobox.clear()
		combobox.addItems(new_options)
		if cur_choice in new_options: #If choice still available
			combobox.setCurrentText(cur_choice)
		combobox.blockSignals(False)



	# def set_column_options(self, column_options : typing.List):
	# 	log.debug(f"Setting RenameLabelDialog column options to {column_options}")
	# 	cur_choice = self.ui.fromCombobox.currentText()
	# 	self.ui.columnOptionsCombobox.clear() #Reset items
	# 	self.ui.columnOptionsCombobox.addItems(column_options)

	