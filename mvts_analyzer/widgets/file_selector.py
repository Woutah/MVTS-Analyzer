from PySide6 import QtWidgets, QtCore
from pydoc import locate
import logging
log = logging.getLogger(__name__)


class FileSelector(QtWidgets.QWidget):

	fileNameChanged = QtCore.Signal(str)
	# selectionFiletypeChanged = QtCore.Signal(str)

	def __init__(self, *args, **kwargs):
		super(FileSelector, self).__init__(*args, **kwargs)
		# self.refresh_properties() #get properties from dict
		# self.update_ui() #update based on those properties
		log.info("Initializing confFileSelector")
		self.layout = QtWidgets.QHBoxLayout()
		self.setLayout(self.layout)


		self.cur_path_lbl = QtWidgets.QLabel()
		self.file_dialog_btn = QtWidgets.QPushButton()
		self.file_dialog_btn.clicked.connect(self._file_picker)

		# self.drop_selector = QtWidgets.QComboBox()
		# self.drop_selector.currentIndexChanged.connect(self.on_select)
		self.selection_filetype = "*"
		self.cur_path = None

		self.layout.addWidget(self.cur_path_lbl)
		self.layout.addWidget(self.file_dialog_btn)
	
	def set_selection_filetype(self, new_filetype : str):
		"""Set the desired filetype when selecting new source

		Args:
			filetype (str): Filetype extension of the form "*.*"
		"""
		self.selection_filetype = new_filetype


	def set_cur_path(self, new_path : str):
		self.cur_path = new_path
		self.cur_path_lbl.setText(new_path)
		self.fileNameChanged.emit(new_path)

	
	def _file_picker(self):
		fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', 
					self.cur_path, self.selection_filetype)

		log.debug("Picked file: {}".format(fname))

		self.set_cur_path(fname[0])
		# self.changed_value(fname) #update value #TODO: fname[1] contains the filetype (path, filetype)

	# def _update_ui(self):
	# 	#Should be done automatically
	# 	cur_path = str(utility.get_dict_entry(self.properties, ["val"]))
	# 	self.cur_path_lbl.setText(cur_path)

