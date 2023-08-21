# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'merge_column_window.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QHBoxLayout,
    QLabel, QLayout, QMainWindow, QMenuBar,
    QPushButton, QSizePolicy, QSpacerItem, QStatusBar,
    QVBoxLayout, QWidget)
import mvts_analyzer.res.app_resources_rc

class Ui_MergeColumnWindow(object):
    def setupUi(self, MergeColumnWindow):
        if not MergeColumnWindow.objectName():
            MergeColumnWindow.setObjectName(u"MergeColumnWindow")
        MergeColumnWindow.resize(1016, 261)
        icon = QIcon()
        icon.addFile(u":/Icons/icons/Tango Icons/actions/go-down.svg", QSize(), QIcon.Normal, QIcon.Off)
        MergeColumnWindow.setWindowIcon(icon)
        self.centralwidget = QWidget(MergeColumnWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.verticalLayout_2 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setSizeConstraint(QLayout.SetMinimumSize)
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setSizeConstraint(QLayout.SetMinimumSize)
        self.returnMsgLabel = QLabel(self.centralwidget)
        self.returnMsgLabel.setObjectName(u"returnMsgLabel")
        self.returnMsgLabel.setEnabled(False)
        self.returnMsgLabel.setAlignment(Qt.AlignBottom|Qt.AlignLeading|Qt.AlignLeft)

        self.verticalLayout_3.addWidget(self.returnMsgLabel)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")

        self.horizontalLayout_3.addWidget(self.label)

        self.sourceColumnCombobox = QComboBox(self.centralwidget)
        self.sourceColumnCombobox.setObjectName(u"sourceColumnCombobox")

        self.horizontalLayout_3.addWidget(self.sourceColumnCombobox)


        self.verticalLayout_3.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.toLabel = QLabel(self.centralwidget)
        self.toLabel.setObjectName(u"toLabel")
        self.toLabel.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.horizontalLayout_2.addWidget(self.toLabel)

        self.destinationColumnCombobox = QComboBox(self.centralwidget)
        self.destinationColumnCombobox.setObjectName(u"destinationColumnCombobox")
        self.destinationColumnCombobox.setEnabled(True)
        self.destinationColumnCombobox.setEditable(True)

        self.horizontalLayout_2.addWidget(self.destinationColumnCombobox)


        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

        self.Mergemode = QHBoxLayout()
        self.Mergemode.setObjectName(u"Mergemode")
        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")

        self.Mergemode.addWidget(self.label_2)

        self.mergeModeComboBox = QComboBox(self.centralwidget)
        self.mergeModeComboBox.addItem("")
        self.mergeModeComboBox.addItem("")
        self.mergeModeComboBox.addItem("")
        self.mergeModeComboBox.setObjectName(u"mergeModeComboBox")
        self.mergeModeComboBox.setEditable(False)

        self.Mergemode.addWidget(self.mergeModeComboBox)


        self.verticalLayout_3.addLayout(self.Mergemode)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_4 = QLabel(self.centralwidget)
        self.label_4.setObjectName(u"label_4")

        self.horizontalLayout_4.addWidget(self.label_4)

        self.newTypeComboBox = QComboBox(self.centralwidget)
        self.newTypeComboBox.setObjectName(u"newTypeComboBox")
        self.newTypeComboBox.setEditable(False)

        self.horizontalLayout_4.addWidget(self.newTypeComboBox)


        self.verticalLayout_3.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_3 = QLabel(self.centralwidget)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_5.addWidget(self.label_3)

        self.preserveSourceCheckBox = QCheckBox(self.centralwidget)
        self.preserveSourceCheckBox.setObjectName(u"preserveSourceCheckBox")

        self.horizontalLayout_5.addWidget(self.preserveSourceCheckBox)


        self.verticalLayout_3.addLayout(self.horizontalLayout_5)

        self.verticalSpacer = QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)

        self.verticalLayout_3.addItem(self.verticalSpacer)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(-1, 0, -1, 0)
        self.renameBtn = QPushButton(self.centralwidget)
        self.renameBtn.setObjectName(u"renameBtn")

        self.horizontalLayout.addWidget(self.renameBtn)

        self.cancelBtn = QPushButton(self.centralwidget)
        self.cancelBtn.setObjectName(u"cancelBtn")

        self.horizontalLayout.addWidget(self.cancelBtn)


        self.verticalLayout_3.addLayout(self.horizontalLayout)


        self.verticalLayout_2.addLayout(self.verticalLayout_3)

        MergeColumnWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MergeColumnWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setEnabled(False)
        self.menubar.setGeometry(QRect(0, 0, 1016, 22))
        MergeColumnWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MergeColumnWindow)
        self.statusbar.setObjectName(u"statusbar")
        self.statusbar.setEnabled(False)
        MergeColumnWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MergeColumnWindow)

        QMetaObject.connectSlotsByName(MergeColumnWindow)
    # setupUi

    def retranslateUi(self, MergeColumnWindow):
        MergeColumnWindow.setWindowTitle(QCoreApplication.translate("MergeColumnWindow", u"Column Editor", None))
        self.returnMsgLabel.setText("")
        self.label.setText(QCoreApplication.translate("MergeColumnWindow", u"Source Column:", None))
#if QT_CONFIG(tooltip)
        self.toLabel.setToolTip(QCoreApplication.translate("MergeColumnWindow", u"Merging into \"None\" will remove the column entirely", None))
#endif // QT_CONFIG(tooltip)
        self.toLabel.setText(QCoreApplication.translate("MergeColumnWindow", u"Destination Column:", None))
#if QT_CONFIG(tooltip)
        self.label_2.setToolTip(QCoreApplication.translate("MergeColumnWindow", u"If column already exists, this determines what merging mode is used, source priority means that for every timestamp, if both source and destination contain a label, source will overwrite destination. Idem but other way around for Destination priority. Overwrite all will discard the destination column (if it exists) and replace it by the source column.", None))
#endif // QT_CONFIG(tooltip)
        self.label_2.setText(QCoreApplication.translate("MergeColumnWindow", u"Merge mode:", None))
        self.mergeModeComboBox.setItemText(0, QCoreApplication.translate("MergeColumnWindow", u"Source priority", None))
        self.mergeModeComboBox.setItemText(1, QCoreApplication.translate("MergeColumnWindow", u"Destination priority", None))
        self.mergeModeComboBox.setItemText(2, QCoreApplication.translate("MergeColumnWindow", u"Overwrite entirely", None))

        self.label_4.setText(QCoreApplication.translate("MergeColumnWindow", u"New column type:", None))
#if QT_CONFIG(tooltip)
        self.label_3.setToolTip(QCoreApplication.translate("MergeColumnWindow", u"Whether source column should be preserved, by default, it is deleted after mergin", None))
#endif // QT_CONFIG(tooltip)
        self.label_3.setText(QCoreApplication.translate("MergeColumnWindow", u"Preserve source:", None))
        self.preserveSourceCheckBox.setText("")
        self.renameBtn.setText(QCoreApplication.translate("MergeColumnWindow", u"Merge", None))
        self.cancelBtn.setText(QCoreApplication.translate("MergeColumnWindow", u"Cancel", None))
    # retranslateUi

