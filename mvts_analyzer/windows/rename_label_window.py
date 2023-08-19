import typing
from mvts_analyzer.graphing.graph_data import GraphData
# from mvts_analyzer.windows.RenameLabelWindow.RenameLabelWindow_ui import Ui_RenameLabelWindow 
from mvts_analyzer.ui.rename_label_window_ui import Ui_RenameLabelWindow
from mvts_analyzer.graphing.graph_settings_model import GraphSettingsModel
from PySide6 import QtWidgets, QtCore
import typing
from mvts_analyzer.widgets.dropdown_add_option import DropdownAddOption

import logging
log = logging.getLogger(__name__)

class RenameLabelWindow():

	def __init__(self, graph_data_model : GraphData, parent=None) -> None:
		
		self.ui = Ui_RenameLabelWindow()
		self.graph_data_model = graph_data_model
		self.window = QtWidgets.QMainWindow(parent=parent)
		self.ui.setupUi(self.window)
		self.toCombobox = DropdownAddOption()
		self.toCombobox.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
                                                 QtWidgets.QSizePolicy.Fixed))
		self.ui.renameToVLayout.addWidget(self.toCombobox, stretch=0)
		self.ui.returnMsgLabel.setText("")
 

		self.ui.renameToVLayout.addWidget(self.toCombobox)
		# self.ui.columnOptionsCombobox.

		# self.graph_data_model.plot_settings.dfColumnsChanged.connect(lambda *_: self.reload_all_options())
		self.graph_data_model.dfChanged.connect(lambda *_: self.reload_all_options())
		self.window.show()


		self.ui.cancelBtn.pressed.connect(self.window.close)
		self.ui.renameBtn.pressed.connect(self.attempt_rename)

		self.reload_all_options()

		self.ui.columnOptionsCombobox.currentTextChanged.connect(self.column_selection_changed)
		pass

	def column_selection_changed(self, new_selection : str):
		log.debug(f"Column selection changed to {new_selection}")
		self.reload_rename_options()


	def attempt_rename(self):
		col = self.ui.columnOptionsCombobox.currentText()
		from_lbl = self.ui.fromCombobox.currentText()
		to_lbl = self.toCombobox.currentText()

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
			self.ui.returnMsgLabel.setStyle("color: red")


	# def reload_rename_options(self):
	# 	self.set_column_options(self.model.get_lbl_columns)

	# def reload_column_options(self):
	# 	self.set_column_options(self.model.get_lbl_columns)

	def get_rename_options(self):
		curtext = self.ui.columnOptionsCombobox.currentText() 
		options = []
		try: 
			options = self.graph_data_model.df[curtext].unique()
			options = [str(i) for i in options]
		except KeyError as err:
			pass
	
		return options
		

		# if curtext in self.model.get_column_names:
		# 	self.model.

	def reload_rename_options(self):
		self.ui.fromCombobox.blockSignals(True)
		options = self.get_rename_options()
		if options is None or len(options) == 0:
			self.ui.fromCombobox.setEnabled(False)
			self.toCombobox.setEnabled(False)
		else:
			self.ui.fromCombobox.setEnabled(True)
			self.toCombobox.setEnabled(True)
			self.set_combobox_options(self.ui.fromCombobox, options)
			self.toCombobox.set_options(options)

			
		self.ui.fromCombobox.blockSignals(False)

	def reload_column_options(self):
		self.ui.columnOptionsCombobox.blockSignals(True)
		self.set_combobox_options(self.ui.columnOptionsCombobox, self.graph_data_model.get_lbl_columns())
		self.ui.columnOptionsCombobox.blockSignals(False)
		# self.set_combobox_options(self.ui.fromCombobox, self.)
		
	def reload_all_options(self):
		self.reload_column_options()
		self.reload_rename_options()



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

	