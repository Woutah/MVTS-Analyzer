
from PySide6 import QtWidgets, QtCore
from numpy import select
from mvts_analyzer.utility import GuiUtility
from pydoc import locate
import typing
import logging
log = logging.getLogger(__name__)

from mvts_analyzer.widgets.widget_list import WidgetList


# from mvts_analyzer.windows.custom_widgets import datastructures



class ComboboxList(WidgetList):

	"""
	Variable length list of comboboxes, makes use of a WidgetList of type QtWidgets.QCombobox
	"""

	selectionsChanged = QtCore.Signal(object) #Return string list of choices

	def __init__(self, options = None, *args, **kwargs):
		super(ComboboxList, self).__init__(widget_type=QtWidgets.QComboBox, *args, **kwargs)
		# self.combo_list = WidgetList(QtWidgets.QComboBox, fixed_height_increase=fixed_height_increase)
		# self.layout.addWidget(self.combo_list)

		self.options = []
		self._selections = []

		# self.set_options(["A", "B", "C"])
		# self.choicesChanged.connect(lambda x: print(f"kaas: {self.get_selections()}"))

	def _set_box_count(self, count : int):
		# self.combo_list.set_widgetcount(count)
		while len(self.widgets) > count:
			self.pop()
			# self.pop_widget()
			# self._selections.append("")
		while len(self.widgets) < count:
			self.append()
			# self._selections.pop()
			# self.push_widget()




	def append(self):
		super().append()
		self._selections.append("")
		cur_index = len(self.widgets)-1
		self.widgets[-1].currentTextChanged.connect(
				lambda x:
					self._handle_edit(cur_index, x)
			)
		self._refresh_list()
		# self.selectionsChanged.emit(self.get_selections())


	def pop(self):
		if len(self.widgets) > 0:
			super().pop() 
			self._selections.pop()
			# log.debug(f"{self._selections}")
		self.selectionsChanged.emit(self.get_selections())




	def _handle_edit(self, index : int, newtext : str):
		if self._selections[index] != newtext:
			self._selections[index] = newtext 
			self.selectionsChanged.emit(self.get_selections())

	def _set_options(self, options : typing.List[str]):
		if self.options != options:
			self.options = options

	def _set_selections(self, selections: typing.List[str], reset_boxcount : bool = True ):
		if self._selections != selections:
			if reset_boxcount or len(selections) > len(self._selections): #If boxcount should be reset (this would remove all empty boxes on model update)
				self._set_box_count(len(selections)) #make sure that this is done beforehand, otherwise the new self._selections will be popped as well
			for i in range(len(self._selections)):
				if i < len(selections):
					self._selections[i] = selections[i]
				else:
					self._selections[i] = ""
		
		log.debug(f"Tried to set combobox selection to {selections}, resulting in {self._selections}, now refreshing")
		self._refresh_list()

	
	def set_options(self, options : typing.List[str]):
		if "" not in options:
			options.insert(0, "")
		log.debug(f"Setting options of cobobox list to {options}")
		self._set_options(options)
		self._refresh_list()

	def set_selections(self, selections : typing.List[str], reset_boxcount = True):
		self._set_selections(selections, reset_boxcount)
	
	def set_selections_and_options(self, options : typing.List[str], selections : typing.List[str]):
		self._set_options(options)
		self._set_selections(selections)


	def get_selections(self, filter_empty = True):
		return [item for item in self._selections if (
			item is not None 
			and (len(item) > 0 or not filter_empty) 
		)]

	def get_options(self):
		return self.options
		# for i, combo in enumerate(self.combo_list):
		# 	combo = QtWidgets.QComboBox()
		# 	cur = combo.currentText()


	def _refresh_list(self):
		"""
		Refreshes the list by clearing all items and setting again
		"""

		# self.blockSignals(False)
		log.debug(f"combolist len {len(self.widgets)} - selections: {self._selections}")
		for i, combo in enumerate(self.widgets):
			combo.blockSignals(True)
			combo.clear() #Clear items
			combo.addItems(self.options)
			# print(f"adding {self.options}")
			combo.setCurrentText(self._selections[i])
			combo.blockSignals(False)
		# self.blockSignals(True)