
"""Small implementation of a labeling widget using MVC, when model options are set, they are updated immediately
20220110
"""


import typing
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from mvts_analyzer.widgets import dropdown_add_option
from mvts_analyzer.widgets.dropdown_add_option import DropdownAddOption
from mvts_analyzer.graphing.graph_settings_model import GraphSettingsModel
import logging
log = logging.getLogger(__name__)

class LabelerWindowView(QtWidgets.QWidget):
	setLabelBtnPressed = QtCore.Signal(str, str) #When set label is being pressed, pass COL and LBL 
	columnOptionChanged = QtCore.Signal(str)

	def __init__(self, ):
		super().__init__()

		self.hide = False


		self.layout = QtWidgets.QVBoxLayout()

		#================ COL selector ================
		self.col_layout = QtWidgets.QHBoxLayout()
		# self.col_dropdown = DropdownAddOption(options=["kaas"])
		self.col_dropdown = QtWidgets.QComboBox()
		self.col_dropdown.setEditable(True) #Make editable
		self.col_layout.addWidget(QtWidgets.QLabel("Column Name:"), 1)
		self.col_layout.addWidget(self.col_dropdown, 8)
		self.layout.addLayout(self.col_layout)

		# self.col_dropdown.selectionEdited.connect(self.columnOptionChanged)
		self.col_dropdown.editTextChanged.connect(self.columnOptionChanged)
		
		#================ LBL selector ================
		self.lbl_layout = QtWidgets.QHBoxLayout()
		# self.lbl_dropdown = DropdownAddOption(options=[])
		self.lbl_dropdown = QtWidgets.QComboBox()
		self.lbl_dropdown.setEditable(True) #Make editable
		self.lbl_layout.addWidget(QtWidgets.QLabel("Label:"), 1)
		self.lbl_layout.addWidget(self.lbl_dropdown, 8)
		self.layout.addLayout(self.lbl_layout)

		#============= set Label button ===============

		self.lbl_btn_layout = QtWidgets.QHBoxLayout()
		self.lbl_btn_layout.setContentsMargins(0, 10, 0, 0)
		self.lbl_btn = QtWidgets.QPushButton("Set label")
		# self.lbl_btn.setStyleSheet('padding: 15px')
		self.lbl_btn.clicked.connect(lambda *_ : self._labelBtnPressed())

		self.lbl_btn_layout.addWidget(self.lbl_btn, 10)

		# self.lbl_select_gaps = QtWidgets.QCheckBox("Select Gaps")
		# self.lbl_btn_layout.addWidget(self.lbl_select_gaps, 1)


		self.layout.addLayout(self.lbl_btn_layout)
		self.setLayout(self.layout)

	def _labelBtnPressed(self):
		col = self.col_dropdown.currentText()
		label = self.lbl_dropdown.currentText()
		self.setLabelBtnPressed.emit(col,label)


	def set_lbl_column_options(self, options : typing.List[str], cur_option : str = None) -> None:

		cur_text = self.col_dropdown.currentText()

		self.col_dropdown.blockSignals(True)
		self.col_dropdown.clear()
		self.col_dropdown.addItems(options)
		if cur_option: #If current selection is specified
			self.col_dropdown.setEditText(cur_option)
		else:
			if cur_text in [self.col_dropdown.itemText(i) for i in range(self.col_dropdown.count())]:
				self.col_dropdown.setCurrentText(cur_text)
			else:
				self.col_dropdown.setCurrentIndex(0)
			# self.col_dropdown.setEditText(cur_text)
			
		self.col_dropdown.blockSignals(False)

	def set_lbl_lbl_options(self, options : typing.List[str], cur_option : str = None) -> None:

		cur_text = self.lbl_dropdown.currentText()

		self.lbl_dropdown.blockSignals(True)
		self.lbl_dropdown.clear()
		self.lbl_dropdown.addItems(options)
		if cur_option: #If current selection is specified
			self.lbl_dropdown.setEditText(cur_option)
		else:
			if cur_text in [self.lbl_dropdown.itemText(i) for i in range(self.lbl_dropdown.count())]:
				self.lbl_dropdown.setCurrentText(cur_text)
			else:
				self.lbl_dropdown.setCurrentIndex(0)
		self.lbl_dropdown.blockSignals(False)

# class LabelerWindowModel(QtCore.QObject):
# 	"A simple labeler window"
    
#     # fftZoomViewSignal = QtCore.Signal()


# 	def __init__(self, *args, **kwargs):
# 		super().__init__(*args, **kwargs)
# 		self.settings_layout = QtWidgets.QVBoxLayout(self)


# class LabelerWindowController(QtCore.QObject):
# 	dfChanged = QtCore.Signal(object)
# 	dfSelectionChanged = QtCore.Signal(object)


# 	def __init__(self, model : LabelerWindowModel, view : LabelerWindowView, graph_model : GraphSettingsModel):
# 		super().__init__()

# 		self.model = model
# 		self.view = view
# 		self.graph_model = graph_model


