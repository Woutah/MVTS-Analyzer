"""
The main entry point - we launch the app from here (optionally with arguments)	
"""

import logging
# from mvts_analyzer.utility.
log = logging.getLogger(__name__)
from res.Paths import Paths
#================= GUI ===========================
# from mvts_analyzer.windows.MainWindow import MainWindow
from mvts_analyzer.windows.main_window import MainWindow
from PySide6 import QtGui, QtWidgets
import argparse 
import matplotlib.pyplot as plt
# from PySide6.QtWidgets import


#

if __name__ == "__main__":
	import sys
	print("Started main function")
	plt.ioff() #Dont just spit out plots/turn off interactive plotting, but keep them in memory TODO: Note that it is possible that this will break some things?? 

	# logging.basicConfig(format='[%(asctime)s %(pathname)s:%(lineno)d] %(levelname)s - %(message)s'
	# 				, level=logging.DEBUG) #With time
	formatter = logging.Formatter("[{pathname:>90s}:{lineno:<4}]  {levelname:<7s}   {message}", style='{')
	handler = logging.StreamHandler()
	handler.setFormatter(formatter)
	logging.basicConfig(
		handlers=[handler],
		level=logging.DEBUG) #Without time
	logging.getLogger('matplotlib').setLevel(logging.INFO)
	logging.getLogger('fontmanager').setLevel(logging.INFO)
	logging.getLogger('asyncua').setLevel(logging.WARN)
	# logging.getLogger('asyncua').setLevel(logging.WARN)
	logging.getLogger('numba').setLevel(logging.WARN)
	logging.getLogger('apscheduler').setLevel(logging.ERROR)

	parser = argparse.ArgumentParser(description='Tool arguments')
	parser.add_argument("--df_path", 
						help="path to initial plot dataframe (.pkl file)",
						default=None
					)

	#Argument for dark mode store true
	parser.add_argument("--dark_mode", 
						help="Turn on dark mode",
						action="store_true",
						default=False
					)

	parser.add_argument("--launch_on_monitor",
						help="Launch on monitor with given index",
						default=None,
						type=int
					)

	args = parser.parse_args()

	app = QtWidgets.QApplication(sys.argv)
	
	if args.dark_mode:
		app.setStyleSheet(open(Paths.DarkStyleSheetFilePath).read())
		plt.style.use('dark_background')

	opc_manager = None
	# with OPCManager as opc_manager:	
	# w = LiveViewWindow()
	w = MainWindow(graph_model_args={"df_path": args.df_path})
	if args.launch_on_monitor:
		#Launch on monitor with given index
		monitor = app.screens()[args.launch_on_monitor].geometry()
	else: #Otherwise launch on primary monitor
		monitor = QtGui.QGuiApplication.primaryScreen().geometry()

	w.setGeometry( int(0.05* monitor.width()), int(0.05* monitor.height()), int(0.9*monitor.width()), int(0.9*monitor.height()))
	w.move(monitor.left(), monitor.top())
	w.show()
	app.exec_()


	log.info("Reached end of main, exiting...")
	print("Done!")
	# import sys, traceback, threading
	# thread_names = {t.ident: t.name for t in threading.enumerate()}
	# log.debug(f"Running threads at end: {thread_names} - {sys._current_frames()}")
