from PySide6 import QtCore, QtGui, QtWidgets
import abc
import logging
log = logging.getLogger(__name__)


class DualPrimitive(QtWidgets.QWidget):
	boxChanged = QtCore.Signal(tuple) #[str, str]
	boxEdited = QtCore.Signal(tuple)#[str, str] 

	def __init__(self, *args, **kwargs):
		super(DualPrimitive, self).__init__(*args, **kwargs)
		self.boxEdited.connect(self.boxChanged) #Edit always means change but not the other way around
		return

	@abc.abstractmethod
	def set_texts(self, text1, text2):
		pass

	@abc.abstractmethod
	def get_texts(self):
		pass

class LabelBox(DualPrimitive):
	

	def __init__(self, label_txt = "", box_txt = "", *args, **kwargs):
		super(LabelBox, self).__init__(*args, **kwargs)
		self.layout = QtWidgets.QHBoxLayout()

		#====== Label =========
		self.label = QtWidgets.QLabel()
		self.label.setText(label_txt)
		self.layout.addWidget(self.label)

		#======== Box ===========
		self.default_txt = box_txt
		self.box = QtWidgets.QLineEdit(box_txt)
		self.box.textChanged.connect(lambda *_: self.boxEdited.emit(self.get_texts()))

		#Add to layout
		self.layout.addWidget(self.label)
		self.layout.addWidget(self.box)
		self.setLayout(self.layout)


	def set_texts(self, text1, text2):
		self.label.setText(text1)
		self.box.setText(text2)
		self.boxChanged.emit(self.get_texts())

	def get_texts(self):
		return (self.label.text(), self.box.text())


class DualBox(DualPrimitive):
	def __init__(self, box1_txt = "", box2_txt = "", *args, **kwargs):
		super(DualBox, self).__init__(*args, **kwargs)
		self.layout = QtWidgets.QHBoxLayout()
		#======== Box ===========
		self.default_txts = [box1_txt, box2_txt]

		self.box = [None, None]

		for i in range(2):
			self.box[i] = QtWidgets.QLineEdit(self.default_txts[i])
			self.box[i].textChanged.connect(lambda *_: self.boxEdited.emit(self.get_texts())) #Emit both on change
			self.layout.addWidget(self.box[i])
		
		#Add to layout
		self.setLayout(self.layout)

	def set_texts(self, text1, text2):
		self.box[0].setText(text1)
		self.box[1].setText(text2)
		self.boxChanged.emit(self.get_texts())

	def get_texts(self):
		return (self.box[0].text(), self.box[1].text())
