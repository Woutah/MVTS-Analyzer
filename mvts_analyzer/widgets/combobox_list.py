"""
List of comboboxes, makes use of a WidgetList of type QtWidgets.QCombobox
"""
import logging
import typing
from PySide6 import QtCore, QtWidgets
from mvts_analyzer.widgets.widget_list import WidgetList


log = logging.getLogger(__name__)


class ComboboxList(WidgetList):

	"""
	Variable length list of comboboxes, makes use of a WidgetList of type QtWidgets.QCombobox
	"""

	selectionsChanged = QtCore.Signal(object) #Return string list of choices

	def __init__(self, **kwargs):
		super(ComboboxList, self).__init__(widget_type=QtWidgets.QComboBox, **kwargs)
		self.options = []
		self._selections = []

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
			if reset_boxcount or len(selections) > len(self._selections): #If boxcount should be reset
				self._set_box_count(len(selections)) #make sure that this is done beforehand
			for i in range(len(self._selections)): #pylint: disable=consider-using-enumerate
				if i < len(selections):
					self._selections[i] = selections[i]
				else:
					self._selections[i] = ""

		log.debug(f"Tried to set combobox selection to {selections}, resulting in {self._selections}, now refreshing")
		self._refresh_list()


	def set_options(self, options : typing.List[str]):
		"""
		Set the options of all comboboxes (assumes that all comboboxes share the same options)
		"""
		if "" not in options:
			options.insert(0, "")
		log.debug(f"Setting options of cobobox list to {options}")
		self._set_options(options)
		self._refresh_list()

	def set_selections(self, selections : typing.List[str], reset_boxcount = True):
		"""
		Set the selected options for all comboboxes. If reset_boxcount is True, the number of comboboxes will be set to
		the length of the selections list
		"""
		self._set_selections(selections, reset_boxcount)

	def set_selections_and_options(self, options : typing.List[str], selections : typing.List[str]):
		"""
		Set both options and selections of the comboboxes
		"""
		self._set_options(options)
		self._set_selections(selections)


	def get_selections(self, filter_empty = True):
		"""
		Get the list of currently selected items in the comboboxes
		"""
		return [item for item in self._selections if (
			item is not None
			and (len(item) > 0 or not filter_empty)
		)]

	def get_options(self):
		"""
		Returns the current list of options for the comboboxes
		"""
		return self.options


	def _refresh_list(self):
		"""
		Refreshes the list by clearing all items and setting again
		"""
		log.debug(f"combolist len {len(self.widgets)} - selections: {self._selections}")
		for i, combo in enumerate(self.widgets):
			combo.blockSignals(True)
			combo.clear() #Clear items
			combo.addItems(self.options)
			combo.setCurrentText(self._selections[i])
			combo.blockSignals(False)
