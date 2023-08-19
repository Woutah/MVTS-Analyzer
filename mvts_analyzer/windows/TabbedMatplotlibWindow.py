# Largely based on https://stackoverflow.com/questions/37346845/tabbed-window-for-matplotlib-figures-is-it-possible - Superjax

import matplotlib
# prevent NoneType error for versions of matplotlib 3.1.0rc1+ by calling matplotlib.use()
# For more on why it's nececessary, see
# https://stackoverflow.com/questions/59656632/using-qt5agg-backend-with-matplotlib-3-1-2-get-backend-changes-behavior
matplotlib.use('qt5agg')

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QTabWidget, QVBoxLayout, QSplitter
import PySide6.QtCore as QtCore
# import PySide6.QtCore.Qt 
import matplotlib.pyplot as plt
import sys

class TabbedMatplotlibWindow(QWidget):
	def __init__(self, parent=None):
		# self.app = QApplication(sys.argv)
		super().__init__(parent)
		self.MainWindow = QMainWindow(self)
		self.MainWindow.setWindowTitle("plot window")
		self.canvases = []
		self.figure_handles = []
		self.toolbar_handles = []
		self.tab_handles = []
		self.current_window = -1
		self.tabs = QTabWidget()
		self.MainWindow.setCentralWidget(self.tabs)
		self.MainWindow.resize(1280, 900)
		# self.MainWindow.show()

	def addPlot(self, title, figure):
		new_tab = QWidget()
		layout = QVBoxLayout()
		new_tab.setLayout(layout)

		# figure.subplots_adjust(left=0.05, right=0.99, bottom=0.05, top=0.91, wspace=0.2, hspace=0.2)
		new_canvas = FigureCanvas(figure)
		new_toolbar = NavigationToolbar(new_canvas, new_tab)

		layout.addWidget(new_canvas)
		layout.addWidget(new_toolbar)
		self.tabs.addTab(new_tab, title)

		self.toolbar_handles.append(new_toolbar)
		self.canvases.append(new_canvas)
		self.figure_handles.append(figure)
		self.tab_handles.append(new_tab)

	def addPlots(self, title, figures, stretches = []):
		new_tab = QWidget()
		layout = QVBoxLayout()
		new_tab.setLayout(layout)
		layout.setContentsMargins(0, 0, 0, 0)
		if len(stretches) == 0:
			stretches = [1] * len(figures)

		for stretch, figure in zip(stretches, figures):
			# figure.subplots_adjust(left=0.05, right=0.99, bottom=0.05, top=0.91, wspace=0.2, hspace=0.2)
			new_canvas = FigureCanvas(figure)
			new_toolbar = NavigationToolbar(new_canvas, new_tab)

			#add sublayout to widget, then to layout
			sublayout = QVBoxLayout()
			# sublayout.setContentsMargins(0, 0, 0, 0)
			sublayout_wrapper = QWidget()
			sublayout_wrapper.setLayout(sublayout)
			# sublayout_wrapper.setContentsMargins(0, 0, 0, 0)
			# splitter.addWidget(sublayout_wrapper)

			sublayout.addWidget(new_canvas)
			sublayout.addWidget(new_toolbar)
			# splitter.addWidget(sublayout_wrapper)
			layout.addWidget(sublayout_wrapper, stretch=stretch)

			self.toolbar_handles.append(new_toolbar)
			self.canvases.append(new_canvas)
			self.figure_handles.append(figure)
			self.tab_handles.append(new_tab)
		
		self.tabs.addTab(new_tab, title)


	def show(self):
		self.MainWindow.show()
	#     self.app.exec_()

if __name__ == '__main__':
	import numpy as np

	pw = TabbedMatplotlibWindow()

	x = np.arange(0, 10, 0.001)

	f = plt.figure()
	ysin = np.sin(x)
	plt.plot(x, ysin, '--')
	pw.addPlot("sin", f)

	f = plt.figure()
	ycos = np.cos(x)
	plt.plot(x, ycos, '--')
	pw.addPlot("cos", f)
	pw.show()