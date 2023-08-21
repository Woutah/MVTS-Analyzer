"""
A helper class for selecting points in matplotlib axes.
When the plot is created, we pass the axes, and the pandas indexes to this class. Upon selection, the pandas
indexes are emitted.
"""
import logging
import time

import matplotlib.axes
import matplotlib.backend_bases
import matplotlib.collections
import matplotlib.lines
import matplotlib.path
import matplotlib.widgets
import numpy as np
from PySide6 import QtCore, QtWidgets

log = logging.getLogger(__name__)

class CollectionSelector(QtWidgets.QWidget):
	#Inspired from : https://matplotlib.org/stable/gallery/widgets/lasso_selector_demo_sgskip.html
	"""
	Select indices from a matplotlib collection using `LassoSelector`.

	Selected indices are saved in the `ind` attribute. This tool fades out the
	points that are not part of the selection using a simple brightness approximation.
	"""

	pdSelectionEdited = QtCore.Signal(object)

	def __init__(self,
				ax,
				xys,
				minmaxes,
				locs):
		super().__init__()
		self.reset_all(
			ax,
			xys,
			minmaxes,
			locs
		)

	def reset_all(self,
				selector_ax : matplotlib.axes.Axes,
				xys,
				minmaxes : np.ndarray,
				locs
			):
		"""Reset all settings

		Args:
			ax (matplotlib.axes.Axes): The main axis, y-lim should be 0.0-1.0 to accomodate for normalization
			collections (matplotlib.collections.Collection): List of collections for each ax used
			minmaxes (np.array): The min-max values for each axis, used to calculate the selection for each axis
			locs (np.array): Array with the pandas-plot indexes which is used to emit the selected pandas indexes
			brightness_other (float): brightness used to calculate not-selected naN values
				(simple rule based on HSL brightness)
			redraw_on_selection (bool): turns on or off redraws after selection
			update_graphics_on-selection (bool): whether graphics should be updated immediately after selection
				(grey out not-selected items) for efficiency this can be turned off when pandas selection changes are
				first passed through a model/controller
				and passed back (as this would result in 2 redraws)
			lineplot (bool): whether the target plot is a lineplot, this means collections contains a list of Line2D
				instead of a collection of points
		"""
		self._ax = selector_ax
		self._canvas = None
		if selector_ax is not None:
			self._canvas = selector_ax.figure.canvas
			self._lmbselector = matplotlib.widgets.LassoSelector(
				selector_ax,
				onselect=self.on_select_lasso,
				button=matplotlib.backend_bases.MouseButton.LEFT,
			)
			self._mmbselector = matplotlib.widgets.RectangleSelector(
				selector_ax,
				onselect=self.on_select_rect,
				button=matplotlib.backend_bases.MouseButton.MIDDLE,
			)
			self._rmbselector = matplotlib.widgets.SpanSelector(
				selector_ax, onselect=self.on_select_span,
				direction="horizontal",
				useblit=True,
				props=dict(alpha=0.2, facecolor='red'),
				button=matplotlib.backend_bases.MouseButton.RIGHT,
			)


		self._locs = locs #The pandas idx's

		before = time.perf_counter()
		self._loc_to_indxs = [] #Dictionary to convert loc values back to indexes (should save time when converting)
		for loc in locs:
			cur_loc_to_indx = {}
			for i, cur_loc in enumerate(loc):
				cur_loc_to_indx[cur_loc] = i
			self._loc_to_indxs.append(cur_loc_to_indx)

		log.debug(f"Creating loc->index dictionary took: {time.perf_counter() - before}")
		self._minmaxes = minmaxes
		# self._selections = [] #2d array with current selected ids in each ax
		self._selection_locs = [] #unique list of all selected ids
		self._selection_locs_set = None

		self._xys = xys


	def on_select_rect(self,
				eclick : matplotlib.backend_bases.MouseEvent,
				erelease : matplotlib.backend_bases.MouseEvent,
			) -> None:
		"""Selects all points within the given rectangle

		Args:
			eclick (matplotlib.backend_bases.MouseEvent): The mouse event when the mouse button is pressed
			erelease (matplotlib.backend_bases.MouseEvent): The mouse event when the mouse button is released

		ret:
			None
		"""
		pd_locs = set([])
		for xy_coord, minmax, loc in zip(self._xys, self._minmaxes, self._locs):
			ind = np.nonzero(
				(xy_coord[:, 0] >= eclick.xdata)
				& (xy_coord[:, 0] <= erelease.xdata)
				& (xy_coord[:, 1] >= (eclick.ydata * (minmax[1] - minmax[0]) + minmax[0]))
				& (xy_coord[:, 1] <= (erelease.ydata * (minmax[1] - minmax[0]) + minmax[0]))
				)[0]
			pd_locs.update(list(loc[ind]))

		log.debug(f"Currently selected locs: {list(pd_locs)[:min(len(pd_locs), 3)]}... etc (len={len(pd_locs)})")
		self.pdSelectionEdited.emit(pd_locs)


	def on_select_span(self, minval: float, maxval: float) -> None:
		"""Selects all points within the given span

		Args:
			minval (float): The minimum value
			maxval (float): The maximum value
		"""
		pd_locs = set([])
		for xy_coord, minmax, loc in zip(self._xys, self._minmaxes, self._locs): #pylint: disable=unused-variable
			ind = np.nonzero((xy_coord[:, 0] >= minval) & (xy_coord[:, 0] <= maxval))[0]
			pd_locs.update(list(loc[ind]))

		log.debug(f"Currently selected locs: {list(pd_locs)[:min(len(pd_locs), 3)]}... etc (len={len(pd_locs)})")
		self.pdSelectionEdited.emit(pd_locs)

	def on_select_lasso(self, verts) -> None:
		"""When selecting using the lasso tool this function is called

		Args:
			verts: matplotlib points for the lasso, used to select points that lie within lasso-range
		"""
		log.debug(f"Selection verts (new): {verts}")

		pd_locs = set([])
		# ind_locs = set([])
		for xy_coord, minmax, loc in zip(self._xys, self._minmaxes, self._locs):
			unnormalized_verts = [(vert[0], vert[1] * (minmax[1] - minmax[0]) + minmax[0]) for vert in verts]
			path = matplotlib.path.Path(unnormalized_verts)
			ind = np.nonzero(path.contains_points(xy_coord))[0]
			pd_locs.update(list(loc[ind]))
			# ind_locs.update(list(ind))

		log.debug(f"Currently selected locs: {list(pd_locs)[:min(len(pd_locs), 3)]}... etc (len={len(pd_locs)})")
		self.pdSelectionEdited.emit(pd_locs)
