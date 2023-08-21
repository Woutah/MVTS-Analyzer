"""
Implements classes that contain the data for plotting (dataframe). Also keeps track of the sources of that data.
Differs from graph-settings(-data) in that this contains only the actual data, not the settings for plotting.

Separated from the graph-settings so that we can have multiple graphs operating on the same data, but different
display settings.
"""

import datetime
import logging
import time
import traceback
import typing
from enum import Enum
import pandas as pd
from PySide6 import QtCore

# from mvts_analyzer.utility import GuiUtility
from mvts_analyzer.utility import DfUtility
from mvts_analyzer.widgets.datastructures import LimitedRange

log = logging.getLogger(__name__)

class OperationType(Enum):
	"""Methods used when loading new data"""
	APPEND = 0 #Add to current
	OVERWRITE = 1 #Overwrite current
	COMPLEMENT = 2 #Everything except

# class GraphSettingsModel(QtCore.QObject):
class GraphData(QtCore.QObject):
	"""
	Contains all plot-data (mainly a dataframe) and all help-functions related to manipulating the data. e.g.
	hiding datapoints, changing selection, changing labels etc.

	Separated from the graph-settings so that we can have multiple graphs with the same data, but different settings.

	"""
	dfChanged = QtCore.Signal() #The dataframe changed
	dfSelectionChanged = QtCore.Signal(object) #The dataframe selection changed
	fileSourceChanged = QtCore.Signal(str) #The file-source changed
	hiddenDatapointsChanged = QtCore.Signal(object) #The hidden (non-plotted) datapoints changed

	def __init__(self, df_path = None):
		super().__init__()

		self._df : pd.DataFrame | None = None
		self._df_selection : set = set([]) #Set of pandas locs
		self._file_source : str = ""

		if df_path is not None:
			try:
				self.load_from_file(df_path)
			except Exception as err: #pylint: disable=broad-exception-caught
				log.error(f"Could not load from file: {err}")

		self.hidden_datapoints = set([]) #TODO: globally hidden datapoints, is somewhat different from view-filters. Although

		self._dt_col = "DateTime"


	def hide_selection(self):
		"""Hide the currently selected datapoints"""
		self.hide_datapoints(self._df_selection)

	def hide_all_datapoints_except_selection(self):
		"""Hide all datapoints except those selected"""
		self.hide_all_datapoints_except(self._df_selection)

	def hide_datapoints(self, idxes : set | None):
		"""Hide the passed (by pandas-idx) datapoints

		Args:
			idxes (set): The indexes to hide
		"""
		if idxes is None:
			return
		log.debug("Hiding some datapoints")
		firstlen = len(self.hidden_datapoints)
		self.hidden_datapoints.update(idxes)

		if firstlen != len(self.hidden_datapoints):
			self.hiddenDatapointsChanged.emit(self.hidden_datapoints)


	def unhide_all_datapoints(self):
		"""Reset the hidden datapoints - no datapoints will be hidden"""
		log.debug("Unhiding all datapoints")
		if len(self.hidden_datapoints) > 0:
			self.hidden_datapoints = set([])
			self.hiddenDatapointsChanged.emit(self.hidden_datapoints)

	def hide_all_datapoints_except(self, idxes : set):
		"""Hide all datapoints except those passed (by pandas-idx)

		Args:
			idxes (set): The indexes to keep visible
		"""
		if self._df is None:
			return
		all_indx = set(list(self._df.index))
		self.hidden_datapoints = all_indx - idxes
		self.hiddenDatapointsChanged.emit(self.hidden_datapoints)

	def flip_hidden(self):
		"""
		Flip the hidden datapoints, i.e. if some datapoints are hidden, unhide them, and vice versa
		"""
		self.hide_all_datapoints_except(self.hidden_datapoints)

	def get_df_len(self) -> int:
		"""Return the length of the current dataframe (0 if no dataframe is loaded)"""
		if self._df is None:
			return 0
		return len(self._df)

	@property
	def file_source(self):
		"""Returns the current file-source"""
		return self._file_source

	@file_source.setter
	def file_source(self, new_file_source : str):
		"""
		We cannot set the file-source directly, the load_from_file functions should be used instead, which will
		also update the file-source.

		Args:
			new_file_source (str): The new file-source
		"""
		raise NotImplementedError("Load new file using function instead of just setting path")

	@property
	def df_selection(self):
		"""
		Returns the current dataframe selection as a list(! not a set!) of indexes
		"""
		return list(self._df_selection)

	@df_selection.setter
	def df_selection(self, new_selection : set):
		"""Overwrite the current dataframe-selection"""
		self._df_selection = new_selection #TODO: check for change?
		self.dfSelectionChanged.emit(new_selection) #Emit new selection

	def set_df_selection(self,
				new_selection : set,
				mode : OperationType = OperationType.OVERWRITE,
				fill_gaps_ms : int = 0
			):
		"""Change the dataframe selection, can use multiple opreations (APPEND, OVERWRITE, COMPLEMENT)

		Args:
			new_selection (set): The newly selected points
			mode (OperationType, optional): What to do with old selection, can either reuse (APPEND/COMPLEMENT) or
				completely overwrite. Defaults to OperationType.OVERWRITE.
			fill_gaps_ms (int, optional): Whether to fill gaps between datapoints, e.g. if t=1 and t=3, then t=2
				might not be selected only because the user did not select a column that contained that specific value
				when fillgaps_ms is nonzero, all time-gaps in the selected datapoints (max size fillgaps_ms)
				are also selected e.g. (if dataframe contains data every second):

				t(s)=[1, 5, 7] with fill_gaps_ms = 4000 would result in t(s)=[1, 2, 3, 4, 5, 6, 7]
				t(s)=[1, 5, 7] with fill_gaps_ms = 2000 would result in t(s)=[1, 5, 6, 7]
				t(s)=[1, 5, 7] with fill_gaps_ms = 1000 would result in t(s)=[1, 5, 7]

				Defaults to 0.
		"""
		assert isinstance(new_selection, set)
		if self._df is None:
			return

		before_time = time.perf_counter()


		if len(new_selection) >= 2 and fill_gaps_ms > 0: #Only if more than 2 datapoints and fill_gaps is turned on
			log.debug(f"Settings GraphData selection in mode {mode} - filling gaps of size (ms): {fill_gaps_ms}")
			time_selection = self._df[[self._dt_col]].copy()
			time_selection["mask"] = False
			time_selection.loc[list(new_selection), "mask"] = True
			time_selection["indx"] = self._df.index
			time_selection.index = time_selection[self._dt_col] #type:ignore

			time_selection.sort_index(inplace=True) #Sort ascending (dt=0  -> indx = 0)

			#We have to do the following operation twice to account for left + right
			time_selection["mask"] = (
				#If left + right aligned rolling find at least 1 entry -> select this one
				((time_selection["mask"].rolling(f"{int(fill_gaps_ms/2)}ms", closed='both').sum()) > 0)
				& (time_selection["mask"][::-1].rolling(f"{int(fill_gaps_ms/2)}ms", closed='both').sum()[::-1] > 0)
			)
			time_selection["mask"] = (
				#Do this a second time to account for left/right
				((time_selection["mask"].rolling(f"{int(fill_gaps_ms/2)}ms", closed='both').sum()) > 0)
				& (time_selection["mask"][::-1].rolling(f"{int(fill_gaps_ms/2)}ms", closed='both').sum()[::-1] > 0)
			)

			new_selection = set(time_selection.loc[time_selection["mask"], "indx"]) #Take indexes where time selection
			log.debug(f"Filling gaps in selection took: {time.perf_counter() - before_time}")

		if mode == OperationType.APPEND:
			prev = len(self._df_selection)
			self._df_selection = self._df_selection.union(new_selection)
			if prev != len(self._df_selection): #If selection actually changed
				self.dfSelectionChanged.emit(self._df_selection) #Emit new selection
		elif mode == OperationType.OVERWRITE:
			self._df_selection = new_selection #TODO: check for change?
			self.dfSelectionChanged.emit(self._df_selection ) #Emit new selection
		elif mode == OperationType.COMPLEMENT:
			prev = len(self._df_selection)
			self._df_selection = self._df_selection - new_selection
			if prev != len(self._df_selection): #If selection actually changed
				self.dfSelectionChanged.emit(self._df_selection ) #Emit new selection



		# log.debug(f"Model selection: {self._df.loc[new_selection]}")


	def get_column_type(self, column : str):
		"""Return the type of a column by name"""
		if self._df is not None and column in self._df:
			return self._df.dtypes[column]
		return type(None)





	def get_df_datetime_range(self):
		"""Get the datetime range for the current dataframe, if empty or no datetime entries,
		this range will be ((1900,1,1), (1900,1,1))

		Returns:
			tuple: A tuple of two datetimes, the first one being the date of the oldest entry in the dataframe,
				the other the most recent entry in the dataframe
		"""
		if self._df is None or self._dt_col not in self._df.columns: #If no dataframe or no datetime column
			return (datetime.datetime(1900, 1, 1), datetime.datetime(1900, 1, 1))
		else:
			maxval = self._df.max(axis=0)[self._dt_col] # get most recent entry
			minval = self._df.min(axis=0)[self._dt_col] # get oldest entry
			minval = minval.to_pydatetime(minval)
			maxval = maxval.to_pydatetime(maxval)
			return (minval,maxval)


	def get_column_names(self):
		"""Get the column names as a list

		Returns:
			List[str]: List of strings (columns)
		"""
		if self._df is None:
			return []
		else:
			return list(self._df.columns)

	@property
	def df(self): #pylint: disable=invalid-name
		"""Return _df NOTE: this is not a copy!!!"""
		return self._df


	def get_col_limrange(self, col : str | None):
		"""Get the limrange for a column (min/max), pd.Timestamp columns arre converted to pydatetimes

		Args:
			col (str): column

		Returns:
			LimitedRange: datastructure which contains min/max values
		"""
		if self._df is not None and col is not None and col in self._df: #TODO: datetime separately?
			maxval = self._df[col].max(axis=0) # column AAL's max
			minval = self._df[col].min(axis=0) # column AAL's min
			if isinstance(maxval, pd.Timestamp):
				log.debug("Maxval was timestamp, converting to datetime")
				maxval = maxval.to_pydatetime(maxval) #type: ignore
			if isinstance(minval, pd.Timestamp):
				log.debug("Minval was timestamp, converting to datetime")
				minval = minval.to_pydatetime(minval) #type: ignore
				log.debug(f"Type is now {type(minval)}")

			log.debug(f"Col ({col}) limrange resulted in : {minval} {maxval}")

			return LimitedRange(minval, maxval, minval, maxval) #TODO: always like this?
		return LimitedRange()

	def get_fft_columns(self):
		"""Return the fft-capable column (columns that contain numpy arrays)"""
		return DfUtility.get_fft_columns(self._df)

	def get_lbl_columns(self):
		"""Return the label-columns (columns that contain str items)"""
		return DfUtility.get_lbl_columns(self._df)


	def set_selection_lbls(self, column : str, label : typing.Any):
		"""Set labels of selected data

		Args:
			column (str): The column in which the labels will be set
			label (any): The new label (can be string, int, Int64 etc)
		"""
		if self._df is None:
			raise ValueError("No dataframe loaded, cannot set labels")

		if column is not None and len(column) > 0 and self._df_selection is not None:
			selection = list(self.df_selection)
			self._df.loc[selection, column] = label #type: ignore
			log.debug(f"Columns are now: {self._df.columns}")
			self.dfChanged.emit()
			return True
		return False

	def save_df_selection(self, save_path : str):
		"""Save only the selected datapoints to a file"""
		if self._df is None:
			raise ValueError("No dataframe loaded, cannot save selection.")
		return DfUtility.save_dataframe(self._df.loc[list(self._df_selection)], save_path=save_path)

	def save_df_not_hidden_only(self, save_path : str):
		"""Save all non-hidden datapoints to a file (is different from view-only save)"""
		if self._df is None:
			raise ValueError("No dataframe loaded, cannot save dataframe.")
		all_indx = set(list(self._df.index))
		tosave = all_indx - self.hidden_datapoints
		return DfUtility.save_dataframe(self._df.loc[list(tosave)], save_path=save_path)

	def save_df(self, save_path : str):
		"""Save the whole dataframe to a file"""
		if self._df is None:
			raise ValueError("No dataframe loaded, cannot save dataframe.")
		return DfUtility.save_dataframe(self._df, save_path)




	def rename_lbls(self, column : str, transform_dict : dict):
		"""Renames a label in a column if that label-column exists
			NOTE: the string 'None' will be inserted as python None (Nulltype)
		Args:
			column (str): The column in which the to-be-renamed label resides
		"""
		if self._df is None:
			raise ValueError("No dataframe loaded, cannot rename labels.")

		for key,item in transform_dict.items():
			if item == "none" or item == "None": #Insert "None" string as None
				transform_dict[key] = None

		try:
			self._df[column] = self._df[column].replace(transform_dict)
		except Exception as err: #pylint: disable=broad-exception-caught
			return False, str(err)

		returnmsg = [f"{key} -> {val}" for key,val in transform_dict.items()]

		return True, f"Successfully renamed labels in column: '{column}' using: {', '.join(returnmsg)}"

	def merge_columns(self,
				src_column : str,
				dst_column : str,
				mode : typing.Literal["Source priority", "Destination priority"] = "Source priority",
				preserve_source : bool = False,
				astype : str | None = None
			):
		"""
		Merge two columns into one, either by overwriting the destination column, or by creating a new column.

		Args:
			src_column (str): The source-column
			dst_column (str): The destination column (doesn't need to exist)
			mode (str, optional): If merging columns, what column has priority. Defaults to "Source priority".
			preserve_source (bool, optional): Whether to preserve the source-column. Defaults to False.
			astype (str | None, optional): Enforce a certain type. Defaults to None.
		"""
		if self._df is None:
			raise ValueError("No dataframe loaded, cannot merge columns.")

		if astype == "Destination":
			target_type = None #By default we merge into existing column that already has this type
		elif astype == "Source":
			target_type = None
			if src_column in self._df.columns:
				target_type = self._df[src_column].dtype
		else:
			raise NotImplementedError(f"Could not merge columns, as type-deduction ({astype}) is not set to source/dest.")




		if src_column == dst_column:
			try:
				if target_type != self._df[dst_column].dtype: #If dtype should be changed
					self._df[dst_column] = self._df[dst_column].astype(target_type) #type: ignore
					return True, f"Changed type of column {src_column} to: {target_type}"
			except Exception as err: #pylint: disable=broad-exception-caught
				log.error(traceback.format_exc(), err)
				return False, str(err)

			return True, "Source and destination the same, continuing"
		try:
			if mode == "Overwrite entirely":
				self._df[dst_column] = self._df[src_column]
			elif dst_column is None or dst_column == "None" or dst_column == "": #If "just" wanting to delete a column
				pass
			else:
				if dst_column not in self._df.columns: #Create empty column if it does not yet exist
					self._df[dst_column] = None

				# merged_col = None
				if mode == "Source priority":
					self._df[dst_column] = self._df[src_column].fillna(self._df[dst_column])
				elif mode == "Destination priority":
					self._df[dst_column] = self._df[dst_column].fillna(self._df[src_column])
				else:
					raise NotImplementedError(f"Could not merge columns, as merging mode {mode} is not implemented")

			if not preserve_source:
				self._df.drop(src_column, axis=1, inplace=True) #Remove src column if so desired
				self.dfChanged.emit() #TODO: change this to columnschanged? Not everything needs to be updates
				# if src_column in self.plot_settings.plotted_labels_list:
				# 	self.plot_settings.plotted_labels_list.remove(src_column) #Remove src column from plotlist if it is there

			if target_type: #If enforced datatype is specified
				self._df[dst_column] = self._df[dst_column].astype(target_type)#, errors='coerce')

		except Exception as err: #pylint: disable=broad-exception-caught
			log.error(traceback.format_exc(), err)
			return False, str(err)

		self.dfChanged.emit()
		return True, f"Merged columns {src_column} into {dst_column} succesfully (using {mode}-mode)"




	def validate_df(self, new_df : pd.DataFrame | None, inplace_try_fix : bool = True):
		"""validates a df (to see if it is loadable) and can also try to fix it

		Args:
			new_df (pd.DataFrame): The new df to be validated/fixed
			inplace_try_fix (bool, optional): Whether in-place fixes should be tried. Defaults to True
		Returns:
			bool: Whether the resulting dataframe is valid (after attempted fixes if enabled)
		"""
		if new_df is None:
			return False

		try:

			log.debug("Now attempting to validate/fix pandas dataframe")
			#Unfixable errors:
			assert isinstance(new_df, pd.DataFrame) #Assert the loaded file
			if inplace_try_fix:
				log.debug("Inplace_try_fix enabled in validate_df, but not implemented yet...")
			# assert(self._dt_col in new_df.columns), "A datetime column should be present (TODO: make optional)"
		except Exception as err: #pylint: disable=broad-exception-caught
			log.error(f"Could not validate/fix dataframe : {err}")
			return False

		return True


	def load_from_file(self, file_source : str):
		"""Overwrites all existing loaded data and attempts to load from specified file, if succesful, new file path is
		also set

		Raises:
			Exception: General exception if compatibility error occurs (validate_df fails)
		Returbn

		"""
		log.info(f"Reloading current database from file: {file_source}")
		if file_source: #if path has been specified
			success, msg, new_df = DfUtility.load_dataframe_using_file_extension(file_source=file_source)
			# new_df = pd.read_pickle(file_source)

			if not success:
				raise ValueError(msg)
			elif not self.validate_df(new_df, inplace_try_fix=True) or new_df is None:
				raise ValueError("Dataframe compatibility error - returning...")

			self._df = new_df

			log.info(f"Succesfully (re)loaded database from file - df size: {len(new_df)}, columns: {new_df.columns}")
			self._df_selection = set([]) #Reset selection
			self._file_source = file_source
			self.fileSourceChanged.emit(self.file_source)
			# self.df_selection = np.array([i for i in range(int(len(new_df) * 0.5))])
			# self._df.set_index(self._dt_col) #Added 20220424 --> set datetime as index

			#TODO: safe to add this assertionerror here?
		# except (AttributeError, ImportError, ModuleNotFoundError, TypeError, FileNotFoundError, AssertionError) as err:


			# self.update_config_using_df()
		else:
			log.info("File not specified... keeping original dataframe")
			return
		self.dfChanged.emit()

	# def append_existing_df(self, append_df : pd.DataFrame):

	def apply_python_code(self, code : str, force_update_afterwards : bool = True):
		"""Executes the passed code using Exec (note: this function is not very safe).
			Makes it possible to create/execute dataset processing techniques on-the-fly

		Args:
			code (str): The code to be executed using exec.
			force_update_afterwards (bool, optional): Whether to force an update of the dataframe after executing the
				code. Defaults to True.
		"""
		log.info(f"Now trying to execute python code of (char)length: {len(code)}")
		msg = "Success!"
		try:
			exec(code) #pylint: disable=exec-used
			log.info("Succesfully executed the python code!")
			if force_update_afterwards:
				self.dfChanged.emit()
			return True, msg
		except Exception as err: #pylint: disable=broad-exception-caught
			msg = f"Error while executing: {err}"
			log.warning(msg)
			log.warning(traceback.format_exc())
			return False, msg


	def load_existing_df(self,
			new_df : pd.DataFrame,
			append_mode : bool = False,
			duplicate_overwrite : bool = False,
			resample_seconds : int | None = None #TODO: use datetime.timedelta instead?
		):
		"""Loads an existing DF

		Args:
			new_df (pd.DataFrame): The new Pandas Dataframe
			append_mode (bool, optional): Whether the new dataframe should be appended to the existing dataframe.
				Defaults to False.
			duplicate_overwrite (bool, optional): Whether duplicate column values should be overwritten with new
				dataframe, default behaviour keeps the original (Or first Not-None value)
			resample_seconds (int | None, optional): Whether to resample the dataframe to a certain frequency. Defaults
				to None (no resampling).
		"""
		if append_mode and self._df is not None: #If append mode and we currently have a dataframe loaded
			merged_df = None
			if duplicate_overwrite:
				merged_df = pd.concat([self._df, new_df])
			else:
				merged_df = pd.concat([new_df, self._df])

			if resample_seconds is not None:
				merged_df = merged_df.groupby([pd.Grouper(freq='1S', key=self._dt_col)]).last() #Group every 1 seconds together
			merged_df = merged_df.sort_values(by=self._dt_col)[::-1]
			merged_df.reset_index(inplace=True)

			merged_df.dropna(
				axis=0, subset=merged_df.columns.difference([self._dt_col]), how="all", inplace=True
			) #Drop columns that are completely empty
			self._df = merged_df
		else:
			self._df = new_df #Copy?
		self.dfChanged.emit() #Broadcast
