# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'apply_python_window.ui'
##
## Created by: Qt User Interface Compiler version 6.5.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QLayout,
    QMainWindow, QMenu, QMenuBar, QPushButton,
    QSizePolicy, QSpacerItem, QStatusBar, QTextEdit,
    QVBoxLayout, QWidget)
import mvts_analyzer.res.app_resources_rc

class Ui_ApplyPythonWindow(object):
    def setupUi(self, ApplyPythonWindow):
        if not ApplyPythonWindow.objectName():
            ApplyPythonWindow.setObjectName(u"ApplyPythonWindow")
        ApplyPythonWindow.resize(1065, 788)
        icon = QIcon()
        icon.addFile(u":/Icons/icons/mainwin.ico", QSize(), QIcon.Normal, QIcon.Off)
        ApplyPythonWindow.setWindowIcon(icon)
        self.actionSaveAs = QAction(ApplyPythonWindow)
        self.actionSaveAs.setObjectName(u"actionSaveAs")
        icon1 = QIcon()
        icon1.addFile(u":/Icons/icons/Tango Icons/actions/document-save-as.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionSaveAs.setIcon(icon1)
        self.actionOpenFromFile = QAction(ApplyPythonWindow)
        self.actionOpenFromFile.setObjectName(u"actionOpenFromFile")
        self.actionSave = QAction(ApplyPythonWindow)
        self.actionSave.setObjectName(u"actionSave")
        self.actionSave.setEnabled(True)
        icon2 = QIcon()
        icon2.addFile(u":/Icons/icons/Tango Icons/actions/document-save.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionSave.setIcon(icon2)
        self.actionactionExecutePythonCode = QAction(ApplyPythonWindow)
        self.actionactionExecutePythonCode.setObjectName(u"actionactionExecutePythonCode")
        self.centralwidget = QWidget(ApplyPythonWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setEnabled(True)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setSizeIncrement(QSize(0, 0))
        self.verticalLayout_2 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setItalic(True)
        self.label.setFont(font)

        self.verticalLayout_2.addWidget(self.label)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.pythonCodeTextEdit = QTextEdit(self.centralwidget)
        self.pythonCodeTextEdit.setObjectName(u"pythonCodeTextEdit")

        self.verticalLayout.addWidget(self.pythonCodeTextEdit)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(278, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.ExecuteButton = QPushButton(self.centralwidget)
        self.ExecuteButton.setObjectName(u"ExecuteButton")
        self.ExecuteButton.setLocale(QLocale(QLocale.English, QLocale.Netherlands))

        self.horizontalLayout.addWidget(self.ExecuteButton)

        self.ExecuteAndUpdateButton = QPushButton(self.centralwidget)
        self.ExecuteAndUpdateButton.setObjectName(u"ExecuteAndUpdateButton")

        self.horizontalLayout.addWidget(self.ExecuteAndUpdateButton)

        self.CancelButton = QPushButton(self.centralwidget)
        self.CancelButton.setObjectName(u"CancelButton")

        self.horizontalLayout.addWidget(self.CancelButton)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.verticalLayout_2.addLayout(self.verticalLayout)

        ApplyPythonWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(ApplyPythonWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1065, 22))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        ApplyPythonWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(ApplyPythonWindow)
        self.statusbar.setObjectName(u"statusbar")
        ApplyPythonWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSaveAs)
        self.menuFile.addAction(self.actionOpenFromFile)

        self.retranslateUi(ApplyPythonWindow)

        QMetaObject.connectSlotsByName(ApplyPythonWindow)
    # setupUi

    def retranslateUi(self, ApplyPythonWindow):
        ApplyPythonWindow.setWindowTitle(QCoreApplication.translate("ApplyPythonWindow", u"Apply Python Code", None))
        self.actionSaveAs.setText(QCoreApplication.translate("ApplyPythonWindow", u"Save as...", None))
#if QT_CONFIG(shortcut)
        self.actionSaveAs.setShortcut(QCoreApplication.translate("ApplyPythonWindow", u"Ctrl+Shift+S", None))
#endif // QT_CONFIG(shortcut)
        self.actionOpenFromFile.setText(QCoreApplication.translate("ApplyPythonWindow", u"Open...", None))
#if QT_CONFIG(tooltip)
        self.actionOpenFromFile.setToolTip(QCoreApplication.translate("ApplyPythonWindow", u"Open from file", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.actionOpenFromFile.setShortcut(QCoreApplication.translate("ApplyPythonWindow", u"Ctrl+O", None))
#endif // QT_CONFIG(shortcut)
        self.actionSave.setText(QCoreApplication.translate("ApplyPythonWindow", u"Save", None))
#if QT_CONFIG(shortcut)
        self.actionSave.setShortcut(QCoreApplication.translate("ApplyPythonWindow", u"Ctrl+S", None))
#endif // QT_CONFIG(shortcut)
        self.actionactionExecutePythonCode.setText(QCoreApplication.translate("ApplyPythonWindow", u"actionExecutePythonCode", None))
        self.label.setText(QCoreApplication.translate("ApplyPythonWindow", u"Note: the dataframe is accesible in this window via the \"model\" variable (.e.g. model.df, or model.selection)", None))
        self.ExecuteButton.setText(QCoreApplication.translate("ApplyPythonWindow", u"Execute", None))
        self.ExecuteAndUpdateButton.setText(QCoreApplication.translate("ApplyPythonWindow", u"Execute + Update", None))
        self.CancelButton.setText(QCoreApplication.translate("ApplyPythonWindow", u"Cancel", None))
        self.menuFile.setTitle(QCoreApplication.translate("ApplyPythonWindow", u"File", None))
    # retranslateUi

