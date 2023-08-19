
#TODO: Make itemchanged contain the final result? Now Get_data needs to be called for each time the neccesary data is used - Or put cache in get_data functions (especially in the case of lists) to not have a cascading effect

import logging
from abc import abstractmethod, abstractproperty
from pydoc import locate

from PySide6 import QtCore, QtWidgets

from mvts_analyzer.utility import GuiUtility

log = logging.getLogger(__name__)


from mvts_analyzer.widgets import datastructures
from mvts_analyzer.widgets.dual_boxes import DualBox, LabelBox


class ListItem(object):
	itemChanged = QtCore.Signal() #child index, signal type
	itemEdited = QtCore.Signal() #child index, signal type 


	@abstractmethod	
	def get_data(self):
		raise NotImplementedError()
	
	@abstractmethod
	def set_data(self, data : list):
		raise NotImplementedError()



class WidgetList(QtWidgets.QWidget):

	"""
	"""
	
	# valueSliderEdited = QtCore.Signal(int)
	# valueBoxEdited = QtCore.Signal(str)

	widgetCountChanged = QtCore.Signal(int) #child index, signal type
	widgetCountEdited = QtCore.Signal(int) #child index, signal type

	def __init__(self, widget_type, widget_creation_args={}, fixed_height_increase=35, user_addable=True, layout = "vertical", *args, **kwargs):
		# super(WidgetList, self).__init__(*args, **kwargs)
		super().__init__(*args, **kwargs)

		# self.val_type = utility.get_dict_entry(item_dict, ("entry", "value_type"))

		if layout == "horizontal":
			self._layout = QtWidgets.QHBoxLayout(self)
		else:
			if layout != "vertical":
				log.error(f"Error: could not parse layout {layout} - defaulting to vertical")
			self._layout = QtWidgets.QVBoxLayout(self)

		self._widgets_layout = QtWidgets.QVBoxLayout()
		self.widget_type = widget_type
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
		
		# self._widgets_layout.addStretch()

		# self.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.MinimumExpanding)


		# self.setFixedHeight(40)
		# self.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.MinimumExpanding)
		self._add_btn.clicked.connect(self._append_btn_clicked)
		self._remove_btn.clicked.connect(self._pop_btn_clicked) 

		# self.slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
		# self.text_box = QtWidgets.QLineEdit()
		# self.text_converter = text_converter

	def set_widgetcount(self, new_count : int):
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
		self.append()
		self.widgetCountEdited.emit(len(self.widgets))

	def _pop_btn_clicked(self, *_):
		if len(self.widgets) > 0:
			self.pop()
			self.widgetCountEdited.emit(len(self.widgets))

	def append(self):
		# log.debug(f"New widget, now at count: {len(self.widgets)}")
		# log.debug(f"Widget type: {self.widget_type} - creation args: {self.widget_creation_args}")
		new_widget = self.widget_type(**self.widget_creation_args)
		self.widgets.append(new_widget)
		self._widgets_layout.addWidget(new_widget)
		self.widgetCountChanged.emit(len(self.widgets))
		return new_widget

	def pop(self):
		if len(self.widgets) == 0: #If cannot delete
			log.debug("Cannot delete widgets as there are none")
			return
		self.widgets[-1].setParent(None) #Set parent to None (delete widget)
		self.widgets = self.widgets[:-1] #Remove last item
		# self.setFixedHeight(40 + self._fixed_height_increase * len(self.widgets))
		self.widgetCountChanged.emit(len(self.widgets))
		log.debug(f"Removed last widget, remaining count: {len(self.widgets)}")

	


class ListWidgetList(WidgetList, ListItem): #WidgetList that makes nested items easier #NOTE: 19-06-2023 removd ListItem and added
		#itemchanged signal and itemedited signal manually due to init problems
	itemChanged = QtCore.Signal() #child index, signal type
	itemEdited = QtCore.Signal() #child index, signal type 

	itemChanged = QtCore.Signal() #child index, signal type
	itemEdited = QtCore.Signal() #child index, signal type 


	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.widgetCountEdited.connect(lambda *_ : self.itemEdited.emit())
		self.widgetCountChanged.connect(lambda *_: self.itemChanged.emit())

	def append(self):
		# new_widget = super(WidgetList, self).append()
		new_widget = WidgetList.append(self)
		self.blockSignals(True)
		# new_widget = super(ListWidgetList, self).append()
		# new_d
		 
		new_widget.itemEdited.connect(self.itemEdited)
		new_widget.itemChanged.connect(self.itemChanged)
		self.blockSignals(False)


	def get_data(self):
		data = []
		for widget in self.widgets:
			data.append(widget.get_data())		
		return data
	
	def set_data(self, data : list):
		self.blockSignals(True)
		self.set_widgetcount(len(data))
		for item, widget in zip(data, self.widgets):
			widget.set_data(item)
		self.blockSignals(False)
		self.itemChanged.emit()
			
			
class ListTextboxAndList(ListItem, QtWidgets.QWidget): #Item for widgetlist: editable textbox with a widgetlist
	
	itemChanged = QtCore.Signal() #child index, signal type
	itemEdited = QtCore.Signal() #child index, signal type 

	def __init__(self, box_stretch=1, list_stretch=1, box_args = {}, *args, **kwargs):
		super().__init__()
		self.layout = QtWidgets.QHBoxLayout()
		self.list = ListWidgetList(*args, **kwargs)

		self.list.itemChanged.connect(lambda *_: self.itemChanged.emit())
		self.list.itemEdited.connect(lambda *_: self.itemEdited.emit())

		self.box = QtWidgets.QLineEdit(**box_args)
		self.box.editingFinished.connect(lambda *_: self.itemEdited.emit())
		self.box.editingFinished.connect(lambda *_: self.itemChanged.emit())

		self.layout.addWidget(self.box, box_stretch)
		self.layout.addWidget(self.list, list_stretch)

		self.setLayout(self.layout)

	def get_data(self):
		# data = []
		# for widget in self.widgets:
		# 	data.append(widget.get_data())		
		return [self.box.text(), self.list.get_data()]
	
	def set_data(self, data : list):
		self.blockSignals(True)
		self.box.setText(data[0])
		self.list.set_data(data[1])
		self.blockSignals(False)
		self.itemChanged.emit()

class ListBox(QtWidgets.QLineEdit, ListItem):
	
	itemChanged = QtCore.Signal() #child index, signal type
	itemEdited = QtCore.Signal() #child index, signal type 

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.editingFinished.connect(lambda *_: self.itemChanged.emit()) 
		self.editingFinished.connect(lambda *_: self.itemEdited.emit()) 


	def get_data(self):
		# data = []
		# for widget in self.widgets:
		# 	data.append(widget.get_data())		
		return self.text()
	
	def set_data(self, data : str):
		self.blockSignals(True)
		self.setText(data)
		self.blockSignals(False)
		self.itemChanged.emit()

class ListBoxAndBox(DualBox, ListItem):
	
	itemChanged = QtCore.Signal() #child index, signal type
	itemEdited = QtCore.Signal() #child index, signal type 


	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.boxChanged.connect(self.itemChanged)
		self.boxEdited.connect(self.itemEdited)

	def get_data(self):
		# data = []
		# for widget in self.widgets:
		# 	data.append(widget.get_data())		
		return self.get_texts()
	
	def set_data(self, data : list):
		self.blockSignals(True)
		self.box[0].setText(data[0])
		self.box[1].setText(data[0])
		self.blockSignals(False)
		self.itemChanged.emit(True)