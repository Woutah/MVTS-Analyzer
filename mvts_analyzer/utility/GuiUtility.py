
#TODO: put this in main directory and make accesible everywhere 

from pydoc import locate
import logging

from numpy import iterable
log = logging.getLogger(__name__)
import datetime
import dateutil
import typing
from PySide6 import QtWidgets, QtCore

def get_dict_entry(thedict : dict, location : list):
	"""
	Args:
		thedict (dict): the full configuration dict (including metadata)
		location (list): list of nested location, e.g. ["entry", "subtype"]

	Returns:
		bool: Whether full-config layout is valid
	"""
	x = None
	try:
		cur = thedict
		for i in location: #walk through nested location
			cur = cur[i]
		x = cur
		# x = thedict[location]
	except (KeyError, TypeError) as err:
		log.error(f'Could find location {location} , error: {err}')
		return None
	
	return x


def safe_parse_strings(item, cast_using : str, desired_type = "None"): 
	"""Safe PARSING method for input items using strings for types and cast methods

	Args:
		item (any): item to be cast
		cast_type (str): Method used to parse/cast the item 
		desired_type_str (str): type to-be cast to ("int", "str", "float" . supported)

	Returns:
		any: the cast type, or None if failed
	"""
	new_val = None

	# desired_type = None
	#=================Cast desired type
	
	try:
		desired_type = eval(desired_type)
		if isinstance(item, desired_type): #If already the right type --> just return 
			log.info(f"Item: {item} already of desired type: {desired_type}, returning it")
			return item
		else:
			log.info(f"Item: {item} not of desired type: {desired_type}, now trying to parse it...")
	except (ValueError, TypeError) as err:
		log.info(f"Could not cast desired_type (string): {desired_type} to a valid comparable type ({err}), now trying to cast...")
	

	try:
		new_type = eval(cast_using)
		new_val = new_type(item) #Else, cast
	except (ValueError, TypeError) as err:
		log.info(f"Could not cast {str(new_val)} to a type specified by conversion function {str(cast_using)}, resetting to unknown - Err: {err}")

	return new_val


#TODO: rename to safe_parse after removing all occurences of previous versions
def safe_parse_new(item, cast_using : typing.Callable | None = None, default=None) -> typing.Tuple[bool, object]: 
	"""Safe PARSING method for input items

	Args:
		item (any): item to be cast
		desired_type (typing.Type): type to-be cast to (int, str, float etc)
		cast_type (str): Method used to parse/cast the item, if none, try to use default converter

	Returns:
		tuple with;
			1. Whether conversion was succesful (exceptionless)
			2. The parsed value
	"""
	new_val = None

	# desired_type = None
	#=================Cast desired type
	
	# if isinstance(item, desired_type): #If already the right type --> just return 
	# 	log.debug(f"Item: {item} already of desired type: {desired_type}, returning it")
	# 	return True, item

	# log.debug(f"Item: {item} not of desired type: {desired_type}, now trying to parse it...")

	# if cast_using is None: #If no explicit conversion method defined
	# 	cast_using = desired_type

	try:
		new_val = cast_using(item) #Else, cast
	except (ValueError, TypeError) as err:
		log.info(f"Could not cast {str(new_val)} to a type specified by conversion function: {str(cast_using)}, returning None - Err: {err}")
		return False, default
	
	return True, new_val

def clip(val_actual, val_min = None, val_max = None):
	if val_actual is None:
		return None
	clipped = val_actual

	if val_min is not None:
		clipped = max(val_min, clipped)
	
	if val_max is not None:
		clipped = min(val_max, clipped)

	return clipped 





class iterable_display_window(QtWidgets.QMainWindow):
	def __init__(self, value, parent= None, *args, **kwargs) -> None:
		super().__init__(parent = None, *args, **kwargs)
		self.treewidget = QtWidgets.QTreeWidget()

		self.toplevelitem = QtWidgets.QTreeWidgetItem()
		self.treewidget.addTopLevelItem(self.toplevelitem)
		self.setCentralWidget(self.treewidget)
		self._fill_item(self.toplevelitem, value)

	def update(self, new_dict):
		del self.toplevelitem
		self.treewidget.takeTopLevelItem(0)
		self.toplevelitem = QtWidgets.QTreeWidgetItem()
		self.treewidget.addTopLevelItem(self.toplevelitem)
		# self.treewidget.TopLevel
		self._fill_item(self.toplevelitem, new_dict)


	def _fill_item(self, widget, value):
		# from PySide6.QtWidgets import QTreeWidgetItem
		# item.setExpanded(True)
		widget.setExpanded(True)
		if type(value) is dict:
			for key, val in sorted(value.items()):
				child = QtWidgets.QTreeWidgetItem()
				child.setText(0, str(key))
				widget.addChild(child)
				self._fill_item(child, val)
				# widget.add_
		elif type(value) is list:
			for val in value:
				child = QtWidgets.QTreeWidgetItem()
				widget.addChild(child)
				if type(val) is dict:      
					child.setText(0, '[dict]')
					self._fill_item(child, val)
				elif type(val) is list:
					child.setText(0, '[list]')
					self._fill_item(child, val)
				else:
					child.setText(0, val)              
				child.setExpanded(True)
		else:
			child = QtWidgets.QTreeWidgetItem()
			child.setText(0, str(value))
			widget.addChild(child)
		

def clear_layout(layout : QtWidgets.QLayout):
	#Source: https://stackoverflow.com/questions/4528347/clear-all-widgets-in-a-layout-in-pyqt
	#Should remove widgets and prevent long-term storage TODO: works for nested layouts? 
	for i in reversed(range(layout.count())): 
		widgetToRemove = layout.itemAt(i).widget()
		# remove it from the layout list
		layout.removeWidget(widgetToRemove)
		# remove it from the gui
		widgetToRemove.setParent(None)

def create_qt_warningbox(text : str, box_title : str = "Message"):
	msg = QtWidgets.QMessageBox()
	msg.setIcon(QtWidgets.QMessageBox.Icon.Warning)
	msg.setText(f"{text}")
	msg.setWindowTitle(box_title)
	# msg.setDetailedText("The details are as follows:")
	# msg.setInformativeText("This is additional information")
	msg.exec_()