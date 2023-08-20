
#TODO: put this in main directory and make accesible everywhere

import logging
import traceback
import typing

from PySide6 import QtWidgets, QtGui

log = logging.getLogger(__name__)

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
	"""Safe parsing method for input items using strings for types and cast methods

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
		desired_type = eval(desired_type) #pylint: disable=eval-used
		if isinstance(item, desired_type): #If already the right type --> just return
			log.info(f"Item: {item} already of desired type: {desired_type}, returning it")
			return item
		else:
			log.info(f"Item: {item} not of desired type: {desired_type}, now trying to parse it...")
	except (ValueError, TypeError) as err:
		log.info(f"Could not cast desired_type (string): {desired_type} to a valid comparable type ({err}), now trying to cast...")


	try:
		new_type = eval(cast_using) #pylint: disable=eval-used
		new_val = new_type(item) #Else, cast
	except (ValueError, TypeError) as err:
		log.info(f"Could not cast {str(new_val)} to a type specified by conversion function {str(cast_using)}, resetting to unknown - Err: {err}")

	return new_val


#TODO: rename to safe_parse after removing all occurences of previous versions
def safe_parse_new(item, cast_using : typing.Callable, default=None) -> typing.Tuple[bool, object]:
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
	"""Clipping function, clips val_actual to be between val_min and val_max"""
	if val_actual is None:
		return None
	clipped = val_actual

	if val_min is not None:
		clipped = max(val_min, clipped)

	if val_max is not None:
		clipped = min(val_max, clipped)

	return clipped



def create_qt_warningbox(text : str, box_title : str = "Message"):
	"""One-liner to create and show a qt warning box"""
	msg = QtWidgets.QMessageBox()
	msg.setIcon(QtWidgets.QMessageBox.Icon.Warning)
	msg.setText(f"{text}")
	msg.setWindowTitle(box_title)
	msg.exec_()



def catch_show_exception_in_popup_decorator(
		re_raise : bool = True,
		add_traceback_to_details : bool = True,
		custom_error_msg : str | None = None,
		title : str = "Error",
		target_width : float | int | None = 500
	):
	"""Decorator that catches ALL exceptions and logs them. Also shows a message box if the app is running.
	TODO: second argument with list of exceptions to catch?
	Args:
		func (callable): The function which should be called
		re_raise (bool, optional): If True, the exception will be re-raised after being logged. Defaults to True.
		target_width (float | int, optional): Desired width of the message box - if int in pixels, if float
			width of screen size. If None, determine size automatically. Defaults to 500.
	"""
	def catch_show_exception_in_popup(func : typing.Callable):
		def wrapper(*args, **kwargs):
			try:
				return func(*args, **kwargs)
			except Exception as exception: #pylint: disable=broad-except
				log.exception(f"Exception in {func.__name__}: {exception}")
				#Also create a message box
				#Check if app is running, if so -> show message box
				if QtWidgets.QApplication.instance() is not None:
					msg = QtWidgets.QMessageBox()
					msg.setWindowTitle(title)
					msg.setIcon(QtWidgets.QMessageBox.Icon.Critical)
					if custom_error_msg is not None:
						msg.setText(custom_error_msg)
					else:
						msg.setText(f"<b>An error occured in {func.__name__}</b>")
					msg.setInformativeText(f"{type(exception).__name__}: {exception}")
					trace_msg = f"Traceback:\n{traceback.format_exc()}"
					if add_traceback_to_details:
						msg.setDetailedText(trace_msg)
					msg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
					if target_width is not None:
						if isinstance(target_width, float):
							desired_width = int(target_width * QtGui.QGuiApplication.primaryScreen().geometry().width())
						else:
							desired_width = target_width
						spacer = QtWidgets.QSpacerItem(
							desired_width,
							0,
							QtWidgets.QSizePolicy.Policy.Minimum,
							QtWidgets.QSizePolicy.Policy.Expanding
						)
						layout : QtWidgets.QGridLayout = msg.layout() #type: ignore #Msgbox contains grid layout
						layout.addItem(spacer, layout.rowCount(), 0, 1, layout.columnCount())
					msg.exec()
				if re_raise:
					raise
		return wrapper
	return catch_show_exception_in_popup
