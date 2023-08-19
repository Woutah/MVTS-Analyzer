


import datetime
import logging
import math
import numbers
import time
import traceback
from cmath import nan

import keyboard
import matplotlib
import matplotlib.axes
import matplotlib.axis
import matplotlib.backend_bases
import matplotlib.collections
import matplotlib.colors
import matplotlib.dates
import matplotlib.dates as dates
import matplotlib.gridspec
import matplotlib.patches
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms
import numpy as np
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import \
    NavigationToolbar2QT as NavigationToolbar
from PySide6 import QtWidgets
from skimage.measure import block_reduce

from mvts_analyzer.graphing.graph_data import GraphData, OperationType
from mvts_analyzer.graphing.graph_settings_model import GraphSettingsModel
from mvts_analyzer.graphing.plotter.collection_selector import \
    CollectionSelector
from mvts_analyzer.res.Paths import Paths
from mvts_analyzer.utility.GuiUtility import create_qt_warningbox

log = logging.getLogger(__name__)


class DragDetector():
	"""
	Manages the dragging of a rectangle, self.drag_start and self.drag_end correspond to the ax coordinates
	of the first/last click of the drag
	"""
	def __init__(self,
			canvas : matplotlib.backend_bases.FigureCanvasBase,
			ax : matplotlib.axes.Axes, #pylint: disable=invalid-name
			rect : matplotlib.patches.Rectangle,
			toolbar : NavigationToolbar
		):

		self.ax = ax
		self.connect(canvas)
		self.canvas = canvas
		self.rect = rect
		self.dragging = False
		self.drag_start = None
		self.drag_end = None
		self.toolbar = toolbar


	def connect(self, canvas):
		"""Connect a new canvas to the drag detector so that we can detect drags/releases/movements on this canvas"""
		canvas.mpl_connect('button_release_event', self.on_release)
		canvas.mpl_connect('button_press_event', self.on_press)
		canvas.mpl_connect('motion_notify_event', self.on_motion)


	def on_press(self, event):
		"""On detection of key-press"""
		coords = (event.x, event.y)
		if not self.rect.contains_point(coords):
			return

		self.dragging = True
		log.debug(f"In axis: {self.ax.in_axes(event)}")

		#Translates the event to be inside the axis
		# xdata, ydata = self.ax.transData.inverted().transform(coords)
		log.debug(f"Drag start: {coords} => {self.ax.transData.inverted().transform(coords)}")
		self.ax.start_pan(event.x, event.y, event.button)


	def on_motion(self, event):
		"""On mouse movement, if dragging, update drag/pan"""
		if not self.dragging:
			return
		coords = (event.x, event.y)
		self.drag_end = self.ax.transAxes.inverted().transform(coords)
		log.debug(f"Current drag: {coords} => {self.ax.transData.inverted().transform(coords)}")
		# xdata, ydata = self.ax.transData.inverted().transform(coords)
		self.ax.drag_pan(event.button, event.key, event.x, event.y)
		self.canvas.draw_idle()


	def on_release(self, event):
		"""On mouse-button release, stop dragging"""
		if not self.dragging:
			log.debug("was not dragging")
			return
		self.dragging = False
		# coords = (event.x, event.y)
		self.ax.end_pan() #End panning

class MplCanvas(FigureCanvasQTAgg):
	"""
	Wrapper around matplotlib figure-canvas, used to manage axes and twinxes for a stacked plot.
	Makes it easier to add/remove axes and set their respective heights
	"""

	def __init__(self): #, parent=None, width=5, height=4, dpi=100):
		# super(MplCanvas, self).__init__()
		fig, ax = plt.subplots(1)
		super(MplCanvas, self).__init__(fig)
		self.figure = fig
		self.ax_sizes = { "main" : 10}
		self.ax_order = ["main"]
		self.ax_dict : dict[str, matplotlib.axes.Axes] = {"main" : ax }
		self.twinxes = {"main" : {}}
		self.annots = {"main": None}


	def add_axis(self, name, index, relative_height = 1, refresh_after = True):
		"""Adds an axis to the plot, with the given name, index and relative height"""
		self.ax_order.insert(index, name)
		self.ax_sizes[name] = relative_height
		self.twinxes[name] = {}
		self.annots[name] = None
		if refresh_after:
			self._refresh_axes()


	def get_twinx(self, ax_name, twinx_name) -> matplotlib.axes.Axes:
		"""Safe method to retrieve twinx axes, twinx axes are never deleted and can thus be reused

		Args:
			ax_name (str): where to add twinx axis
			twinx_index (int): index of twinx

		Returns:
			matplotlib.axes.Axes: twinx axis of specified axis
		"""
		if twinx_name in self.twinxes[ax_name].keys(): #if axis already exists
			return self.twinxes[ax_name][twinx_name]

		twinx = self.ax_dict[ax_name].twinx()
		twinx.name = ax_name #TODO: check if this works
		self.twinxes[ax_name][twinx_name] = twinx
		return twinx

	def add_axes(self, names, indexes, relative_heights):
		"""TODO make sure they are passed in ascending order (indexes)

		Args:
			names (list[string]): list of names of new axes
			indexes (list[int]): list of indexes of axes, make sure the ordering of this list is ascending as they
				are added iteratively
			relative_heights (list[float]): the relative heights of these axes compared to main (size=10)
		"""
		for (name, index, height) in zip(names, indexes, relative_heights):
			self.add_axis(name, index, height, refresh_after=False)
			# self.ax_order.insert(indexes[i], names[i])

			# # self.ax_sizes.append(relative_heights[i])
			# self.ax_sizes[names[i]] = relative_heights[i]

		log.debug(f"Added axes: {names} with heights : {relative_heights},"
	    	f"this resulted in total list: {self.ax_order}, {self.ax_sizes}")
		# self._refresh_axes()
		self._remake_axes()

	def remove_axis(self, name):
		"""
		Remove a given axis from the plot and clean up.

		Args:
			name (str): name of axis to remove.
		"""
		self.ax_order = [i for i in self.ax_order if i!= name]
		if name in self.ax_sizes:
			del self.ax_sizes[name] #remove
		if name in self.twinxes:
			for twinxname in self.twinxes[name].keys():
				del self.twinxes[name][twinxname]
		if name in self.ax_dict:
			del self.ax_dict[name] #remove
		if name in self.annots:
			del self.annots[name] #Remove annotations
		self.ax_order = [i for i in self.ax_order if i != name]
		self._remake_axes()

	def get_axis(self, name):
		"""Get axis by name"""
		return self.ax_dict[name]


	def open_save_popup(self):
		"""Show popup to save figure to file"""
		try:
			fname = QtWidgets.QFileDialog.getSaveFileName(
						None, #type: ignore
						'Save As...',
						# Paths.FiguresBasePath,
						Paths.FiguresBasePath,
						"""Portable Network Graphics (*.png)
						Joint Photographic Experts Group (*.jpeg, *.jpg)"
						PGF code for LaTeX (*.pgf)
						Portable Document Format (*.pdf)
						Portable Network Graphics (*.png)
						Postscript (*.ps)
						Raw RGBA bitmap (*.raw *.rgba)
						Scalable Vector Graphics (*.svg *svgz)
						Tagged Image File Format (*tif *tiff)"""
					)
			log.debug(f"Trying to save figure as: {fname}")
			self.figure.savefig(fname[0])
		except Exception as err: #pylint: disable=broad-exception-caught
			log.warning(f"Could not save figure - {err}")

	def _remake_axes(self):
		"""
		Remakes axes in the same figure, uses relative sizes to determine the height of each axis
		"""
		sizes = [self.ax_sizes[i] for i in self.ax_order]
		self.figure.clf() #Changed into this to not interfere with other figures
		temp_axes = []
		grid = matplotlib.gridspec.GridSpec(len(sizes), 1, height_ratios=sizes, hspace=0) #Create grid-specification
		# gs.update(wspace=0, hspace=0)
		for i in range(len(sizes)): #Then remake axes
			if i > 0:
				# temp_axes.append(plt.subplot(gs[i], sharex = temp_axes[i-1]))
				new_subplot = self.figure.add_subplot(grid[i], sharex = temp_axes[i-1])
				# new_subplot.title #TODO: do this so we can easily normalize
				temp_axes.append(new_subplot)

			else:
				# temp_axes.append(plt.subplot(gs[i]))
				temp_axes.append(self.figure.add_subplot(grid[i]))

			# temp_axes.append(self.figure.add_subplot(1, i, gridspec))

		for i, name in enumerate(self.ax_order):
			self.ax_dict[name] = temp_axes[i]



		log.debug(f"Axes remade: {self.ax_dict}")


	def clear_all_axes(self): #TODO: this doesnt seem to work?
		"""Clear the figure"""
		log.debug("Now clearing figure...")
		self.figure.clf()

	def remove_twinxes(self):
		"""Remove all twinxes from the plot"""
		for ax_name, ax in self.twinxes.items():
			twinx_names =  list(self.twinxes[ax_name].keys())
			for twinx_name in twinx_names:
				del self.twinxes[ax_name][twinx_name]

	def remove_axes(self, except_main = True):
		"""Remove all axes from the plot, except main (if specified)"""
		for name, ax in self.ax_dict.copy().items():
			if name == "main" and except_main: #Skip main deletion if so desired
				continue
			self.remove_axis(name)
		self.remove_twinxes()
		self._remake_axes()
		log.debug(f"Refreshed axes, this resulted in axes: {self.ax_dict} and twinxes: {self.twinxes}")


class QPlotter(QtWidgets.QWidget):
	"""
	Intermediate between plot datamodel/settingsmodel which manages the plotter using the GraphSettingsModel
	data passed on replot call
	"""
	def __init__(self,
				data_model : GraphData,
				settings_model : GraphSettingsModel,
				*args,
				**kwargs
			):
		super(QPlotter, self).__init__(*args, **kwargs)
		log.debug("Reloading QPlotter")

		self.canvas = MplCanvas()#, width=5, height=4, dpi=100)
		self.toolbar = NavigationToolbar(self.canvas, self)
		layout = QtWidgets.QVBoxLayout()
		layout.addWidget(self.toolbar)
		layout.addWidget(self.canvas)
		self.setLayout(layout)

		self.settings_model = settings_model
		self.data_model = data_model

		self.model = None
		self.selected_data = None #The intermediate dataframe used to plot the main data
		self.selection_exclusion_brightness = 0.75 #The brightness factor for the points not selected
		self.plot_title = "-"
		self.fft_data = (None, None, None)

		self.cur_pd_selection = set([])
		self.selectors = []
		self.selector = CollectionSelector(self.canvas.get_axis("main"), [], [],[])

		self.selector.pdSelectionEdited.connect(self.handle_selection_change)
		self.data_model.dfSelectionChanged.connect(self._set_selection)

		self._colorbar_legend = None
		# self.selector.pandasSelectionEdited.connect(lambda x: self.set_cur_loc_selection(x, redraw_after=True))

	def handle_selection_change(self, new_selection : set):
		mode = OperationType.OVERWRITE
		try:  # used try so that if user pressed other than the given key error will not be shown
			if keyboard.is_pressed('ctrl') or keyboard.is_pressed('shift'):  # if key 'q' is pressed
				mode = OperationType.APPEND
			elif keyboard.is_pressed('alt'):
				mode = OperationType.COMPLEMENT
		except Exception: #pylint: disable=broad-exception-caught
			pass
		self.data_model.set_df_selection(new_selection, mode, fill_gaps_ms=self.settings_model.selection_gap_fill_ms)


	@staticmethod
	def x_axis_reformatter(val):
		if isinstance(val, datetime.datetime):
			val = val.strftime("%Y-%m-%d %H:%M:%S") #up until seconds precision
		else:
			val = str(val)

		return val

	def replot(self,):
		log.debug("Now trying to replot...")
		try:
			self._replot()
		except Exception as err:
			log.error(traceback.format_exc(), err)
			# msg = QtWidgets.QMessageBox()
			# msg.setIcon(QtWidgets.QMessageBox.Icon.Warning)
			# msg.setText(f"{err}")
			# msg.setWindowTitle("Exception")
			# # msg.setDetailedText("The details are as follows:")
			# # msg.setInformativeText("This is additional information")
			# msg.exec_()
			create_qt_warningbox(err, "Exception during replot: {err}")

	def _replot_fft(self):
		if self.fft_data is None or self.fft_data[0] is None:
			log.info("FFT data is none, could not replot")
			return
		log.debug(f"Chose for fft_color {self.settings_model.fft_color_map}")
		if self.settings_model.fft_color_map == "BlueYellowRed":

			colordict = [
				(0, "Blue"),
				(0.9999, "Yellow"),
				(1.0, "Red")
			]
			fft_cmap = matplotlib.colors.LinearSegmentedColormap.from_list("custom", colordict, N=256)

		else:
			fft_cmap = plt.get_cmap(self.settings_model.fft_color_map)



		fft_cmap = fft_cmap(np.arange(fft_cmap.N))
		fft_cmap[:, -1] = self.settings_model._fft_transparency
		fft_cmap = matplotlib.colors.ListedColormap(fft_cmap)

		X, Y, Z = self.fft_data
		log.debug(f"Creating mesh of dimensions: {len(X)}")
		mesh = self.canvas.get_axis("main").pcolormesh(X, Y, Z, vmax=1.0, cmap=fft_cmap, linewidth=0, rasterized=True)#, cmap=cMap)
		mesh.set_edgecolor('face')


		#======= y -axis on left side =====
		self.canvas.get_axis("main").yaxis.set_visible(False)
		log.debug("Now creating left axis")
		cur_ax = self.canvas.get_twinx("main", "AAFFT") #Get

		# cur_ax.set_zorder(self.canvas.get_axis("main").get_zorder()-2)
		# cur_ax.set_zorder(-10)
		# cur_ax.patch.set_visible(False)

		#TODO TODO high importance : make 1000 variable as well -> _fft_line_range max should also be private so make a get method?
		cur_ax.set_ylim(1000 * self.settings_model.fft_line_range_left/self.settings_model._fft_line_range.max_val, 1000 * self.settings_model.fft_line_range_right/self.settings_model._fft_line_range.max_val)
		cur_ax.spines['left'].set_position(("axes", -0.0 ))
		cur_ax.yaxis.tick_left()
		cur_ax.yaxis.set_label_position('left')
		cur_ax.spines['left'].set_visible(True)

		cur_ax.tick_params(axis='y', labelrotation=90)
		cur_ax.set_ylabel("Frequency (Hz)")
		# cur_ax.spines['left'].set_position(('outward', 0))

	def _reload_fft_data(self):
		log.info("Now reloading FFT data")


		# cur_ax.spines['left'].set_visible(True)

		if self.settings_model.fft_column == "":
			log.info("Selected FFT column is empty, not plotting")
			return

		plot_xlim = self.settings_model.plot_domain_limrange
		cols = ["DateTime", self.settings_model.fft_column]
		fft_df = self.data_model._df[cols]
		fft_df = fft_df.sort_values("DateTime", ascending=True).dropna() #TODO: make this more elegant


		if plot_xlim.left_val is not None: #if xmin specified
			fft_df = fft_df[ fft_df["DateTime"] >= plot_xlim.left_val]
		if plot_xlim.right_val is not None:  #If xmax specified
			fft_df = fft_df[ fft_df["DateTime"] <= plot_xlim.right_val]

		if fft_df.empty:
			log.info("Could not create fft_data, as the fft dataframe of selection is empty")
			self.fft_data=(None, None, None)
			return


		y_len = self.settings_model.fft_line_range_right - self.settings_model.fft_line_range_left
		y_res_reduction = int(51 - 50*math.pow(self.settings_model.fft_quality, 1/5))
		X, Y, Z = [], [], []
		X = fft_df["DateTime"].to_numpy()
		Y = np.array([i/ math.ceil(y_len/y_res_reduction) for i in range(math.ceil(y_len/y_res_reduction))]) #TODO: Don't hardcode 1601, change based on amount of lines
		# print(fft_df[self.settings_model.fft_column].tolist())
		Z = np.array(fft_df[self.settings_model.fft_column].tolist())[:, self.settings_model.fft_line_range_left : self.settings_model.fft_line_range_right] #DO this this way, as fft_df[self.

		# fft_column] creates an array of lists
		Z = np.swapaxes(Z, 0, 1)

		if y_res_reduction > 1:
			Z = block_reduce(Z, block_size=(y_res_reduction,1), func=np.mean) #reduce y-resolution by a factor 10
		log.debug(f"FFT max is : {np.max(Z)}")
		log.debug(f"Reduction factor: {y_res_reduction}  --- Z size is: {Z.shape}   Y shape is: {Y.shape}")

		Z = (Z / Z.mean() * pow(self.settings_model.fft_brightness * 2, 5))
		self.fft_data = (X, Y, Z)


	# def _handle_matplotlib_movement(self, event):
	# 	cur_ax = event.inaxes

		# for name, ax in self.canvas.ax_dict.items():
		# 	if ax == cur_ax: #If ax is found
		# 		if name != "main":
		# 			log.debug(f"Event in ax {name} -> {event.xdata}")
		# 			try:
		# 				if self.canvas.annots[name] is None:
		# 					log.debug(f"No annots for {name}")
		# 					self.canvas.annots[name] = ax.annotate("Kaas", xy=(event.xdata, event.ydata), xytext=(0,5), textcoords="offset points")
		# 					log.debug(f"Annots are now: {self.canvas.annots[name]}")
		# 				else:
		# 					self.canvas.annots[name].set_text("Kaas")
		# 			except Exception as ex:
		# 				log.warning(f"Could not annotate axis {name} due to: {type(ex)}={ex}")

		# 			annot = ax.annotate("Kaas", xy=(event.xdata, event.ydata), xytext=(0,5), textcoords="offset points")
		# 			annot.set_visible(True)


	def _replot_colorbars(self):
		"""Function used for plotting colorbar, indicating the class for each time-period

		Args:
			df (pd.DataFrame): Pandas dataframe containing at least a "DateTime" column and a column indicating a class
			color_column (str, optional): The color-class column, each unique entry in this column will be plotted as a separate color. Defaults to "Prediction".
			legend_name_dict (dict, optional): Dictionary with translations for each class for the legend, e.g.:
				if two unique classes exists: [0, 1], and legend name dict={0: "Class1", 1: "Class2"}, then legend names will be
				"Class1" and "Class2" instead of 1&2.
			Defaults to {}.
		"""
		before= time.perf_counter()
		label_columns = self.settings_model.plotted_labels_list #Get list of plotted label-columns
		log.debug(f"Label columns: {label_columns}")

		if len(label_columns) == 0:
			return

		all_classes = set({})
		# dt_lbl_df = self.data_model.df[["DateTime", *label_columns]].sort_values("DateTime", ascending=True).fillna("None")
		before1= time.perf_counter()
		dt_lbl_df = self.selected_data[["DateTime", *label_columns]].sort_values("DateTime", ascending=True)  #Changed 20220520 due to time issues when operating on whole dataframe each time
		dt_lbl_df.fillna(np.nan) #To make sure <nans> are processed properly
		# dt_lbl_df.fillna(value=0)
		if len(dt_lbl_df) == 0:
			log.info("Not plotting colorbar as length of dataframe is 0")
			return

		log.debug(f"Sorting and replacing None took: {time.perf_counter() - before1}")

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


		# self.canvas.add_axes(label_columns, [i+1 for i in range(len(label_columns))], [0.5 / len(label_columns) for i in range(len(label_columns))])
		self.canvas.add_axes(label_columns, [i+1 for i in range(len(label_columns))], [0.3 for i in range(len(label_columns))])

		color_map = matplotlib.colors.ListedColormap(colors)


		log.debug(f"Label columns: {label_columns}")

		axes = [self.canvas.get_axis(label_col) for label_col in label_columns]

		annot=None

		for ax, label_col in zip(axes, label_columns): #Go over label columns
			log.debug(f"Now plotting colorbar for column '{label_col}'")
			before1= time.perf_counter()
			dt_lbl_original = dt_lbl_df[["DateTime", label_col]].copy() #.to_numpy() #Should already be sorted descending, as such this should be more efficient TODO: make sure this stays this way - als: na_value can be used instead of fillna earlier
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


			X = dt_lbl["DateTime"].to_numpy()
			Z = dt_lbl[label_col].astype("int64").to_numpy() #Added 20221021 -> every class (including None =0 )should be an integer now -> make sure interpreted as such
			log.debug(f"Calculating least squares pcolormesh for {label_col} took : {time.perf_counter() - before1}")

			before1 = time.perf_counter()

			pc = ax.pcolormesh(X, [0,1], [np.array(Z)[:-1]], cmap=color_map, vmin=0, vmax=len(all_classes)) # cmap=cMap) #TODO: make sure this is right
			# pc = ax.pcolormesh(X, [0, 1], [np.array(Z), np.array(Z)], cmap=color_map, vmin=0, vmax=len(all_classes))# 2022-07-13: changed to stacked Np.Array(Z) due to problems on some other PC's (otherwise (X,Y).shape != Z.shape )  2022-01-05: changed back to above bc python3.10 did not work otherwise
			log.debug(f"Creating pcolormesh of size {len(X)} took: {time.perf_counter() - before1}s")
			ax.set(yticklabels=[])
			ax.set_ylabel(label_col, rotation=0, fontsize=self.settings_model.font_size, ha='right', va='center')


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
				self.canvas.draw_idle()

			def on_axis_leave(event, annot):
				#check if annotation is visible (otherwise lag when moving away from plot)
				if annot.get_visible():
					annot.set_visible(False)
					self.canvas.draw_idle()

			def format_coord(x, y, original_labels, original_dts):
				dt = matplotlib.dates.num2date(x).replace(tzinfo=None)
				label = original_labels[original_dts.sub(dt).abs().idxmin()]

				# update_annot(x, y, label) #TODO: this takes some time so updating label text takes some ms -> make this faster?
				return f"x={dt} 		class={label}"

				# return f"x={dt} 		class={ dt_lbl_original[label_col][dt_lbl_original['DateTime'].sub(dt).abs().idxmin()]}"

			def on_axis_hover(event, ax, original_labels, original_dts, annot): #NOTE: merged this function with format_coord -> might not be necceasary anymore
				if event.inaxes == ax:
					x, y = event.xdata, 0.5
					dt = matplotlib.dates.num2date(x).replace(tzinfo=None)
					label = original_labels[original_dts.sub(dt).abs().idxmin()]
					update_annot(x, y, label, annot)
				# else:
				# 	on_axis_leave(event, annot)

			#NOTE: turn on to get labeling... But takes some time when moving over plot
			# self.canvas.mpl_connect("motion_notify_event", lambda x, ax=ax, original_labels=dt_lbl_original[label_col], original_dts=dt_lbl_original['DateTime'], annot=annot: on_axis_hover(x, ax, original_labels, original_dts, annot))
			# self.canvas.mpl_connect("axes_leave_event", lambda x, annot=annot: on_axis_leave(x, annot))
			ax.format_coord = lambda x,y, original_labels=dt_lbl_original[label_col], original_dts=dt_lbl_original['DateTime']: format_coord(x,y, original_labels=original_labels, original_dts=original_dts )

			# annot = ax.annotate("", xy=(0,0), xytext=(20,20),textcoords="offset points",
			#         bbox=dict(boxstyle="round", fc="w"),
			#         arrowprops=dict(arrowstyle="->"))
			# ax.





		log.debug(f"REPLOT COLORBARS (Total time): {time.perf_counter() - before}")

		legend_names = all_classes
		legend_colors = np.array([ matplotlib.lines.Line2D([0], [0], color=color, lw=4) for color in colors ])
		log.debug(f"Creating colorplot legend using {legend_names} and {legend_colors}")

		#Sort legend names based on their name
		sort_index = np.argsort(legend_names)
		legend_names = np.array(legend_names)[sort_index]
		legend_colors = legend_colors[sort_index]

		# ax.legend(legend_colors, legend_names, loc='upper center', bbox_to_anchor=(0.5, 1.39), ncol = len(all_classes))
		self._colorbar_legend = axes[-1].legend(legend_colors, legend_names, loc='upper center', bbox_to_anchor=(0.5, -1.5), ncol = min(10, len(legend_names)), frameon = False)






	def _recolor_selection_scatter(self, ax, ind_selection, collection, base_colors, length):
		# base_colors[:, :3] = 0.75 * (1.0 - base_colors[:, :3]) + base_colors[:, :3]
		fc = base_colors.copy()
		# slice = [i for i in range(length) if i not in ind_selection]
		kaas = fc[:, :3]
		fc[:, :3] = 0.75 * (1.0 - fc[:, :3]) + fc[:, :3] #Lighten everything except selected points
		fc[ind_selection] = base_colors[ind_selection]

		collection.set_facecolors(fc)
		collection.set_edgecolors(fc)
		self.canvas.draw_idle()

	def _recolor_selection_lineplot(self, ind_selection, collection, base_colors, length):
		# unpacked =
		# raise NotImplementedError("Recolor lineplot not implemented")
		fc = base_colors.copy()
		# slice = [i for i in range(length) if i not in ind_selection]
		nextselection = [i - 1 for i in ind_selection if i !=0] #Always take the line after the selected item

		if len(nextselection) == 0:
			fc[nextselection] = base_colors[nextselection]
		else:
			fc[:, :3] = 0.75 * (1.0 - fc[:, :3]) + fc[:, :3] #Lighten everything except selected points
			# fc[ind_selection] = base_colors[ind_selection]
			fc[nextselection] = base_colors[nextselection]

		collection.set_facecolors(fc)
		collection.set_edgecolors(fc)
		self.canvas.draw_idle()





	def _set_selection(self, loc_selection):
		self.cur_pd_selection = set(loc_selection)
		for ax_idx, (ax, loc, colors, length) in enumerate(zip(self.data_axes, self.data_locs, self.data_colors, self.data_lengths)):
			plot_ind = []

			for i in range(len(loc)):
				if loc[i] in self.cur_pd_selection:
					plot_ind.append(i) #Append all indexes of values that have been selected

			if self.cur_plot_type == "Scatter":
				self._recolor_selection_scatter(ax, plot_ind, self.collections[ax_idx], colors, length)
			else:
				self._recolor_selection_lineplot(plot_ind, self.collections[ax_idx], colors, length)



	def _remake_legend(self, names):
		log.debug("Could not create legend, not implemented")

	def _replot_selected_data(self):
		log.debug("Now replotting selected data")



		# self.canvas.clear_all_axes() #TODO: maybe take a historic-df that looks what columns have changed? Only clear those?
		# self.prepare_axes()




		main_ax = self.canvas.get_axis("main")
		main_ax.set_ylim(0, 1) #Normalize

		self.legend_names = []
		self.legend_colors_dict = {}

		color_based_on_col = self.settings_model.plot_color_method == self.settings_model.plot_color_method_options[0]
		if color_based_on_col:
			self.legend_names = self.settings_model.plot_list
		else:
			color_col = self.settings_model.plot_color_column
			try:
				self.legend_names = set([])
				for name in  self.data_model.df[color_col].unique():
					if type(name) == float and np.isnan(name) or pd.isna(name): #Treat NaN as None
						self.legend_names.add(None)
						continue #Don't add nan
					self.legend_names.add(name)
				self.legend_names = list(self.legend_names)
			except Exception as ex:
				log.warning(f"Cannot create color legend for this plot: {ex}")

		log.debug(f"Legend names {self.legend_names}")
		# self.legend_colors = [color for color in col_colors[:len(self.legend_names)]]

		col_colors = matplotlib.cm.tab10.colors #Default color scheme (but only works up to 10 colors)
		col_colors = [[*color, 1.0] for color in col_colors] #Alpha is missing by default
		if len(self.legend_names) > 10: #Otherwise create a linear separation
			col_colors = matplotlib.cm.rainbow(np.linspace(0,1,len(self.legend_names))) #get new color for each class

		assert(len(col_colors) >= len(self.legend_names)) #This has gone wrong before.... Make sure there are enough colors otherwise the dictionary will fail in a later stage

		color_dict = {name : np.array(color) for name, color in zip(self.legend_names, col_colors)}
		color_dict[None] = np.array([.8, .8, 0.8, 1])
		# color_dict[None] = "kaas"

		self.legend_colors_dict = color_dict
		# self.legend_colors_dict = [color for color in color_dict.values()]

		log.debug(f"Trying to plot columns: {list(self.settings_model.plot_list)}")
		# for col, col_color in zip(self.plot_data.cur_plot_df.columns, col_colors): #go over columns (and give each one a color)



		minmaxes = []
		XYs = []
		self.data_locs = []
		self.data_axes = []
		self.collections = [] #in the case of scatterplots
		self.line2dlist = [] #In the case of lineplots
		self.data_lengths = []
		self.cur_plot_type = self.settings_model.plot_type


		self.data_colors = []

		previous_ax_rect_loc = (0,0)
		self._drag_detectors = []
		# exit(0)
		for col_idx, (col, col_color) in enumerate(zip(list(self.settings_model.plot_list), col_colors)): #go over columns (and give each one a color)

			if col is None or col == "": #skip empty colnames
				continue

			nan_mask = np.isfinite(self.selected_data[col])
			# nan_mask = self.selected_data.index
			# self.selected_data = self.selected_data.fillna(np.nan)
			# self.selected_data = self.selected_data.replace({np.nan: None})


			cur_locs = self.selected_data.index.to_numpy()[nan_mask]
			self.data_locs.append(cur_locs) #To translate in-graph selection back to pandas selection
			X = self.selected_data[self.settings_model.x_axis].to_numpy()[nan_mask] #Remove nan entries #TODO: what if date is none?
			Y = self.selected_data[col].to_numpy()[nan_mask]

			if len(X) == 0 or len(Y) == 0: #Skip if no data
				log.info(f"Columns {col} contained no data... Skipping plotting")
				continue

			cur_ax : matplotlib.axes.Axes = self.canvas.get_twinx("main", col) #Get
			# cur_ax.set_zorder(self.canvas.get_axis("main").get_zorder()+1)
			# cur_ax.patch.set_visible(False)

			# a = X[0]
			# b = X[-1]

			# cur_ax.set_zorder(self.canvas.get_axis("main").get_zorder() - 2) #Get) #Get

			# data_gap_mask = [] #Don't connect datapoints in line-graph if time-distance is more than x seconds
			x_axis_is_dt = isinstance(X[0], pd.Timestamp) or isinstance(X[0], np.datetime64) or pd.api.types.is_datetime64_any_dtype(X[0])
			if x_axis_is_dt:
				X = dates.date2num(X)




			XYs.append( np.vstack((X, Y)).T)

			self.data_lengths.append(len(X))
			self.data_axes.append(cur_ax)
			cur_ax.yaxis.label.set_color(col_color)
			cur_ax.spines['right'].set_color(col_color)

			diff =  abs((max(Y) - min(Y))* 0.05)
			minmax = ( min(Y) - diff, max(Y) + diff) #Take some leeway in the plot to better see edges
			cur_ax.set_ylim(minmax)
			minmaxes.append(minmax)

			x_transform = mtransforms.IdentityTransform() + mtransforms.ScaledTranslation(1,0, cur_ax.transAxes) #Set axes-based offset (right outer edge of axis)
			transform = mtransforms.blended_transform_factory(x_transform, cur_ax.transAxes) #x-axis in pixels, y-axis in axes coords
			# spine_width = 20
			#Get spine width in pixels
						#Get dpi of figure
			dpi = self.canvas.figure.get_dpi()

			cur_ax.spines['right'].set_position(
				('outward', previous_ax_rect_loc[0]/(0.013888*dpi)) #NOTE: 1.388=@100dpi, probabably amount of inches? This `should` work on all dpi's
			) #each axis 60 pixels to the right #TODO: constant?
			# cur_ax.spines['right'].set_position(('outward', col_idx * spine_width)) #each axis 60 pixels to the right #TODO: constant?
			cur_ax.tick_params(axis='y', colors=col_color, labelrotation=90)
			spine_width = cur_ax.spines['right'].get_tightbbox(self.canvas.get_renderer()).width + self.settings_model.font_size
			#Also add the width of the ticklabels
			spine_width += cur_ax.yaxis.get_ticklabels()[0].get_window_extent().width


			# self.rectangle = matplotlib.patches.Rectangle((col_idx * spine_width * self.settings_model.font_size/10.0 * 1.388, 0), 20 * 1.388, 1, fc=col_color, alpha=0.15, transform=transform, clip_on=False) #TODO: Not sure shy a factor is neccesary here,
			self.rectangle = matplotlib.patches.Rectangle((previous_ax_rect_loc[0], previous_ax_rect_loc[1]), spine_width, 1, fc=col_color, alpha=0.15, transform=transform, clip_on=False) #TODO: Not sure shy a factor is neccesary here,

			previous_ax_rect_loc = ( #Get top right corner of rectangl
				self.rectangle.get_bbox().get_points()[1][0], #x1y1-> pick x1
				self.rectangle.get_bbox().get_points()[0][1] #x0y0 -> pick y0 -> results in top right
			)
			# cur_ax.add_patch(self.rectangle) #Are these deleted?
			cur_ax.add_artist(self.rectangle)


			self._drag_detectors.append(
				DragDetector(canvas = self.canvas, ax=cur_ax, rect = self.rectangle, toolbar=self.toolbar)
			)
			# self.canvas.mpl_connect('button_press_event', self.toolbar.

			#link click and drag to drag_zoom of toolbar




			if color_based_on_col: #If all datapoints same color
				self.data_colors.append(np.tile(np.array([col_color[0], col_color[1], col_color[2], 1.0]), (len(X), 1)), )
			else: #If color based on class
				try:
					# color_col = self.settings_model.plot_color_column
					# # color_arr = color_arr.fillna(np.nan)
					# color_arr = self.selected_data.loc[nan_mask, color_col].fillna(np.nan).replace({np.nan: None})#NOTE/TODO: Inserting np.nan in a separate dictionary and then calling replace does not work and results in only the first Nan value being replaced, only if np.nan is in the constructore inside .replace() as denoted here
					# # color_arr = color_arr.fillna(None)
					# # color_arr = np.array(color_arr.map(color_dict).tolist())

					# # color_arr = self.selected_data[color_col].values
					# color_arr = color_arr.map(color_dict).to_list()

					# # kaas = np.unique(color_arr)

					# self.data_colors.append(color_arr)

					# # temp = np.tile(np.array([col_color[0], col_color[1], col_color[2], 1.0]), (len(X), 1))
					# # kaas = np.array(color_arr[:10])
					# kaas1 = self.selected_data.loc[nan_mask, color_col].to_numpy()[4000:4100]
					color_col = self.settings_model.plot_color_column
					color_arr = self.selected_data.loc[nan_mask, color_col].fillna(np.nan).replace({np.nan:None, nan:None, None: None, pd.NaT : None, pd.NA: None}) #NOTE/TODO: Inserting np.nan in a separate dictionary and then calling replace does not work and results in only the first Nan value being replaced, only if np.nan is in the constructore inside .replace() as denoted here
					color_arr = np.array(color_arr.map(color_dict).tolist())#[nan_mask]
					self.data_colors.append(color_arr)

					# temp = np.tile(np.array([col_color[0], col_color[1], col_color[2], 1.0]), (len(X), 1))
					# kaas = np.array(color_arr[:10])



				except KeyError as err:
					raise KeyError(f"KeyError: Selected color-column ({color_col}) resulted in error: {err}, please make sure an existing column is selected under Plot Colors")
			# idx_sorted = np.argsort(self.legend_names)
			log.debug(f"Plotting column: {col}")


			if self.cur_plot_type == "Scatter":
				self.collections.append(cur_ax.scatter(X, Y, c=self.data_colors[-1], label=col, s=1)) #Always plot scatter TODO: is this neccesary for lassoselector?
			else:
				before = time.perf_counter()

				#========== Set color for points far from eachother =========
				dts = self.selected_data["DateTime"].to_numpy()[nan_mask] #TODO: "DateTime is hardcoded here"
				dt_distances = (dts[:-1] - dts[1:]) / np.timedelta64(1, 's')
				dt_distances_mask = dt_distances > 100 #If more than 100 seconds
				# kaas = np.where(dt_distances == True)
				kaas = np.sum(dt_distances_mask)
				self.data_colors[-1][:-1][dt_distances_mask] = self.data_colors[-1][:-1][dt_distances_mask] * [1, 1, 1, 0.1]#Select data colors => skip last value => all where threshold is true => set alpha (-1) to 0.1

				# dt_too_far_apart = # Don't connect points further than x seconds from eachother


				#===============0.298 lineplot ====================
				a = np.expand_dims(np.vstack((X[:-1], Y[:-1])), axis=1)
				b = np.expand_dims(np.vstack((X[1:], Y[1:])), axis=1)
				lines = np.vstack((a, b)).T
				lines = lines.reshape(len(X) - 1, 2, 2)
				lc = matplotlib.collections.LineCollection(lines, colors=self.data_colors[-1])
				cur_ax.add_collection(lc)
				self.collections.append(lc)

			log.debug("Data collections created and added to matplotlib")


		self.canvas.ax_dict["main"].set_facecolor([0, 0, 0, 0]) #Make main axis transparent

		#set rspline of main axis invisible
		self.canvas.ax_dict["main"].spines["right"].set_visible(False)


		# self.canvas.ax_dict["main"].rspine.set_visible(False) #Make main axis transparent

		self.selector.reset_all(self.canvas.ax_dict["main"], XYs, minmaxes, self.data_locs)

		if self.data_model.df_selection is not None and len(self.data_model.df_selection) > 0: #If at least 1 points slected
			self._set_selection(self.data_model.df_selection)

		log.debug(f"legend colors: {self.legend_colors_dict}")

	# def _set_ylim_factor(self, ax_name : str, )


	def _replot_ax_style(self):
		#TODO: line2d or something else better?
		legend_indicator_list = []
		for name in  self.legend_names:
			color = self.legend_colors_dict[name]
			legend_indicator_list.append(matplotlib.lines.Line2D([0], [0], color=color, lw=4))
		legend_indicators = np.array(legend_indicator_list)

		# legend_indicators = np.array([ matplotlib.lines.Line2D([0], [0], color=self.legend_colors_dict[name], lw=4) for name in self.legend_names ]) #line figures in legend
		legend_names = np.array([str(i) for i in self.legend_names])
		idx_sorted = range(len(self.legend_names))

		log.debug(f"legend colors: {self.legend_colors_dict}")


		# plt.title(self.plot_title)
		self.canvas.figure.suptitle(self.plot_title)
		# exit(0)

		self.canvas.ax_dict["main"].set_xlim(left=self.settings_model.plot_domain_limrange.left_val, right=self.settings_model.plot_domain_limrange.right_val)
		self.canvas.ax_dict["main"].set_ylim(0, 1)


		# self.canvas.ax_dict["main"].legend(legend_indicators[idx_sorted], legend_names[idx_sorted], loc='upper center', bbox_to_anchor=(0.5, 1.08), ncol = len(legend_names))
		main_legend = self.canvas.ax_dict["main"].legend(legend_indicators[idx_sorted], legend_names[idx_sorted], loc='upper center', bbox_to_anchor=(0.5, 1.007), ncol = min(len(legend_names), 10), frameon=False)




		for i, name in enumerate(self.canvas.ax_order[:-1]):
			self.canvas.ax_dict[name].set_xlabel("") #Remove xlabels
			self.canvas.ax_dict[name].tick_params(labelbottom=False)#Remove ticks


		if self.settings_model.x_axis == "DateTime":
			temp = matplotlib.dates.AutoDateLocator()
			self.canvas.ax_dict[self.canvas.ax_order[-1]].xaxis.set_major_formatter(matplotlib.dates.ConciseDateFormatter(temp))

		self.canvas.ax_dict[self.canvas.ax_order[-1]].set_xlabel(self.settings_model.x_axis)


		# if plotting colorbar, make sure labels don't get in eachothers way
		if self.settings_model.plotted_labels_list is not None and len(self.settings_model.plotted_labels_list) > 0:
			#Make sure y-labels don't overlap with label
			plt.setp(self.canvas.ax_dict["main"].get_yticklabels(), va="bottom")

			# #Also put x-axis label in the bottom left corner
			# self.canvas.ax_dict[self.canvas.ax_order[-1]].xaxis.set_label_coords(0, -0.1, align="left")



		self.canvas.figure.tight_layout()


	def _reload_selected_data(self):
		# self.selected_data = self.settings_model.df[list(set([i for i in self.settings_model.plots if i is not None]))]

		# #============= X Axis ============
		# if x_axis is None:
		# 	log.error(f"X-Axis {self.settings_model.x_axis} not found in provided data, defaulting to table index")
		# else:
		# 	log.info(f"Using x-axis: {x_axis}")
		# 	self.selected_data[self.settings_model.x_axis] = self.settings_model.df[[self.settings_model.x_axis]]


		#===========Plot xlim===================== TODO: xlim implementation
		x_axis = self.settings_model.x_axis
		plot_xlim = self.settings_model.plot_domain_limrange
		self.plot_title = ""
		self.selected_data = self.data_model._df #Create dataframe view of data that is to be plotted

		for filter in self.settings_model.plot_filters:
			try:
				temp = filter(self.selected_data)
				self.selected_data = temp
			except Exception as err:
				msg = f"Issue while filtering data in view : {err}"
				log.error(msg)
				create_qt_warningbox(msg)

		self.selected_data = self.selected_data.loc[ self.selected_data.index.difference(self.data_model.hidden_datapoints)]


		if plot_xlim is not None and x_axis is not None:
			log.info(f"Setting plot xlim to : {plot_xlim}")

			if plot_xlim.left_val is not None: #if xmin specified
				log.info(f"Setting xlim to min {plot_xlim.left_val}")
				self.selected_data = self.selected_data[ self.selected_data[x_axis] >= plot_xlim.left_val ]

				#If x_axis reformatted left val is float, round to 2 decimal places in title
				if isinstance(plot_xlim.left_val, float): #TODO: create a title formatter - is more neat
					self.plot_title += str(round(plot_xlim.left_val, 2)) + "  -  "
				else:
					self.plot_title += self.x_axis_reformatter(plot_xlim.left_val) + "  -  "


			else:
				self.plot_title += "x  -  "

			if plot_xlim.right_val is not None:  #If xmax specified
				log.info(f"Setting xlim to max {plot_xlim.right_val}")

				if isinstance(plot_xlim.right_val, float):
					self.plot_title += str(round(plot_xlim.right_val, 2))
				else:
					self.plot_title += self.x_axis_reformatter(plot_xlim.right_val)


				self.selected_data = self.selected_data[ self.selected_data[x_axis] <= plot_xlim.right_val ]
			else:
				self.plot_title += "x"
			# if plot_xlim[0] is not None and plot_xlim[1] is not None: #TODO: do this in-plot
			# 	self.canvas.ax.set_xlim(plot_xlim[0], plot_xlim[1])
		else:
			log.info(f"Plot xlim {self.settings_model.plot_domain_limrange} not used for axis {x_axis} due to <None> value (either left/right/xname)")


		#=============== Plot datetime ===================



	def _replot(self):
		self._colorbar_legend = None
		if self.data_model._df is None:
			log.error("Could not replot, no dataframe loaded")
			return
		if self.settings_model.x_axis is None:
			log.error("Could not replot, no x-axis selected")
			return

		matplotlib.rcParams.update({'font.size' : self.settings_model.font_size}) #Setting font size
		self.canvas.remove_axes(except_main=True) #Only keep main axis
		# self.canvas.ax.clear() #TODO: put in canvas?
		# for ax in self.canvas.axes.items():
		# self.canvas.clear_axes() #TODO: neccesary for all?




		self.canvas.figure.subplots_adjust(hspace=0.0)
		before = time.perf_counter()
		self._reload_selected_data()
		log.debug(f"Reloading selected data took: {time.perf_counter() - before}")
		self._replot_colorbars()


		if self.settings_model.fft_toggle: #if fft is toggled on
			if self.settings_model.x_axis != "DateTime": #TODO: do not hardcode "Datetime"? Maybe check pd.type
				create_qt_warningbox("Warning: could not plot fft diagram because X-axis is not Datetime - Pleas turn off FFT or select DateTime for x-axis and replot")
			else:
				self._reload_fft_data()
				self._replot_fft()
		else:
			self.canvas.ax_dict["main"].set_zorder(10) #Draw main axis on top for selection purposes (though this seems to make it so pcolormesh is drawn over all other plots so only do this if fft is off )
		before = time.perf_counter()
		self._replot_selected_data()
		log.debug(f"Replotting selected data took: {time.perf_counter() - before}")
		self._replot_ax_style()

		before = time.perf_counter()

		# self.canvas.ax_dict["main"].patch.set_visible(False)
		self.canvas.draw() #Redraw everything
		log.debug(f"Drawingdata took: {time.perf_counter() - before}")







