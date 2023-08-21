"""
Implements several general-utility functions
"""
import datetime
import logging
import math
import os
import pathlib
import platform
import subprocess

import numpy as np

log = logging.getLogger(__name__)


def get_full_path(subpath):
	"""Gets full path using the current directory (of this script) + the subpath

	Args:
		subpath (str): subpath in current directory

	Returns:
		str: the full path
	"""
	cur_dir = pathlib.Path(__file__).parent.absolute()
	log.debug(f"Parent path: {pathlib.Path(__file__).parent.absolute()}")
	return os.path.join(cur_dir, subpath)

def create_path(path : str):
	"""creates path if it does not yet exist 

	Args:
		path (str): the full path to be created if it does not exist
	"""
	if not os.path.exists(path):
		os.makedirs(path)




def datetime_to_iso8601(date_time : datetime.datetime) -> str:
	"""Generates iso8601 string from datetime

	Args:
		date_time (datetime.datetime): datetime of to-be-converted timestamp

	Returns:
		string: string in isoformat (e.g. 2020-10-16T13:53:11.000Z)
	"""

	return date_time.isoformat()


def datetime_to_timestr(date_time : datetime.datetime) -> str        :
	"""Extracts time from datetime format

	Args:
		date_time (datetime.datetime): date/time as datetime.datetime format

	Returns:
		str: the time from the datetime 
	"""
	# return datetime_to_iso8601(datetime).split('T')[1].split('+')[0]
	return datetime_to_iso8601(date_time).split('+')[0]


def open_file_editor(filepath): #for testing purposes  #TODO: make sure this does not crash the system
	"""Opens passed filepath in the os editor

	Args:
		filepath (string): Path to file 
	"""
	if platform.system() == 'Darwin':       # macOS
		subprocess.call(('open', filepath))
	elif platform.system() == 'Windows':    # Windows
		os.startfile(filepath)
	else:                                   # linux variants
		subprocess.call(('xdg-open', filepath))



def overwrite_to_file(filename, content, encoding="utf-8"):
	"""Simple function that (over)writes passed content to file 

	Args:
		filename (str): name of the file including extension
		content (str): what to write to file
	"""
	with open(filename, "w", encoding=encoding) as file:
		file.write(content)

def get_first_occurence(arr : np.ndarray, elem):
	"""Get first occurency in numpy array   

	Args:
		arr (np.array): the array
		elem (any type): The element to be searched for

	Returns:
		int: at what location the first occurence is found
	"""
	for i, cur_elem in enumerate(arr):
		if elem == cur_elem:
			return i
	return -1


def find_nearest_idx_sorted(array,value):
	"""Source: https://stackoverflow.com/questions/2566412/find-nearest-value-in-numpy-array
	"""
	idx = np.searchsorted(array, value, side="left")
	if idx > 0 and (idx == len(array) or math.fabs(value - array[idx-1]) < math.fabs(value - array[idx])):
		return idx-1
	else:
		return idx
