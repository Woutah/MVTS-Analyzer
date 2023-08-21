# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'rename_label_window.ui'
##
## Created by: Qt User Interface Compiler version 6.5.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QLabel,
    QLayout, QMainWindow, QMenuBar, QPushButton,
    QSizePolicy, QSpacerItem, QStatusBar, QVBoxLayout,
    QWidget)
import mvts_analyzer.res.app_resources_rc

class Ui_RenameLabelWindow(object):
    def setupUi(self, RenameLabelWindow):
        if not RenameLabelWindow.objectName():
            RenameLabelWindow.setObjectName(u"RenameLabelWindow")
        RenameLabelWindow.resize(719, 276)
        icon = QIcon()
        icon.addFile(u":/Icons/icons/Tango Icons/mimetypes/x-office-document-template.svg", QSize(), QIcon.Normal, QIcon.Off)
        RenameLabelWindow.setWindowIcon(icon)
        self.centralwidget = QWidget(RenameLabelWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_2 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setSizeConstraint(QLayout.SetMinimumSize)
        self.returnMsgLabel = QLabel(self.centralwidget)
        self.returnMsgLabel.setObjectName(u"returnMsgLabel")
        self.returnMsgLabel.setEnabled(False)
        self.returnMsgLabel.setAlignment(Qt.AlignBottom|Qt.AlignLeading|Qt.AlignLeft)

        self.verticalLayout_2.addWidget(self.returnMsgLabel)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")

        self.horizontalLayout_3.addWidget(self.label)

        self.columnOptionsCombobox = QComboBox(self.centralwidget)
        self.columnOptionsCombobox.setObjectName(u"columnOptionsCombobox")

        self.horizontalLayout_3.addWidget(self.columnOptionsCombobox)


        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.renameToVLayout = QVBoxLayout()
        self.renameToVLayout.setObjectName(u"renameToVLayout")
        self.renameLabel = QLabel(self.centralwidget)
        self.renameLabel.setObjectName(u"renameLabel")
        self.renameLabel.setAlignment(Qt.AlignCenter)

        self.renameToVLayout.addWidget(self.renameLabel)

        self.fromCombobox = QComboBox(self.centralwidget)
        self.fromCombobox.setObjectName(u"fromCombobox")
        self.fromCombobox.setEnabled(False)

        self.renameToVLayout.addWidget(self.fromCombobox)

        self.toLabel = QLabel(self.centralwidget)
        self.toLabel.setObjectName(u"toLabel")
        self.toLabel.setAlignment(Qt.AlignCenter)

        self.renameToVLayout.addWidget(self.toLabel)

        self.toComboBox = QComboBox(self.centralwidget)
        self.toComboBox.setObjectName(u"toComboBox")
        self.toComboBox.setEditable(True)

        self.renameToVLayout.addWidget(self.toComboBox)


        self.verticalLayout_2.addLayout(self.renameToVLayout)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(-1, 30, -1, 0)
        self.renameBtn = QPushButton(self.centralwidget)
        self.renameBtn.setObjectName(u"renameBtn")

        self.horizontalLayout.addWidget(self.renameBtn)

        self.cancelBtn = QPushButton(self.centralwidget)
        self.cancelBtn.setObjectName(u"cancelBtn")

        self.horizontalLayout.addWidget(self.cancelBtn)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.verticalLayout_2.setStretch(3, 1)
        RenameLabelWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(RenameLabelWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setEnabled(False)
        self.menubar.setGeometry(QRect(0, 0, 719, 22))
        RenameLabelWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(RenameLabelWindow)
        self.statusbar.setObjectName(u"statusbar")
        self.statusbar.setEnabled(False)
        RenameLabelWindow.setStatusBar(self.statusbar)

        self.retranslateUi(RenameLabelWindow)

        QMetaObject.connectSlotsByName(RenameLabelWindow)
    # setupUi

    def retranslateUi(self, RenameLabelWindow):
        RenameLabelWindow.setWindowTitle(QCoreApplication.translate("RenameLabelWindow", u"Rename Label", None))
        self.returnMsgLabel.setText("")
        self.label.setText(QCoreApplication.translate("RenameLabelWindow", u"Column", None))
        self.renameLabel.setText(QCoreApplication.translate("RenameLabelWindow", u"Rename:", None))
        self.toLabel.setText(QCoreApplication.translate("RenameLabelWindow", u"To:", None))
        self.renameBtn.setText(QCoreApplication.translate("RenameLabelWindow", u"Rename", None))
        self.cancelBtn.setText(QCoreApplication.translate("RenameLabelWindow", u"Cancel", None))
    # retranslateUi

