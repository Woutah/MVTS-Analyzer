"""
The main entry point - we launch the app from here (optionally with arguments)	
"""

import logging

import argparse
import sys

import matplotlib.pyplot as plt
from PySide6 import QtGui, QtWidgets
from res.Paths import Paths

from mvts_analyzer.windows.main_window import MainWindow
log = logging.getLogger(__name__)


def main(debug_level=logging.INFO):
	"""The main function, starts the app and parses arguments
	"""
	print("Started main function")
	plt.ioff() #Dont just spit out plots/turn off interactive plotting, but keep them in memory TODO: Note that it is possible that this will break some things?? 
	formatter = logging.Formatter("[{pathname:>90s}:{lineno:<4}]  {levelname:<7s}   {message}", style='{')
	handler = logging.StreamHandler()
	handler.setFormatter(formatter)
	logging.basicConfig(
		handlers=[handler],
		level=debug_level)
	logging.getLogger('matplotlib').setLevel(logging.INFO)
	logging.getLogger('fontmanager').setLevel(logging.INFO)
	logging.getLogger('asyncua').setLevel(logging.WARN)
	# logging.getLogger('asyncua').setLevel(logging.WARN)
	logging.getLogger('numba').setLevel(logging.WARN)
	logging.getLogger('apscheduler').setLevel(logging.ERROR)

	parser = argparse.ArgumentParser(description='Tool arguments')
	parser.add_argument("-f", "--file", 
						help="Path to initially loaded data (.xlsx/.csv or pickled pd.dataframe)",
						default=None
					)

	#Argument for dark mode store true
	parser.add_argument("-d", "--dark_mode",
						help="Turn on dark mode for the app.",
						action="store_true",
						default=False
					)

	parser.add_argument("-m", "--use_monitor",
						help="Launch on monitor with given index (default is primary monitor).",
						default=None,
						type=int
					)

	args = parser.parse_args()

	app = QtWidgets.QApplication(sys.argv)
	
	if args.dark_mode:
		app.setStyleSheet(open(Paths.DarkStyleSheetFilePath).read())
		plt.style.use('dark_background')

	w = MainWindow(graph_model_args={"df_path": args.file})
	if args.use_monitor:
		#Launch on monitor with given index
		monitor = app.screens()[args.launch_on_monitor].geometry()
	else: #Otherwise launch on primary monitor
		monitor = QtGui.QGuiApplication.primaryScreen().geometry()

	w.setGeometry( int(0.05* monitor.width()), int(0.05* monitor.height()), int(0.9*monitor.width()), int(0.9*monitor.height()))
	w.move(monitor.left(), monitor.top())
	w.show()
	app.exec_()
	log.info("End of main reached... Exiting...")


if __name__ == "__main__":
	main(logging.DEBUG)