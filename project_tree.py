# -*- coding: utf-8 -*-
# Author : xiaok
# 2011-08-02 15:06
import os
import shutil

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import define
import resource

class KProjectTreeItem(QTreeWidgetItem):
  def __init__(self, text, path, parent, root, icon=None):
    super(KProjectTreeItem, self).__init__(parent, [unicode(text)])
    self.path = unicode(path)
    self.root = unicode(root)
    if icon is not None:
      self.setIcon(0, None)

class KProjectTree(QTreeWidget):
  def __init__(self, parent):
    super(KProjectTree, self).__init__(parent)

  def contextMenuEvent(self, event):
    item = self.currentItem()
    if item is None:
      return
    menu = self.createMenu(item.path, item.path == item.root)
    menu.exec_(event.globalPos())

  def createMenu(self, path, isRoot):
    menu = QMenu(self)
    if isRoot:
      delProAction = menu.addAction(u"删除工程")
      self.connect(delProAction, SIGNAL("triggered()"), self.delPro)
      delProAction = menu.addAction(u"移除工程")
      self.connect(delProAction, SIGNAL("triggered()"), self.removeProject)
      rename_project_action = menu.addAction(u'重命名')
      self.connect(rename_project_action, SIGNAL("triggered()"), self.rename_project)
    if isRoot or os.path.isdir(path):
      addFileFoldAction = menu.addAction(u"添加文件夹")
      self.connect(addFileFoldAction, SIGNAL("triggered()"), self.addFileFold)
      addFileAction = menu.addAction(u"添加配置表")
      self.connect(addFileAction, SIGNAL("triggered()"), self.addFile)
    delFileAction = menu.addAction(u"删除文件(夹)")
    if not isRoot:
      renameAction = menu.addAction(u"重命名")
      self.connect(renameAction, SIGNAL("triggered()"), self.renameFile)
    self.connect(delFileAction, SIGNAL("triggered()"), self.delFile)
    return menu

  def rename_project(self):
    project_name, ok = QInputDialog.getText(self, u"重命名", '',
        QLineEdit.Normal, self.currentItem().text(0))
    if not ok or not project_name:
      return
    project_name = unicode(project_name)
    project_name = project_name.replace(u'|', u'@')
    item = self.currentItem()
    item.setText(0, project_name)
    self.emit(SIGNAL("RENAME_PROJECT"), item.path, project_name)

  def delPro(self):
    item = self.currentItem()
    if QMessageBox.question(self, u"删除工程",
        QString(u"删除 %1").arg(os.path.basename(item.path)),
        QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
      return
    self.emit(SIGNAL("delPro"), item.path, item.root)
    shutil.rmtree(item.path)
    self.takeTopLevelItem(self.indexOfTopLevelItem(item))

  def removeProject(self):
    item = self.currentItem()
    if QMessageBox.question(self, u"移除工程",
        QString(u"移除 %1").arg(os.path.basename(item.path)),
        QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
      return
    self.emit(SIGNAL("removeProject"), item.path, item.root)
    self.takeTopLevelItem(self.indexOfTopLevelItem(item))

  def addFileFold(self):
    ffname, ok = QInputDialog.getText(self, u"新建文件夹", '')
    if ok:
      item = self.currentItem()
      npath = item.path + os.sep + ffname
      try:
        os.mkdir(npath)
        self.setCurrentItem(KProjectTreeItem(ffname, npath, item, item.root, QIcon(":f:png")))
      except OSError:
        QMessageBox.warning(self, u"新建文件夹",
                        u"文件%s已经存在" % ffname)
        return
    self.emit(SIGNAL("addFileFold"), npath, item.root)

  def addFile(self):
    fname, ok = QInputDialog.getText(self, u"添加配置表", '')
    if ok:
      item = self.currentItem()
      npath = item.path + os.sep + fname
      if os.path.exists(npath + define.HEADER_FILE_SUF):
        QMessageBox.warning(self, u"添加配置表",
                        u"文件%s已经存在" % fname)
        return
      f = open(unicode(npath + define.HEADER_FILE_SUF), 'w')
      item = KProjectTreeItem(fname + define.DATA_FILE_SUF,
          npath + define.DATA_FILE_SUF, 
          item, item.root)
      item.setIcon(0, QIcon(":f.png"))
      self.setCurrentItem(item)
      f.close()
      f = open(unicode(npath + define.DATA_FILE_SUF), 'w')
      f.close()
    self.emit(SIGNAL("addFile"), item.path, item.root)

  def delFile(self):
    item = self.currentItem()
    delPath = item.path
    if QMessageBox.question(self, u"删除文件",
        QString(u"删除 %1").arg(os.path.basename(delPath)),
        QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
      return
    try:
      if os.path.isfile(delPath):
        os.remove(delPath)
        os.remove(delPath[:-len(define.DATA_FILE_SUF)] + define.HEADER_FILE_SUF)
      else:
        shutil.rmtree(delPath)
      item.parent().removeChild(item)
      self.emit(SIGNAL("delFile"), delPath, item.root)
    except IOError, e:
      QMessageBox.information(u"删除文件错误", "%s" % e, self)
        
  def renameFile(self):
    fname, ok = QInputDialog.getText(self, u"重命名", '')
    if not ok:
      return
    item = self.currentItem()
    npath = unicode(os.path.dirname(item.path) + os.sep + fname +
        define.HEADER_FILE_SUF)
    if fname != os.path.basename(item.path) and os.path.exists(npath):
      QMessageBox.warning(self, u"重命名",
                     u"文件%s已经存在" % fname)
      return
    os.renames(item.path[:-len(define.DATA_FILE_SUF)] + define.HEADER_FILE_SUF,
        npath)
    npath = npath[:-len(define.DATA_FILE_SUF)] + define.DATA_FILE_SUF
    os.renames(item.path, npath)
    item.setText(0, fname + define.DATA_FILE_SUF)
    self.emit(SIGNAL("renameFile"), item.path, npath, item.root)
    item.path = npath
