# -*- coding: utf-8 -*-
# Author : zenk
# 2012-05-26 17:28
import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import genericdelegates as gd
import check_utils as cu

class ResCheck(QDialog):
  def __init__(self, checkedHeaders, checkedDatas, parent=None):
    super(ResCheck, self).__init__(parent)
    self.__checkedDatas = checkedDatas
    self.__checkedHeaders = checkedHeaders

    addButton = QPushButton(u'添加', self)
    delButton = QPushButton(u'删除', self)
    checkButton = QPushButton(u'检查', self)
    self.tableView = QTableView()
    self.tableView.setSelectionMode(QTableView.ContiguousSelection)
    self.tableView.setSelectionBehavior(QTableView.SelectItems)
    delegate = gd.GenericDelegate(self)
    delegate.insertColumnDelegate(0, ComboDelegate(self.__checkedHeaders))
    delegate.insertColumnDelegate(1, DirectoryDelegate())
    self.tableView.setItemDelegate(delegate)
    self.tableView.setMouseTracking(True)
    self.tableView.setAlternatingRowColors(True)
    self.model = ResCheckModel()
    self.tableView.setModel(self.model)
    self.tableView.resizeColumnsToContents()
    self.tableView.resizeRowsToContents()

    buttonLayout = QHBoxLayout()
    buttonLayout.addWidget(addButton)
    buttonLayout.addWidget(delButton)
    buttonLayout.addWidget(checkButton)
    buttonLayout.addStretch()

    mainLayout = QVBoxLayout()
    mainLayout.addWidget(self.tableView)
    mainLayout.addLayout(buttonLayout)
    self.setLayout(mainLayout)

    self.connect(addButton, SIGNAL("clicked()"), self.addOne)
    self.connect(delButton, SIGNAL("clicked()"), self.delOne)
    self.connect(checkButton, SIGNAL("clicked()"), self.check)

  def selectIndexFile(self):
    self.indexFilePath.setText(QFileDialog.getOpenFileName(self, u"选择索引文件"))

  def addOne(self):
    row = self.model.rowCount()
    self.model.insertRows(row)
    index = self.model.index(row, 0)
    self.tableView.setCurrentIndex(index)
    self.tableView.edit(index)
    self.tableView.setColumnWidth(0, 128)

  def delOne(self):
    indexes = self.tableView.selectedIndexes()
    if not len(indexes):
      return
    rowSet = set()
    for idx in indexes:
      rowSet.add(idx.row())
    self.model.removeRows(min(rowSet), len(rowSet))

  def check(self):
    '''
    检查资源文件，只检查与配置表中prefab相对应的bundle文件是否存在
    '''
    headIdxes = [self.__checkedHeaders.index(headName) \
        for headName in self.model.checkingHeader()]
    if not headIdxes:
      return

    checkedFiles = []
    for headIndex in headIdxes:
      data = self.__checkedDatas[headIndex]
      if not data:
        continue

      checkedFiles.append([e.replace("prefab", "bundle") for d in data
      for e in d.split(',')])

    rowIndex, notexistres, notexistd = cu.checkResource(checkedFiles,\
        self.model.checkingDirs())
    if rowIndex > 0:
      QMessageBox.information(self, u"错误", \
          "\n".join([u"%s中不存在以下文件%s" % (d, " ".join(r)) \
        for r, d in zip(notexistres, notexistd)]),\
          QMessageBox.Ok)
    else:
      QMessageBox.information(self, u"It's OK", u"It's OK :D", QMessageBox.Ok)

class ResCheckModel(QAbstractTableModel):
  def __init__(self, parent=None):
    super(ResCheckModel, self).__init__(parent)
    self.__checkedElements = []
    self.__checkedDirs = []

  def checkingHeader(self):
    return self.__checkedElements

  def checkingDirs(self):
    return self.__checkedDirs

  def rowCount(self, index=QModelIndex()):
    return len(self.__checkedElements)

  def columnCount(self, index=QModelIndex()):
    return 2
  
  def headerCount(self, index=QModelIndex()):
    return 2

  def flags(self, index):
    if not index.isValid():
      return Qt.ItemIsEnabled
    return Qt.ItemFlags(QAbstractTableModel.flags(self, index) |
        Qt.ItemIsEditable)

  def data(self, index, role=Qt.DisplayRole):
    if not index.isValid() or \
        not (0 <= index.row() < len(self.__checkedElements)):
          return QVariant()
    if role == Qt.DisplayRole:
      column = index.column()
      row = index.row()
      e = self.__checkedElements[row] if column==0 else self.__checkedDirs[row]
      return QVariant(e)
    return QVariant()

  def headerData(self, section, orientation, role=Qt.DisplayRole):
    if role == Qt.TextAlignmentRole:
      if orientation == Qt.Horizontal:
        return QVariant(int(Qt.AlignLeft | Qt.AlignVCenter))
      return QVariant(int(Qt.AlignRight | Qt.AlignVCenter))
    if role != Qt.DisplayRole:
      return QVariant()
    if orientation == Qt.Horizontal:
      if section == 0:
        return QVariant(u'字段名称')
      elif section == 1:
        return QVariant(u'资源目录')
    return QVariant(int(section + 1))

  def setData(self, index, value, role=Qt.EditRole):
    if index.isValid() and 0 <= index.row() < len(self.__checkedElements):
      if not value:
        return False
      strData = unicode(value.toString())
      column = index.column()
      if column == 0:
        self.__checkedElements[index.row()] = strData
      elif column == 1:
        self.__checkedDirs[index.row()] = strData
      return True
    return False

  def insertRows(self, position, rows = 1, rowList = None, index=QModelIndex()):
    self.beginInsertRows(QModelIndex(), position,
        position + rows - 1)
    self.__checkedElements.append("")
    self.__checkedDirs.append("")
    self.endInsertRows()
    return True

  def removeRows(self, position, rows = 1, index = QModelIndex()):
    self.beginRemoveRows(QModelIndex(), position,
        position + rows - 1)
    del self.__checkedElements[position : position + rows]
    del self.__checkedDirs[position : position + rows]
    self.endRemoveRows()
    return True

  def createEditor(self, parent, option, index):
    lineedit = QLineEdit(parent)
    return lineedit

  def setEditorData(self, editor, index):
    value = index.model().data(index, Qt.DisplayRole).toString()
    editor.setText(value)

class ComboDelegate(QItemDelegate):
  def __init__(self, items=[], parent=None):
    super(ComboDelegate, self).__init__(parent)
    self.__items = items

  def createEditor(self, parent, option, index):
    comboEditor = QComboBox(parent)
    for item in self.__items:
      comboEditor.addItem(item)
    comboEditor.setCurrentIndex(0)
    return comboEditor

  def setEditorData(self, editor, index):
    value = index.model().data(index, Qt.DisplayRole).toString()
    editor.setCurrentIndex(editor.findText(value))
    
  def setModelData(self, editor, model, index):
    model.setData(index, QVariant(editor.currentText()))

class DirectoryDelegate(QItemDelegate):
  def __init__(self, parent=None):
    super(DirectoryDelegate, self).__init__(parent)

  def createEditor(self, parent, option, index):
    editor = QLineEdit(parent)
    return editor

  def setEditorData(self, editor, index):
    value = index.model().data(index, Qt.DisplayRole).toString()
    editor.setText(value)
    
  def setModelData(self, editor, model, index):
    model.setData(index, QVariant(editor.text()))

if __name__ == "__main__":
  app = QApplication(sys.argv)
  widgt = ResCheck(["library.pdf,whatsnew.pdf"], ["E:\doc\python2.6-doc"])
  widgt.setFixedSize(400, 300)
  widgt.show()
  app.exec_()
