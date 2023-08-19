import sys, os
from typing import Iterable
from PySide6 import QtCore, QtGui, QtWidgets

from mvts_analyzer.utility.GuiUtility import create_qt_warningbox
import logging 

log = logging.getLogger(__name__)


#Simple double slider implementation - source: https://stackoverflow.com/questions/42820380/use-float-for-qslider
class DropdownAddOption(QtWidgets.QStackedWidget):
	""" Classic dropdown menu with an added "+" option, when chosen the user can type in a new value to add to options (and optionsEdited is emitted)"""
	
	selectionEdited = QtCore.Signal(object)
	selectionChanged = QtCore.Signal(object)
	optionsEdited = QtCore.Signal(object)

	def __init__(self, options = [], start_selection= None, add_symbol = "+"):
		super().__init__()

		self._options = options
		self._selection = None
		self._add_symbol = add_symbol
		self.combo_box = QtWidgets.QComboBox()



		self.adder_layout = QtWidgets.QHBoxLayout()
		self.textbox = QtWidgets.QLineEdit()
		self.adder_layout.addWidget(self.textbox, stretch = 10)
		self.confirm_btn = QtWidgets.QPushButton("OK")
		self.adder_layout.addWidget(self.confirm_btn, stretch=3)
		self.cancel_button = QtWidgets.QPushButton("Cancel")
		self.adder_layout.addWidget(self.cancel_button, stretch=3)
		

		self.container_widget = QtWidgets.QWidget()
		self.container_widget.setLayout(self.adder_layout) #Small container to fit in stacked widget

		self.addWidget(self.combo_box) #Add combobox (index 0)
		self.addWidget(self.container_widget) #Add "ADD" menu (index 1)


		self.cancel_button.clicked.connect(self._cancel_button_clicked) #Go back to combobox
		# self.cancel_button.clicked.connect(lambda x: self.combo_box.setCurrentIndex(0)) #Go back to combobox (and set to default)
		
		self.textbox.editingFinished.connect(self._textbox_editing_finished)
		self.confirm_btn.clicked.connect(self._confirm_button_clicked)
		self.combo_box.currentIndexChanged.connect(lambda *_ : self._selection_edited())

		self.setCurrentIndex(0)
		self._update_view()

		# self.setLayout(self.layout)

		#============= Final init =================
	
	def _textbox_editing_finished(self, *_):
		log.debug("Texbox editing finished")
		self._add_typed_option()


	def _confirm_button_clicked(self, *_):
		log.debug("Confirm button clicked")
		self._add_typed_option()
		
	def _cancel_button_clicked(self, *_):
		if self.selection == self._add_symbol: #If at add selection
			self.selection = " " #Set to "none" selection
		self.setCurrentIndex(0) 


	def clear(self):
		self.combo_box.clear()
	
	def addItems(self, texts : Iterable):
		self.combo_box.addItems(texts)

	def setCurrentText(self, text):
		self.combo_box.setCurrentText(text)

	def currentText(self):
		return self.combo_box.currentText()

	@property
	def selection(self):
		return self._selection
	
	@selection.setter
	def selection(self, new_selection):
		self._selection = new_selection
		self.selectionChanged.emit(new_selection)
		self._update_view()
	
	def _selection_edited(self):
		log.debug(f"Combobox changed to: {self.combo_box.currentText()}")
		if self.combo_box.currentText() == " " or len(self.combo_box.currentText()) == 0:
			self._selection = None
		elif self.combo_box.currentText() == self._add_symbol:
			self._update_view() #Set back to original selection
			self.setCurrentIndex(1) #To "add" window
			return
		else:
			self._selection = self._options[self.combo_box.currentIndex() - 1] # " " is inserted at the start

		log.debug(f"Selection became: {self._selection}")

		self.selectionChanged.emit(self._selection)
		self.selectionEdited.emit(self._selection)

	def _add_typed_option(self):
		self.textbox.blockSignals(True)
		self.confirm_btn.blockSignals(True)
		
		if self.currentIndex() == 0: #If already back to selectionbox
			self.textbox.blockSignals(False)
			self.confirm_btn.blockSignals(False)
			return

		new_txt = str(self.textbox.text())
		log.debug(f"Trying to add  text: {new_txt} to options list: {self._options}")
		if new_txt == "": #Dont add empty string
			
			self.textbox.blockSignals(False)
			self.confirm_btn.blockSignals(False)
			return

		if new_txt is self._add_symbol:
			self.combo_box.setCurrentIndex(0) #To default
			self.setCurrentIndex(0)
			# self.selection = None
				
			self.textbox.blockSignals(False)
			self.textbox.blockSignals(False)
			self.confirm_btn.blockSignals(False)
			return
		elif new_txt in self._options or new_txt == " ":
			create_qt_warningbox("Warning: this option already existed, now selecting it", "Warning")
			# self.set_options(self, self._op)
			self.combo_box.setCurrentText(new_txt)
		else:
			self._options.append(new_txt)
			self.optionsEdited.emit(self._options)
			
		if self.selection != new_txt:
			self.selectionEdited.emit(self._selection)
			self.selection = new_txt
		self.setCurrentIndex(0) #Go back to combobox
		self._update_view()

		self.textbox.blockSignals(False)
		self.confirm_btn.blockSignals(False)

	# def add_option(self):


	def _update_view(self):
		self.combo_box.blockSignals(True)
		self.combo_box.clear() #Remove options
		self.combo_box.addItems([" "] + [str(i) for i in self._options] + [self._add_symbol])
		self.combo_box.setCurrentText(str(self._selection))
		self.combo_box.blockSignals(False)


	def set_options(self, options):
		"Same as public function but does not add the add option and the 'none' option "
		self._options = list(options)
		if self._selection not in self._options:
			log.debug(f"Cur selection {self._selection} not found in new options {self._options} restting to ' '-option")
			self._selection = " " #Default selection (None) 
		self._update_view() 
		
	