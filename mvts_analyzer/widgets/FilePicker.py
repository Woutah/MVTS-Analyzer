from PySide6 import QtWidgets, QtCore


# class FilePicker():
#     pass


if __name__ == "__main__":
	app = QtWidgets.QApplication([])
	# window = QtWidgets.QWidget()
    testpath = ""
	#Create a dir model
	model = QtWidgets.QFileSystemModel()
	model.setRootPath(QtCore.QDir.rootPath())
	# model.setRootPath(testpath)
	model.setFilter(QtCore.QDir.NoDotAndDotDot | QtCore.QDir.AllDirs)

	#Filter to only json files
	# model.setNameFilters(["*.json"])

	#Create a tree view
	tree = QtWidgets.QTreeView()
	tree.setModel(model)
	tree.setRootIndex(model.index(testpath))
	tree.setAnimated(False)
	tree.setIndentation(20)
	tree.setSortingEnabled(True)
	tree.setWindowTitle("Dir View")
	tree.resize(640, 480)
	


	tree.show()
	app.exec()