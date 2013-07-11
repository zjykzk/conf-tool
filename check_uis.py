# -*- coding: utf-8 -*-
# Author : zenk
# 2012-04-16 11:27
import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import genericdelegates as gd
import check_utils as cu

class ArrayLengthCheck(QDialog):
  def __init__(self, checkedHeaders, checkedDatas, parent=None):
    super(ArrayLengthCheck, self).__init__(parent)
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
    #delegate.insertColumnDelegate(0, QItemDelegate())
    self.tableView.setItemDelegate(delegate)
    self.tableView.setMouseTracking(True)
    self.tableView.setAlternatingRowColors(True)
    self.model = ArrayLengthCheckModel()
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
    headIdxes = [self.__checkedHeaders.index(headName) \
        for headName in self.model.checkingHeader()]
    isOk, rowIdx, columnIdx = cu.checkArrayLength(\
        [self.__checkedDatas[idx] for idx in headIdxes])
    if not isOk:
      QMessageBox.information(self, u"错误", \
          u"第%d行,字段%s，错啦:(" % (rowIdx + 1, self.__checkedHeaders[ \
            headIdxes[columnIdx]]), \
          QMessageBox.Ok)
    else:
      QMessageBox.information(self, u"It's OK", \
          u"It's OK :D", QMessageBox.Ok)

class ArrayLengthCheckModel(QAbstractTableModel):
  def __init__(self, parent=None):
    super(ArrayLengthCheckModel, self).__init__(parent)
    self.__checkedElements = []

  def checkingHeader(self):
    return self.__checkedElements

  def rowCount(self, index=QModelIndex()):
    return len(self.__checkedElements)

  def columnCount(self, index=QModelIndex()):
    return 1
  
  def headerCount(self, index=QModelIndex()):
    return 1

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
      e = self.__checkedElements[index.row()]
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
    return QVariant(int(section + 1))

  def setData(self, index, value, role=Qt.EditRole):
    if index.isValid() and 0 <= index.row() < len(self.__checkedElements):
      if not value:
        return False
      strData = unicode(value.toString())
      self.__checkedElements[index.row()] = value
      return True
    return False

  def insertRows(self, position, rows = 1, rowList = None, index=QModelIndex()):
    self.beginInsertRows(QModelIndex(), position,
        position + rows - 1)
    self.__checkedElements.append("")
    self.endInsertRows()
    return True

  def removeRows(self, position, rows = 1, index = QModelIndex()):
    self.beginRemoveRows(QModelIndex(), position,
        position + rows - 1)
    del self.__checkedElements[position : position + rows]
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

if __name__ == "__main__":
  app = QApplication(sys.argv)
  widgt = ArrayLengthCheck(["1", "2", "3"],[["1"],["2"],["3"]])
  widgt.show()
  app.exec_()
