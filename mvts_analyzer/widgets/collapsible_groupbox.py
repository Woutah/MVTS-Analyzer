"""
Implements CollapsibleGroupBoxLayout - A groupbox that collapses when unchecked
"""
import logging
import typing
from PySide6 import QtCore, QtWidgets

log = logging.getLogger(__name__)

#pylint: disable=invalid-name

class CollapsibleGroupBoxLayout(QtWidgets.QGroupBox):
	"""
	Based on QT's QGroupBox, but collapses when unchecked
	"""

	def __init__(self,
	    	groupbox_name,
			layout: typing.Literal[QtCore.Qt.Orientation.Vertical,
			  QtCore.Qt.Orientation.Horizontal] = QtCore.Qt.Orientation.Vertical, **kwargs):
		super().__init__(groupbox_name, **kwargs)

		self.frame = QtWidgets.QFrame()
		if layout == QtCore.Qt.Orientation.Horizontal:
			self.group_layout = QtWidgets.QHBoxLayout()
		else:
			self.group_layout = QtWidgets.QVBoxLayout()

		self.frame.setLayout(self.group_layout)

		self.setCheckable(True)
		self.toggled.connect(self.toggleHide)

		self.main_layout = QtWidgets.QVBoxLayout()
		self.main_layout.addWidget(self.frame)
		self.setLayout(self.main_layout)

		self.toggleHide(self.isChecked()) #Toggle to current state

	def addWidget(self, widget):
		"""Add widget to layout"""
		self.group_layout.addWidget(widget)

	def toggleHide(self, on : bool):
		"""Toggle hide/show"""
		if on:
			self.frame.show()
		else:
			self.frame.hide()
