# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'E:\python\qt\work\main.ui'
#
# Created: Mon Aug 01 16:40:49 2011
#      by: PyQt4 UI code generator 4.8.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

import project_tree as pt

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(1120, 726)
        self.splitter = QtGui.QSplitter()
        self.splitter.setGeometry(QtCore.QRect(-20, 0, 1131, 671))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.splitter.setAutoFillBackground(True)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.treeWidget = pt.KProjectTree(self.splitter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(3)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.treeWidget.sizePolicy().hasHeightForWidth())
        self.treeWidget.setSizePolicy(sizePolicy)
        self.treeWidget.setMinimumSize(QtCore.QSize(200, 671))
        self.treeWidget.setObjectName(_fromUtf8("treeWidget"))
        self.treeWidget.headerItem().setText(0, _fromUtf8(u"项目"))
        self.treeWidget.setGeometry(0, 0, 200, 671)
        self.tabWidget = QtGui.QTabWidget(self.splitter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(7)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tabWidget.setMinimumSize(QtCore.QSize(926, 671))
        self.tabWidget.setGeometry(0, 0, 926, 671)
        self.tabWidget.setTabsClosable(True)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 3)
        MainWindow.setCentralWidget(self.splitter)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1120, 19))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.fileMenu = QtGui.QMenu(self.menubar)
        self.fileMenu.setObjectName(_fromUtf8("fileMenu"))
        self.editMenu = QtGui.QMenu(self.menubar)
        self.editMenu.setObjectName(_fromUtf8("editMenu"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        #self.toolBar = QtGui.QToolBar(MainWindow)
        #self.toolBar.setObjectName(_fromUtf8("toolBar"))
        #MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.addProjectAction = QtGui.QAction(MainWindow)
        self.addProjectAction.setObjectName(_fromUtf8("addProjectAction"))
        self.delProjectAction = QtGui.QAction(MainWindow)
        self.delProjectAction.setObjectName(_fromUtf8("delProjectAction"))
        self.quitAppAction = QtGui.QAction(MainWindow)
        self.quitAppAction.setObjectName(_fromUtf8("quitAppAction"))
        self.saveOneAction = QtGui.QAction(MainWindow)
        self.saveOneAction.setObjectName(_fromUtf8("saveOneAction"))
        self.saveAllAction = QtGui.QAction(MainWindow)
        self.saveAllAction.setObjectName(_fromUtf8("saveAllAction"))
        self.cpAction = QtGui.QAction(MainWindow)
        self.cpAction.setObjectName(_fromUtf8("cpAction"))
        self.cutAction = QtGui.QAction(MainWindow)
        self.cutAction.setObjectName(_fromUtf8("cutAction"))
        self.pasteAction = QtGui.QAction(MainWindow)
        self.pasteAction.setObjectName(_fromUtf8("pasteAction"))
        self.fileMenu.addAction(self.addProjectAction)
        self.fileMenu.addAction(self.delProjectAction)
        self.fileMenu.addAction(self.quitAppAction)
        self.editMenu.addAction(self.saveOneAction)
        self.editMenu.addAction(self.saveAllAction)
        self.menubar.addAction(self.fileMenu.menuAction())
        self.menubar.addAction(self.editMenu.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", u"配置表工具", None, QtGui.QApplication.UnicodeUTF8))
        self.fileMenu.setTitle(QtGui.QApplication.translate("MainWindow", u"文件", None, QtGui.QApplication.UnicodeUTF8))
        self.editMenu.setTitle(QtGui.QApplication.translate("MainWindow", u"编辑", None, QtGui.QApplication.UnicodeUTF8))
        #self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))
        self.addProjectAction.setText(QtGui.QApplication.translate("MainWindow", u"添加项目", None, QtGui.QApplication.UnicodeUTF8))
        self.delProjectAction.setText(QtGui.QApplication.translate("MainWindow", u"删除项目", None, QtGui.QApplication.UnicodeUTF8))
        self.quitAppAction.setText(QtGui.QApplication.translate("MainWindow", u"退出", None, QtGui.QApplication.UnicodeUTF8))
        self.saveOneAction.setText(QtGui.QApplication.translate("MainWindow", u"保存", None, QtGui.QApplication.UnicodeUTF8))
        self.saveAllAction.setText(QtGui.QApplication.translate("MainWindow", u"保存全部", None, QtGui.QApplication.UnicodeUTF8))

