from PySide6 import QtWidgets, QtCore

import logging
log = logging.getLogger(__name__)
import datetime
import typing

class CollapsibleGroupBoxLayout(QtWidgets.QGroupBox):


	def __init__(self, groupbox_name, layout: typing.Literal[QtCore.Qt.Orientation.Vertical, QtCore.Qt.Orientation.Horizontal] = QtCore.Qt.Orientation.Vertical, *args, **kwargs):
		super().__init__(groupbox_name, *args,**kwargs)

		self.frame = QtWidgets.QFrame()
		if layout == QtCore.Qt.Orientation.Horizontal:
			self.group_layout = QtWidgets.QHBoxLayout()
		else:
			self.group_layout = QtWidgets.QVBoxLayout()

		self.frame.setLayout(self.group_layout)

		self.setCheckable(True)
		self.toggled.connect(self.toggleHide)

		self.layout = QtWidgets.QVBoxLayout()
		self.layout.addWidget(self.frame)
		self.setLayout(self.layout)

		self.toggleHide(self.isChecked()) #Toggle to current state

	def addWidget(self, widget):
		self.group_layout.addWidget(widget)
	
	def toggleHide(self, on : bool):

		if on:
			self.frame.show()
		else:
			self.frame.hide()