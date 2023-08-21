"""
Implements a tabbed matplotlib window - we can add multiple plots that are shown in a tabbed Qt-window
"""

#Largely based on https://stackoverflow.com/questions/37346845/tabbed-window-for-matplotlib-figures-is-it-possible


import matplotlib
# import PySide6.QtCore.Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import \
    FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import \
    NavigationToolbar2QT as NavigationToolbar
from PySide6.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget

# prevent NoneType error for versions of matplotlib 3.1.0rc1+ by calling matplotlib.use()
# For more on why it's nececessary, see
# https://stackoverflow.com/questions/59656632/using-qt5agg-backend-with-matplotlib-3-1-2-get-backend-changes-behavior
matplotlib.use('qt5agg')

class TabbedMatplotlibWindow(QWidget):
	"""
	A qt-window to which we can add matpotlib-plots which are shown in separate tabs
	"""
	def __init__(self, parent=None):
		super().__init__(parent)
		self.main_window = QMainWindow(self)
		self.main_window.setWindowTitle("plot window")
		self.canvases = []
		self.figure_handles = []
		self.toolbar_handles = []
		self.tab_handles = []
		self.current_window = -1
		self.tabs = QTabWidget()
		self.main_window.setCentralWidget(self.tabs)
		self.main_window.resize(1280, 900)
		# self.MainWindow.show()

	def add_plot(self, title, figure):
		"""Add a plot to the window - creates a new tab"""
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

	def add_plots(self, title, figures, stretches = None):
		"""
		Add multiple plots to the window - creates a new tab for each one
		"""
		if stretches is None:
			stretches = []
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
		self.main_window.show()
	#     self.app.exec_()

if __name__ == '__main__':
	import numpy as np

	pw = TabbedMatplotlibWindow()

	x = np.arange(0, 10, 0.001)

	f = plt.figure()
	ysin = np.sin(x)
	plt.plot(x, ysin, '--')
	pw.add_plot("sin", f)

	f = plt.figure()
	ycos = np.cos(x)
	plt.plot(x, ycos, '--')
	pw.add_plot("cos", f)
	pw.show()
