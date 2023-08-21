"""
Implements:
WidgetList - A list of widgets, widgets can be added and removed from the list.
ListItem - Base-class for items in a widgetlist, forces implementation of a get/set data function so we can easily
	set all data in the list at once using a list.

"""

import logging
from abc import abstractmethod
from PySide6 import QtCore, QtWidgets


log = logging.getLogger(__name__)


class ListItem(object):
	"""Base-class for items in a widgetlist"""
	itemChanged = QtCore.Signal() #child index, signal type
	itemEdited = QtCore.Signal() #child index, signal type

	@abstractmethod
	def get_data(self):
		"""Get the data from the item"""
		raise NotImplementedError()

	@abstractmethod
	def set_data(self, data : list):
		"""Set the data of the item"""
		raise NotImplementedError()



class WidgetList(QtWidgets.QWidget):
	"""
	A list of widgets, we can add/remove widgets from the list.
	All elements inherit from ListItem, enabling us the get/set data from the list efficiently.
	"""

	# valueSliderEdited = QtCore.Signal(int)
	# valueBoxEdited = QtCore.Signal(str)

	widgetCountChanged = QtCore.Signal(int) #child index, signal type
	widgetCountEdited = QtCore.Signal(int) #child index, signal type

	def __init__(self,
			widget_type,
			widget_creation_args=None,
			fixed_height_increase=35,
			user_addable=True,
			layout = "vertical",
			**kwargs):
		# super(WidgetList, self).__init__(*args, **kwargs)
		super().__init__(**kwargs)

		# self.val_type = utility.get_dict_entry(item_dict, ("entry", "value_type"))

		if layout == "horizontal":
			self._layout = QtWidgets.QHBoxLayout(self)
		else:
			if layout != "vertical":
				log.error(f"Error: could not parse layout {layout} - defaulting to vertical")
			self._layout = QtWidgets.QVBoxLayout(self)

		self._widgets_layout = QtWidgets.QVBoxLayout()
		self.widget_type = widget_type
		if widget_creation_args is None:
			widget_creation_args = {}
		self.widget_creation_args = widget_creation_args
		self.widgets = []


		self._btn_layout = QtWidgets.QHBoxLayout()
		self._remove_btn = QtWidgets.QPushButton(text="-")
		self._add_btn = QtWidgets.QPushButton(text="+")

		self._btn_layout.addWidget(self._remove_btn, 50)
		self._btn_layout.addWidget(self._add_btn, 50)
		if user_addable: #If user can add/remove widgets
			self._layout.addLayout(self._btn_layout)

		self._layout.addLayout(self._widgets_layout)

		self._fixed_height_increase=fixed_height_increase

		self._add_btn.clicked.connect(self._append_btn_clicked)
		self._remove_btn.clicked.connect(self._pop_btn_clicked)


	def set_widgetcount(self, new_count : int):
		"""
		Set the amount of widgets to be displayed. If the new count is higher than the current count, we add widgets.
		If the new count is lower than the current count, we remove widgets.
		"""
		if new_count == len(self.widgets): #If nothing changed
			return
		new_count = max(0 , new_count)
		self.blockSignals(True)
		while len(self.widgets) > new_count:
			self.pop()
		while len(self.widgets) < new_count:
			self.append()

		self.blockSignals(False)
		self.widgetCountChanged.emit(len(self.widgets))


	def _append_btn_clicked(self, *_):
		"""
		Is called on click of the add button, calls the append-function and emits the changed signal
		"""
		self.append()
		self.widgetCountEdited.emit(len(self.widgets))

	def _pop_btn_clicked(self, *_):
		"""
		On click of the remove button, remove the last widget
		"""
		if len(self.widgets) > 0:
			self.pop()
			self.widgetCountEdited.emit(len(self.widgets))

	def append(self):
		"""
		Add a new widget to the list, and emit the changed signal
		"""
		new_widget = self.widget_type(**self.widget_creation_args)
		self.widgets.append(new_widget)
		self._widgets_layout.addWidget(new_widget)
		self.widgetCountChanged.emit(len(self.widgets))
		return new_widget

	def pop(self):
		"""
		Pop the last widget from the list, and emit the changed signal
		"""
		if len(self.widgets) == 0: #If cannot delete
			log.debug("Cannot delete widgets as there are none")
			return
		self.widgets[-1].setParent(None) #Set parent to None (delete widget)
		self.widgets = self.widgets[:-1] #Remove last item
		# self.setFixedHeight(40 + self._fixed_height_increase * len(self.widgets))
		self.widgetCountChanged.emit(len(self.widgets))
		log.debug(f"Removed last widget, remaining count: {len(self.widgets)}")
