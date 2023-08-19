

import sys, os
from PySide6 import QtCore, QtGui, QtWidgets
from mvts_analyzer.widgets.widget_list import WidgetList
from mvts_analyzer.widgets.dual_boxes import DualBox, LabelBox

import logging
log = logging.getLogger(__name__)


class DictEditor(WidgetList):
		
	# fileNameChanged = QtCore.Signal(str)

	dictEdited = QtCore.Signal(dict)
	dictChanged = QtCore.Signal(dict)

	def __init__(self,  dict = {}, left_editable = False, *args, **kwargs):
		if left_editable:
			super().__init__(widget_type=DualBox, fixed_height_increase=40, user_addable=False, *args, **kwargs)
		else:
			super().__init__(widget_type=LabelBox, fixed_height_increase=40, user_addable=False, *args, **kwargs)

		
		log.debug("Initializing DictEditor")
		self.layout = QtWidgets.QVBoxLayout()
		self.set_dict(dict)


	def set_dict(self, new_dict, left_editable = False):
		self.blockSignals(True)
		self.dict = new_dict
		self.set_widgetcount(0)
		self.set_widgetcount(len(new_dict))

		for index, ((key, val), widget) in enumerate(zip(new_dict.items(), self.widgets)):
			widget.set_texts(key, val)
			widget.boxEdited.connect(lambda x, key=key : self._onItemChange(key, x) ) #extra (key) is neccesary to bind variable
		self.blockSignals(False)


	def _onItemChange(self, key, texts):
		"""Handles changes of widgets in list

		Args:
			key (str): key to be changed
			texts ([str, str]): 2 strings (key + value)
		"""
		# log.debug(f"Item changed - key:{key} became: {texts}")
		self._set_val(key, *texts)
		self.dictEdited.emit(self.dict)
		

	def _set_val(self, key, newkey, newval):
		"""Set value in dictionary

		Args:
			key ([any]): key to be changed
			newkey (str): new key (could be the same as old key)
			newval (str): new value
		"""
		if key==newkey:
			self.dict[key] = newval
		else:
			del self.dict[key]
			self.dict[newkey] = newval

	def set_val(self, key, newkey, newval):
		"""Same as _set_val but also emits dictChanged event

		Args:
			key ([any]): key to be changed
			newkey (str): new key (could be the same as old key)
			newval (str): new value
		"""
		self.dictChanged.emit(self.dict)
