import subprocess, os, platform, pathlib
import datetime
from datetime import timezone
import numpy as np
import matplotlib
from sklearn import preprocessing
import math
from skimage.measure import block_reduce
import pandas as pd
import logging
log = logging.getLogger(__name__)


def get_full_path(subpath):
	"""Gets full path using the current directory (of this script) + the subpath

	Args:
		subpath (str): subpath in current directory

	Returns:
		str: the full path
	"""
	cur_dir = pathlib.Path(__file__).parent.absolute()
	log.debug("Parent path: "+ str( pathlib.Path(__file__).parent.absolute()))
	return os.path.join(cur_dir, subpath)

def create_path(path : str):
	"""creates path if it does not yet exist 

	Args:
		path (str): the full path to be created if it does not exist
	"""
	if not os.path.exists(path):
		os.makedirs(path)




def datetime_to_iso8601(datetime : datetime.datetime) -> str:
	"""Generates iso8601 string from datetime

	Args:
		datetime (datetime.datetime): datetime of to-be-converted timestamp

	Returns:
		string: string in isoformat (e.g. 2020-10-16T13:53:11.000Z)
	"""

	return datetime.isoformat()#.replace("+00:00", "Z") #Also convert to none/Z-format (otherwise it is not recognised by restful api)


def datetime_to_timestr(datetime : datetime.datetime) -> str        :
	"""Extracts time from datetime format

	Args:
		datetime (datetime.datetime): date/time as datetime.datetime format

	Returns:
		str: the time from the datetime 
	"""
	# return datetime_to_iso8601(datetime).split('T')[1].split('+')[0]
	return datetime_to_iso8601(datetime).split('+')[0]


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



def overwrite_to_file(filename, content):
	"""Simple function that (over)writes passed content to file 

	Args:
		filename (str): name of the file including extension
		content (str): what to write to file
	"""
	f = open(filename, "w")
	f.write(content)
	f.close()



def norm_plot(df : pd.DataFrame, ax : matplotlib.axes.Axes, x_axis : str="DateTime" , dont_norm : list=["Date", "Time", "DateTime", "Classification", "Prediction"], column_name_dict : dict = {}, plot_kwarg : dict = {}):
	"""Plot normalized dataframe entries 

	Args:
		df (pd.DataFrame): the dataframe to be plotted
		ax (matplotlib.axes.Axes): on what axes it should be plotted
		x_axis (str, optional): What column to use as x-axis. Defaults to "DateTime".
		dont_norm (list, optional): list of string, column names that shall not be normalized. Defaults to ["Date", "Time", "DateTime", "Classification", "Prediction"].
		column_name_dict (dict, optional): column-renaming dict for plotting purposes, e.g. {"DateTime": "Date"} would rename DateTime column to "Date" in plot. Defaults to {}.
		plot_kwarg (dict, optional): kwargs for pd.dataframe.plot (e.g. s=10 for larger dots etc.). Defaults to {}.
	"""

	df_norm = df.copy()
	for col in df.columns: #go over columns, normalize them 
		if col in dont_norm:
			continue #don't normalize columns which will not be used 
		df_norm[[col]] = preprocessing.MinMaxScaler().fit_transform(df_norm[[col]]) #TODO: -1 to 1 or 0 to 1? 
	
	df_norm = df_norm.interpolate(method='linear') #Interpolate between missing values
	df_columns = [ column_name_dict[col_name] if col_name in column_name_dict.keys() else col_name for col_name in df_norm.columns]

	df_columns.remove("DateTime")

	df_norm.plot(figsize=(20,10), x=x_axis, ax=ax, **plot_kwarg)
	ax.legend(df_columns, loc="upper center", bbox_to_anchor=(0.5, 1.1), ncol = len(df_columns))


def norm_plot_pandas_as_numpy(df : pd.DataFrame, ax : matplotlib.axes.Axes, x_axis="DateTime", dont_norm=["Date", "Time", "DateTime", "Classification", "Prediction"], column_name_dict = {}, plot_kwarg = {}):
	"""Analoguous to norm_plot(), This function was created because some errors seem to exists when using pandas.plot together with plt.plot when sharex=True (for DateTimes),
	this issue does not seem to appear when columns are plotted separately by first converting to numpy

	Args:
		df (pd.Dataframe): Data dataframe
		ax (plt.ax): axis to plot on
		x_axis (str, optional): name of x-axis column. Defaults to "DateTime".
		dont_norm (arr, optional): array of columns that dont need to be normalized. Defaults to ["Date", "Time", "DateTime", "Classification", "Prediction"].
		column_name_dict (dict, optional): translation dictionary to edit names. Defaults to {}.
		plot_kwarg (dict, optional): kwargs for plotting purposes (e.g. {"marker":"o"} etc.). Defaults to {}.
	"""
	for col in df.columns: #go over columns, normalize them TODO: what about time? class? 
		if col in dont_norm: #TODO: depth is normalized, is this okay? 
			continue #don't normalize columns which will not be used 
		temp = df[[col]]
		col_norm = preprocessing.MinMaxScaler().fit_transform(df[[col]]) #TODO: -1 to 1 or 0 to 1?
		if col != x_axis:

			nan_mask = np.isfinite(col_norm)
			X = df[[x_axis]].to_numpy()[nan_mask] #Remove nan entries #TODO: what if date is none? 
			Y = col_norm[nan_mask]
			ax.plot(X,Y, label=col, **plot_kwarg)
	
	ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.1), ncol = len(df.columns))





def get_first_occurence(arr : np.array, elem):
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

import typing
import numbers
import matplotlib
import matplotlib.figure

import time
import matplotlib.dates
def find_nearest_idx_sorted(array,value):
	"""Source: https://stackoverflow.com/questions/2566412/find-nearest-value-in-numpy-array
	"""
	idx = np.searchsorted(array, value, side="left")
	if idx > 0 and (idx == len(array) or math.fabs(value - array[idx-1]) < math.fabs(value - array[idx])):
		return idx-1
	else:
		return idx


def plot_colorbars(df : pd.DataFrame, label_columns : typing.List[str], ax_list : typing.List[any], canvas : matplotlib.figure.Figure, datetime_column : str = "", preferred_sorting : typing.List[str] = []):
	"""Function used for plotting colorbar, indicating classification at each time


	Args:

		df (pd.DataFrame): The dataframe to be plotted
		label_columns (typing.List[str]): The columns to be plotted
		ax_list (typing.List[any]): The axes to be plotted on (same length as label_columns)
		canvas (matplotlib.figure.Figure): The canvas to be plotted on
		datetime_column (str, optional): The column to be used as datetime. Defaults to "" which sets it to the current index.
		preferred_sorting (typing.List[str], optional): The preferred sorting of the labels (first sorts by this order, then alphabetical). Defaults to [] which sorts all in order of occurence.
	"""

	# log.debug(f"Label columns: {label_columns}")

	if len(label_columns) == 0:
		return

	all_classes = set({})
	# dt_lbl_df = self.data_model.df[[datetime_column, *label_columns]].sort_values(datetime_column, ascending=True).fillna("None") 

	if len(datetime_column):
		dt_lbl_df = df[[datetime_column, *label_columns]].sort_values(datetime_column, ascending=True)  #Changed 20220520 due to time issues when operating on whole dataframe each time
	else:
		dt_lbl_df = df[label_columns].sort_index(ascending=True)

	dt_lbl_df.fillna(np.nan) #To make sure <nans> are processed properly
	# dt_lbl_df.fillna(value=0)
	if len(dt_lbl_df) == 0:
		log.info("Not plotting colorbar as length of dataframe is 0")
		return

	for col in label_columns:
		all_classes.update(list(dt_lbl_df[col].unique())) #Use this for only classes in current view
	all_classes = [i for i in all_classes if i is not None and not pd.isna(i) and(not isinstance(i, numbers.Number) or not np.isnan(i)) and i != "nan"] #All classes except NaN (numpy), <NA> (pandas) (make sure to check for <NA> first as otherwise error is trhowns)
	

	all_classes = set([i for i in all_classes if i != "None"])
	log.debug(f"Found classes: {all_classes}")
	colors = matplotlib.cm.rainbow(np.linspace(0,1,len(all_classes))) #get new color for each class
	
	#====== Manually add "None" string ==============
	all_classes = ["None"] + list(all_classes) 
	colors = np.insert(colors, 0, np.array((0.5, 0.5, 0.5, 0.3)), axis=0) 

	all_classes_dict = { item : nr for (nr,item) in enumerate(all_classes)}
	all_classes = np.array(list(all_classes)) #Set back to numpy for indexing options #20221021 moved this after creation all_classes dict -> otherwise they become strings
	color_map = matplotlib.colors.ListedColormap(colors)
	log.debug(f"Label columns: {label_columns}")
	axes = ax_list
	annot=None

	for ax, label_col in zip(axes, label_columns): #Go over label columns
		log.debug(f"Now plotting colorbar for column '{label_col}'")
		
		if len(datetime_column):
			dt_lbl_original = dt_lbl_df[[datetime_column, label_col]].copy() #.to_numpy() #Should already be sorted descending, as such this should be more efficient TODO: make sure this stays this way - als: na_value can be used instead of fillna earlier			
		else:
			dt_lbl_original = dt_lbl_df[[label_col]].copy()

		dt_lbl = dt_lbl_original.copy()
		dt_lbl[label_col] = dt_lbl[label_col].astype("object").replace(to_replace=all_classes_dict).astype("Int64") #Replace all entries by a number indicating its class (Use Object because this will fit every datatype), (or None/NaN), then it should all be Integers (Int64 instead of in64 due to Nones)
		mask = ~(dt_lbl[label_col].isnull() & dt_lbl[label_col].shift(1).isnull()) #Remove repeating Nones
		mask = mask & ((dt_lbl[label_col].shift(1) != dt_lbl[label_col]).fillna(value=True))# | (dt_lbl[label_col].shift(1).isnull() & ~(dt_lbl[label_col].isnull())) )  #Remove repeating others #ADDED 20221021 replace NaN entries in mask by True -> for Int64 (capital i -> with NaN), it seems 3!=NaN results in NaN
		mask.iloc[0] = True #Always take first
		mask.iloc[-1] = True #And always take last
		dt_lbl = dt_lbl.loc[mask] #Shift by 1 and compare with itself -> repeating values will be deleted and only first one remains
		dt_lbl = dt_lbl.fillna(value=0)
		#TODO: commented following line: 
		# dt_lbl[label_col] = dt_lbl[label_col].astype(np.int64) #No nones should remain -> this should succeed. NOTE: pd.Int64Dtype() created errors, even when first converting to numpy, this makes sure everything works before plotting

		X, Y, Z = [], [], []
		log.debug(f"Unique values in label column {label_col} : {dt_lbl[label_col].unique()}")
		if len(datetime_column):
			X = dt_lbl[datetime_column].to_numpy()
		else:
			X = dt_lbl.index.to_numpy()
		Z = dt_lbl[label_col].astype("int64").to_numpy() #Added 20221021 -> every class (including None =0 )should be an integer now -> make sure interpreted as such

		pc = ax.pcolormesh(X, [0,1], [np.array(Z)[:-1]], cmap=color_map, vmin=0, vmax=len(all_classes)) # cmap=cMap) #TODO: make sure this is right
		# pc = ax.pcolormesh(X, [0, 1], [np.array(Z), np.array(Z)], cmap=color_map, vmin=0, vmax=len(all_classes))# 2022-07-13: changed to stacked Np.Array(Z) due to problems on some other PC's (otherwise (X,Y).shape != Z.shape )  2022-01-05: changed back to above bc python3.10 did not work otherwise
		ax.set(yticklabels=[])
		ax.set_ylabel(label_col, rotation=0, ha='right', va='center')


		# ======== Annotation on hover ===============
		annot = ax.annotate("", xy=(0,0), xytext=(0,0 ),textcoords="offset points", ha='center', va='center',
					bbox=dict(boxstyle="round", fc="w"))

		
		
					#arrowprops=dict(arrowstyle="->"))
		#Show dt_lbl string when hovering over pcolumesh:
		def update_annot(x, y, newtext, annot):
			annot.set_visible(True)
			annot.xy = (x,y)
			annot.set_text(newtext)
			annot.get_bbox_patch().set_alpha(1)
			canvas.draw_idle()

		def on_axis_leave(event, annot):
			#check if annotation is visible (otherwise lag when moving away from plot)
			if annot.get_visible():
				annot.set_visible(False)
				canvas.draw_idle()
		
		def format_coord(x, y, original_labels : np.ndarray, original_dts : np.ndarray):
			# time_before = time.perf_counter()
			dt = matplotlib.dates.num2date(x).replace(tzinfo=None)
			dt = np.datetime64(dt)

			nearest = find_nearest_idx_sorted(original_dts, dt)
			# log.info(f"find_nearest_idx_sorted took {time.perf_counter() - time_before} s")

			label = original_labels[nearest]

			# update_annot(x, y, label) #TODO: this takes some time so updating label text takes some ms -> make this faster? 
			return f"x={dt} 		class={label}"
			
			# return f"x={dt} 		class={ dt_lbl_original[label_col][dt_lbl_original['DateTime'].sub(dt).abs().idxmin()]}"

		def on_axis_hover(event, ax, original_labels : np.ndarray, original_dts : np.ndarray, annot): #NOTE: merged this function with format_coord -> might not be necceasary anymore
			if event.inaxes == ax:
				x, y = event.xdata, 0.5
				dt = matplotlib.dates.num2date(x).replace(tzinfo=None)
				dt = np.datetime64(dt)
				# label = original_labels[original_dts.sub(dt).abs().idxmin()]


				nearest = find_nearest_idx_sorted(original_dts, dt)
				# print(f"Nearest: {nearest}")
				label = original_labels[nearest]

				#Show label in pyqt hint box:

			
				# update_annot(x, y, label, annot)
			# else:
			# 	on_axis_leave(event, annot)
			


		if len(datetime_column):
			dt_col_vals = dt_lbl_original['DateTime'].to_numpy()
		else:
			dt_col_vals = dt_lbl_original.index.to_numpy()

		# canvas.mpl_connect("motion_notify_event", lambda x, ax=ax, original_labels=dt_lbl_original[label_col].to_numpy(), original_dts=dt_col_vals, annot=annot: on_axis_hover(x, ax, original_labels, original_dts, annot))
		# canvas.mpl_connect("axes_leave_event", lambda x, annot=annot: on_axis_leave(x, annot))
		ax.format_coord = lambda x,y, original_labels=dt_lbl_original[label_col], original_dts=dt_col_vals: format_coord(x,y, original_labels=original_labels, original_dts=original_dts )
	
	
	legend_names = all_classes
	legend_colors = np.array([ matplotlib.lines.Line2D([0], [0], color=color, lw=4) for color in colors ])
	# log.debug(f"Creating colorplot legend using {legend_names} and {legend_colors}")

	if preferred_sorting and len(preferred_sorting) > 0:
		labels_alphabetical = sorted(legend_names, key=lambda x: x.lower())
		#First sort by preferred sorting, then by alphabetical order
		sort_idx = np.argsort([preferred_sorting.index(label) if label in preferred_sorting else 100+labels_alphabetical.index(label) for label in legend_names])
		legend_colors = [legend_colors[i] for i in sort_idx]
		legend_names = [legend_names[i] for i in sort_idx]


	# ax.legend(legend_colors, legend_names, loc='upper center', bbox_to_anchor=(0.5, 1.39), ncol = len(all_classes))
	axes[-1].legend(legend_colors, legend_names, loc='upper center', bbox_to_anchor=(0.5, -0.5), ncol = min(10, len(legend_names)), frameon = False)

	
		
		

def plot_fft(df : pd.DataFrame, ax : matplotlib.axes.Axes, fft_column : str="None", y_res_reduction : int=5, pcolormesh_kwargs : dict= {}):
	"""Plots fft graph (with Rf = [0, 1]) over time, using passed dataframe

	Args:
		df (pd.DataFrame): Dataframe with at least a DateTime column and fft column with each entry [a1, a2, ..., an] where each entry denotes the activity for each bin #TODO: add frequency range
		ax (matplotlib.axes.Axes): Ax to plot on
		fft_column (str, optional): What column contains the fft activity entries. Defaults to "None".
		y_res_reduction (int, optional): [description]. Defaults to 5.
		pcolormesh_kwargs (dict, optional): [description]. Defaults to {}.
	"""
	fft_df = df[["DateTime", fft_column]].sort_values("DateTime", ascending=True).dropna()


	X, Y, Z = [], [], []
	
	X = fft_df["DateTime"].to_numpy()
	Y = [i/ (1601.0//y_res_reduction) for i in range(1601//y_res_reduction + 1)] #TODO: Don't hardcode 1601, change based on amount of lines
	Z = np.array(fft_df[fft_column].tolist()) #DO this this way, as fft_df[fft_column] creates an array of lists
	Z = np.swapaxes(Z, 0, 1)
	Z = block_reduce(Z, block_size=(y_res_reduction,1), func=np.mean) #reduce y-resolution by a factor 10
	print(f"Max is : {np.max(Z)}")
	Z = (Z / Z.mean() * 2)

	# ax.imshow(Z, cmap=cm.viridis, vmax=1)#, cmap=cMap) #TODO: imshow can be much more efficient, but only for consistent datetime-steps (since pixel width are constant)?, large gaps in datetime would create massive images 
	ax.pcolormesh(X, Y, Z, vmax=1, **pcolormesh_kwargs)#, cmap=cMap) 
	# ax.scatter(X,Y) #For debuggin purposes



if __name__ == "__main__":
	print("Running utility test")
	assert iso8601_get_max_date("2013-01-25T19:20:41.391394", "2013-02-25T19:20:41.391394") == "2013-02-25T19:20:41.391394"
	assert iso8601_get_max_date("2013-01-25T19:20:41.391394", "2013-01-25T19:20:41.391394") == "2013-01-25T19:20:41.391394"
	assert iso8601_get_max_date("2013-01-25T19:20:42.391394", "2013-01-25T19:20:41.391394") == "2013-01-25T19:20:42.391394"
	print(datetime_to_iso8601(datetime.datetime.utcnow().replace(tzinfo=timezone.utc)))
	print("Done, no errors")