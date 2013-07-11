# -*- coding: utf-8 -*-
# Author : xiaok
# 2011-08-01 16:43
import sys
import os
import codecs
import traceback

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import ui_main
import define
import log
import project_tree as pt
import table_data as td
from datawarehouse import *
import resource
import log

class OpenProject(QDialog):
  def __init__(self, parent=None):
    super(QDialog, self).__init__(parent)
    sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    self.selector = QPushButton(u'选择', self)
    self.dirInput = QLineEdit(self)
    self.nameInput = QLineEdit(self)
    layout = QHBoxLayout()
    layout.addWidget(QLabel(u'目录'))
    layout.addWidget(self.dirInput)
    layout.addWidget(self.selector)
    layout.addWidget(QLabel(u'名字'))
    layout.addWidget(self.nameInput)

    buttonBox = QDialogButtonBox(QDialogButtonBox.Ok
                                      | QDialogButtonBox.Cancel)

    layout.addWidget(buttonBox)
    self.setLayout(layout)
    self.connect(self.selector, SIGNAL("clicked()"), self.selectDir)
    self.connect(buttonBox, SIGNAL("accepted()"), self.selectDirOver)
    self.connect(buttonBox, SIGNAL("rejected()"), self.reject)
  def selectDir(self):
    print "select dir"
    proDir = QFileDialog.getExistingDirectory(self)
    self.dirInput.setText(proDir)

  def selectDirOver(self):
    print 'select dir over'
    self.hasSelect = self.nameInput.text().count() > 0 and \
      self.dirInput.text().count() > 0
    print self.hasSelect
    self.done(0)

  def reject(self):
    print 'reject'
    self.hasSelect = False
    self.done(0)

class MainWindow(QMainWindow, ui_main.Ui_MainWindow):
  def __init__(self, parent=None):
    super(MainWindow, self).__init__(parent)
    self.setupUi(self)
    self.fillAction(self.saveOneAction, self.saveOne)
    self.fillAction(self.saveAllAction, self.saveAll)
    self.fillAction(self.addProjectAction, self.addProject)
    self.fillAction(self.delProjectAction, self.delProject)
    self.fillAction(self.quitAppAction, self.quitApp)
    self.connect(self.treeWidget,
        SIGNAL("itemDoubleClicked(QTreeWidgetItem *,int)"),
        self.openTableFromTree)
    self.connect(self.treeWidget, SIGNAL("itemCollapsed(QTreeWidgetItem*)"),
        self.expandedTree)
    self.connect(self.treeWidget, SIGNAL("itemExpanded(QTreeWidgetItem*)"),
        self.collapsedTree)
    self.connect(self.treeWidget, SIGNAL("delFile"), self.delFileAct)
    self.connect(self.treeWidget, SIGNAL("addFile"), self.addFileAct)
    #self.connect(self.treeWidget, SIGNAL("delProject"), self.delFileAct)
    self.connect(self.treeWidget, SIGNAL("renameFile"), self.renameFileAct)
    self.connect(self.treeWidget, SIGNAL("removeProject"), self.removeProjectAct)
    self.connect(self.treeWidget, SIGNAL("RENAME_PROJECT"), self.rename_project)
    self.restoreSetting()
    QTimer.singleShot(0, self.loadOpenedFiles)

  def rename_project(self, root, new_name):
    index = self.projects.index(unicode(root))
    self.project_names[index] = new_name

  def saveOne(self):
    #TODO
    QMessageBox.about(self, QString("save one"), QString(""))

  def saveAll(self):
    #TODO
    QMessageBox.about(self, QString("save all"), QString(""))

  def findReplace(self):
    """
    removed
    """
    self.tabWidget.currentWidget().findReplace()

  def expandedTree(self, tw):
    tw.setIcon(0, QIcon(":fo.png"))

  def collapsedTree(self, tw):
    tw.setIcon(0, QIcon(":fc.png"))

  def addProject(self):
    openDlg = OpenProject(self)
    openDlg.exec_()
    if openDlg.hasSelect:
      project_name, project_dir = (unicode(openDlg.nameInput.text()), 
          unicode(openDlg.dirInput.text()))
    else:
    	return
    print project_dir , project_name

    if project_dir in self.projects:
      return

    if not project_dir:
    	return
    self.projects.append(unicode(project_dir))
    show_name = project_name if project_name else os.path.basename(project_dir)
    self.project_names.append(unicode(show_name))
    self.buildProjectTree(show_name, project_dir, self.treeWidget, project_dir)

  def removeProjectAct(self, root):
    index = self.projects.index(unicode(root))
    self.projects.pop(index)
    self.project_names.pop(index)
    if root in self.openTables:
      for path in self.openTables[root]:
        self.tabWidget.removeTab(self.getTabIndex(path, root))
      del self.openTables[root]
    if self.tabWidget.currentWidget():  
      self.statusBar().showMessage(self.tabWidget.currentWidget().path)

  def buildProjectTree(self, show_name, uProDir, tree, root):
    tw = pt.KProjectTreeItem(show_name, uProDir, tree, root)
    tw.setIcon(0, QIcon(":fc.png"))
    for f in os.listdir(uProDir):
      fp = uProDir + os.sep + f
      if os.path.isfile(fp):
        if f.endswith(define.DATA_FILE_SUF):
          twc = pt.KProjectTreeItem(f, fp, tw, root)
          twc.setIcon(0, QIcon(":f.png"))
      elif f != ".svn":
        self.buildProjectTree(f, fp, tw, root)
    tw.sortChildren(0, Qt.AscendingOrder)

  def delProject(self):
    self.treeWidget.delPro()

  def quitApp(self):
    #TODO
    QMessageBox.about(self, QString("quit app"), QString(""))

  def createTabWidget(self, path, root):
    wd = td.KDataTabWidget(path, root)
    return wd
    try:
      pass
    except Exception,e:
      log.error_log(u"%s" % e)
      log.error_log(traceback.format_exc().decode(define.CODEC))
      QMessageBox.information(self, u"打开文件错误", u"%s" % e)
      return None

  def openTableFromTree(self, item,idx):
    path = item.path
    root = item.root
    self.openTable(path, root)

  def getTabIndex(self, path, root):
    cnt = self.tabWidget.count()
    for idx in range(cnt):
      wgt = self.tabWidget.widget(idx)
      if wgt.isMe(path, root):
        return idx
    return -1

  def openTable(self, path, root):
    if os.path.isdir(path):
      return
    if root in self.openTables and path in self.openTables[root]:
      self.tabWidget.setCurrentIndex(self.getTabIndex(path, root))
      return
    tab = self.createTabWidget(path, root)
    if tab is None:
      return

    self.tabWidget.addTab(tab, self.project_names[self.projects.index(root)] +
        '|' + os.path.basename(path))
    self.tabWidget.setCurrentIndex(len(self.tabWidget) - 1)
    if not root in self.openTables:
      self.openTables[root] = [path]
    else:
      self.openTables[root].append(path)
    self.statusBar().showMessage(QString(path))
  
  def delFileAct(self, path, root):
    ts = self.openTables.get(root, None)
    nts = []
    ctidx = []
    if ts is not None:
      for op in ts:
        if op.startswith(path):
          KDataWarehouse.removeData(op[:-len(define.DATA_FILE_SUF)])
          ctidx.append(self.getTabIndex(op, root))
        else:
          nts.append(op)

    if len(nts) == 0:
      del self.openTables[root]
    else:
      self.openTables[root] = nts

    if len(ctidx) > 0:
      ctidx.sort()
      for idx in reversed(ctidx):
        if idx == -1:
          break
        self.tabWidget.emit(SIGNAL("tabCloseRequested(int)"), idx)

  def addFileAct(self, path, root):
    self.openTable(path, root)

  def toWHFilename(self, fn):
    return fn[:-len(define.DATA_FILE_SUF)]

  def renameFileAct(self, oldPath, newPath, root):
    ts = self.openTables.get(root, None)
    if ts is not None:
      if oldPath in ts:
        ts[ts.index(oldPath)] = newPath
        idx = self.getTabIndex(oldPath, root)
        if idx != -1:
          self.tabWidget.setTabText(idx,
            os.path.basename(newPath))
          self.tabWidget.widget(idx).updatePath(self.toWHFilename(newPath))
    KDataWarehouse.updateFilename(self.toWHFilename(newPath),
        self.toWHFilename(oldPath))

  def fillAction(self, action, slot, signal="triggered()"):
    if slot is not None:
      self.connect(action, SIGNAL(signal), slot)

  @pyqtSignature("int")
  def on_tabWidget_tabCloseRequested(self, index):
    """
    called when close tab page and delete opened-file
    """
    widget = self.tabWidget.widget(index)
    if widget.okToContinue():
      self.tabWidget.removeTab(index)
      KDataWarehouse.closeData(widget.path[:-len(define.DATA_FILE_SUF)])
      openedList = self.openTables.get(widget.root, None)
      if openedList is not None:
        if widget.path in openedList:
          del openedList[openedList.index(widget.path)]
          if not len(openedList):
            del self.openTables[widget.root]
  
  def read_projects(self, line):
    self.project_names = []
    self.projects = []
    for name_dir in line.split(','):
      name_dir_split_index = name_dir.find('|')
      if name_dir_split_index > 0:
        name, p_dir = name_dir[:name_dir_split_index], name_dir[name_dir_split_index+1:]
      else:
      	name, p_dir = os.path.basename(name_dir), name_dir
      self.project_names.append(name)
      self.projects.append(p_dir)

  def loadOpenedFiles(self):
    self.projects, self.project_names = [],[]
    self.openTables = {}
    appFile = self.appFile()
    if not os.path.exists(appFile):
      return
    try:
      fn = codecs.open(appFile, "r", define.CODEC)
      line = fn.readline()
      if len(line) > 1:
        self.read_projects(line[:-1])
      line = fn.readline()
      if len(line) > 1:
        openedTables = line[:-1].split(",")
        for ot in openedTables:
          eles = ot.split('"')
          paths = []
          for p in eles[1].split(';'):
            if os.path.exists(p): paths.append(p)
          self.openTables[eles[0]] = paths;
    except IOError, e:
      log.error_log("loading project error: %s\n", e)
    finally:
      fn.close()
    for name, pdir in zip(self.project_names, self.projects):
      self.buildProjectTree(unicode(name), unicode(pdir), self.treeWidget, unicode(pdir))

    for k in self.openTables:
      paths = self.openTables[k]
      project_name = self.project_names[self.projects.index(k)]
      for path in paths:
        tab = self.createTabWidget(path, k)
        if tab is None:
          continue
        self.tabWidget.addTab(tab, project_name + ':' + os.path.basename(path))
      QApplication.processEvents()
    for _, v in self.openTables.items():
      if v:
        self.statusBar().showMessage(v[0])
        break

  def appFile(self):
    return (os.path.dirname(os.path.realpath(__file__)) + os.sep + \
        define.APP_INFO_FILE)

  def storeOpenedFiles(self):
    fn = codecs.open(self.appFile(), "w", define.CODEC)
    if len(self.projects):
      fn.write(",".join('|'.join(z) for z in zip(self.project_names, self.projects)))
    fn.write('\n')
    if len(self.openTables):
      fn.write(",".join([unicode(k)+'"' +
        ";".join(self.openTables[k]) for k in self.openTables]))
    fn.write('\n')
    fn.close()

  def restoreSetting(self):
    settings = QSettings()
    self.recentFiles = settings.value("RecentFiles").toStringList()
    self.restoreGeometry(settings.value("MainWindow/Geometry").toByteArray())
    self.restoreState(settings.value("MainWindow/State").toByteArray())
    self.setWindowTitle(u"配置表工具")

  def closeEvent(self, event):
    if self.okToContinue():
      settings = QSettings()
      recentFiles = QVariant(self.recentFiles) \
          if self.recentFiles is not None and len(self.recentFiles) \
          else QVariant()
      settings.setValue("RecentFiles", recentFiles)
      settings.setValue("MainWindow/Geometry", QVariant(self.geometry()))
      settings.setValue("MainWindow/State", QVariant(self.saveState()))
      self.storeOpenedFiles()
    else:
      event.ignore()

  def okToContinue(self):
    for idx in range(len(self.tabWidget)):
      if not self.tabWidget.widget(idx).okToContinue():
        return False
    return True

app = QApplication(sys.argv)
form = MainWindow()
form.show()
app.exec_()
