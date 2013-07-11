# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'E:\python\qt\work\table_column.ui'
#
# Created: Mon Aug 01 16:35:10 2011
#      by: PyQt4 UI code generator 4.8.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(864, 622)
        self.widget = QtGui.QWidget(Form)
        self.widget.setGeometry(QtCore.QRect(10, 10, 258, 220))
        self.widget.setObjectName(_fromUtf8("widget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.widget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.addToolButton = QtGui.QToolButton(self.widget)
        self.addToolButton.setObjectName(_fromUtf8("addToolButton"))
        self.horizontalLayout.addWidget(self.addToolButton)
        self.delToolButton = QtGui.QToolButton(self.widget)
        self.delToolButton.setObjectName(_fromUtf8("delToolButton"))
        self.horizontalLayout.addWidget(self.delToolButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.tableView = QtGui.QTableView(self.widget)
        self.tableView.setObjectName(_fromUtf8("tableView"))
        self.verticalLayout.addWidget(self.tableView)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", u"Form", None, QtGui.QApplication.UnicodeUTF8))
        self.addToolButton.setText(QtGui.QApplication.translate("Form", u"添加", None, QtGui.QApplication.UnicodeUTF8))
        self.delToolButton.setText(QtGui.QApplication.translate("Form", u"删除", None, QtGui.QApplication.UnicodeUTF8))

