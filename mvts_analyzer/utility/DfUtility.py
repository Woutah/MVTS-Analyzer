import pandas as pd
import numpy as np
import logging
log = logging.getLogger(__name__)
from enum import Enum


class DfSaveType(Enum): #TODO: is this handy? 
    no_type = 0
    from_file = 1
    from_database = 2



def get_fft_columns(dataframe : pd.DataFrame | None):
	"""Get a dictionary of the form:
			{ fft_col1 : lines }
		Where lines denotes the amount of line.
		All columns containing numpy arrays are considered "fft columns".
		Linecount is determined by the first not-none value in these array columns.
	Returns:
		fft_cols[dict]: dictionary of the form { fft_col : lines }
	"""
	fft_cols = {}
	if dataframe is None: 
		return {}
	
	cols = dataframe.select_dtypes(include=['object', 'category']) #Category/object 
	for cur_col in cols: #Go over potential columns
		idx =  cols[cur_col].first_valid_index()
		if idx is not None:
			var = cols[cur_col].loc[idx]
			if isinstance(var, (list, type(np.array))):
				fft_cols[cur_col] = len(var)
	log.debug("Found FFT columns (non-none columns with list/np.array) {fft_cols}")
	return fft_cols


def get_lbl_columns(dataframe: pd.DataFrame | None):
	"""
	Get the names of columns containing only strings (lbl columns)

	Args:
		dataframe (pd.DataFrame): The dataframe to check

	Returns:
		list: List of strings with column names of all columns that only contain strings (label columns)
	"""
	if dataframe is None: #If nothing loaded 
		return []
	lbl_cols = list(dataframe.select_dtypes(include=['Int64', 'int', 'int64', 'category', "string"])) #TODO: always include ints? TODO: "string" dtype is experimental as of 22-10-2022 
	
	cols = dataframe.select_dtypes(include=['object']) #Specific case -> only str columns 
	for cur_col in cols: #Go over potential columns
		idx =  cols[cur_col].first_valid_index()
		if idx is not None:
			var = cols[cur_col].loc[idx]
			# log.debug(f"col {cur_col} -> first val type: {type(var)}")
			if isinstance(var, (str)): 
				lbl_cols.append(cur_col)
	log.debug(f"Found label columns: {lbl_cols}")
	return lbl_cols

def save_dataframe(dataframe : pd.DataFrame, save_path : str, locs=None):
	if dataframe is None or dataframe.empty:
		msg = "Error: could not save dataframe - dataframe is not set or empty"
		log.error(msg)
		return False, msg
		# GuiUtility.create_qt_warningbox("Error: could not save dataframe - dataframe is not set or empty", "Error")

	if locs is None:  #If no locs have been provided -> select all
		locs = dataframe.index

	file_type = save_path.rsplit(".", 1)[-1] #assume file extension 
	if file_type == "pkl":
		dataframe.loc[locs].to_pickle(save_path)
	elif file_type == "xlsx":
		fft_cols = get_fft_columns(dataframe) #Excel doesn't handle arrays very well, so on't use them
		dataframe.loc[locs, dataframe.columns.difference(fft_cols.keys())].dropna(how='all', axis=1).to_excel(save_path, sheet_name="Sheet1") #Drop empty columns TODO: let user pick sheet? 
	else:
		raise NotImplementedError

	msg = f"Saved df to {save_path}"
	log.info(msg)
	return True, msg

def load_dataframe_using_file_extension(file_source : str):
	"""
	Load a dataframe from file, using the file extension to determine the filetype
	"""
	try:
		filetype = file_source.rsplit(".", 1)[-1]
		if filetype == "pkl":
			new_df = pd.read_pickle(file_source)
		elif filetype == "xlsx":
			new_df = pd.read_excel(file_source)
		else:
			raise NotImplementedError(f"Filetype {filetype} not implemented for loading dataframes...")

		return True, f"Succesfully loaded dataframe form {file_source}", new_df
	except Exception as ex:
		msg = f"Could not append data from selected file ({file_source}): {ex}"
		log.warning(msg)
		return False, msg, None
	
	return False, "Unknown error - reached end of function", None