"""
The main entry point - we launch the app from here (optionally with arguments)
"""

import argparse
import logging
import os
import sys

import matplotlib.pyplot as plt
from PySide6 import QtGui, QtWidgets
from mvts_analyzer.windows.main_window import MainWindow

log = logging.getLogger(__name__)


def main(debug_level=logging.INFO):
	"""The main function, starts the app and parses arguments
	"""
	print("Started main function")
	plt.ioff() #Dont just spit out plots/turn off interactive plotting, but keep them in memory
	#TODO: Note that it is possible that this will break some things??
	formatter = logging.Formatter("[{pathname:>90s}:{lineno:<4}]  {levelname:<7s}   {message}", style='{')
	handler = logging.StreamHandler()
	handler.setFormatter(formatter)
	logging.basicConfig(
		handlers=[handler],
		level=debug_level)
	logging.getLogger('matplotlib').setLevel(logging.INFO)
	logging.getLogger('fontmanager').setLevel(logging.INFO)
	logging.getLogger('asyncua').setLevel(logging.WARN)
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
	parser.add_argument("-e", "--example",
						help="Load the example data",
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
		cur_path = os.path.dirname(os.path.realpath(__file__))
		app.setStyleSheet(
			open(os.path.join(cur_path, "res", "stylesheets", "qt-dark-theme.stylesheet"), encoding="utf-8").read())
		plt.style.use('dark_background')

	graph_model_args = {}

	if args.example:
		graph_model_args["df_path"] = os.path.join(
			os.path.dirname(os.path.realpath(__file__)), 
			"example",
			"example_data.xlsx"
		)
	elif args.file is not None:
		graph_model_args["df_path"] = args.file

	main_win = MainWindow(graph_model_args=graph_model_args)
	if args.use_monitor:
		#Launch on monitor with given index
		monitor = app.screens()[args.launch_on_monitor].geometry()
	else: #Otherwise launch on primary monitor
		monitor = QtGui.QGuiApplication.primaryScreen().geometry()

	main_win.setGeometry(
		int(0.05* monitor.width()), int(0.05* monitor.height()), int(0.9*monitor.width()), int(0.9*monitor.height()))
	main_win.move(monitor.left(), monitor.top())
	main_win.show()
	app.exec_()
	log.info("End of main reached... Exiting...")


if __name__ == "__main__":
	main(logging.DEBUG)
