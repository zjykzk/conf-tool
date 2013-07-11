# -*- coding: utf-8 -*-
# Author : xiaok
# 2011-08-03 11:05
import os
import traceback

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import define
from header_delegate import *
import data_codec as dc
import refeditor
from datawarehouse import *
from findandreplacedlg import *
import log

class KHeaderTableWidget(QWidget):
  def __init__(self, projectDir, filename=None, parent=None):
    super(KHeaderTableWidget, self).__init__(parent)
    self.__filename = filename
    self.__dirty = False
    self.__parent = parent

    addButton = QPushButton(u'添加', self)
    delButton = QPushButton(u'删除', self)
    upButton = QPushButton(u'向上', self)
    downButton = QPushButton(u'向下', self)
    self.saveButton = QPushButton(u'保存', self)    
    self.discardButton = QPushButton(u'放弃', self)
    self.discardButton.setEnabled(False)
    self.saveButton.setEnabled(False)
    self.tableView = QTableView()
    self.tableView.setSelectionMode(QTableView.ContiguousSelection)
    self.tableView.setSelectionBehavior(QTableView.SelectItems)
    delegate = gd.GenericDelegate(self)
    delegate.insertColumnDelegate(define.NAME, KNameColumnDelegate())
    delegate.insertColumnDelegate(define.DATATYPE, KDataTypeColumnDelegate())
    delegate.insertColumnDelegate(define.CS, KCSColumnDelegate())
    delegate.insertColumnDelegate(define.ISUNIQUIE, KIsUniqueColumnDelegate())
    delegate.insertColumnDelegate(define.ALLOWEMPTY, KAllowEmptyColumnDelegate())
    delegate.insertColumnDelegate(define.IS_I18N, I18NEmptyColumnDelegate())
    delegate.insertColumnDelegate(define.REFADDR, KRefColumnDelegate(projectDir, filename))
    delegate.insertColumnDelegate(define.NOTE, KNoteColumnDelegate())
    self.tableView.setItemDelegate(delegate)
    self.tableView.setMouseTracking(True)
    self.tableView.setAlternatingRowColors(True)
    self.model = KHeaderTableModel(filename)
    self.tableView.setModel(self.model)
    self.tableView.resizeColumnsToContents()
    self.tableView.resizeRowsToContents()

    buttonLayout = QHBoxLayout()
    buttonLayout.addWidget(addButton)
    buttonLayout.addWidget(delButton)
    buttonLayout.addWidget(upButton)
    buttonLayout.addWidget(downButton)
    buttonLayout.addStretch()

    buttonLayout1 = QHBoxLayout()
    buttonLayout1.addWidget(self.saveButton)
    buttonLayout1.addWidget(self.discardButton)
    buttonLayout1.addStretch()

    mainLayout = QVBoxLayout()
    mainLayout.addLayout(buttonLayout)
    mainLayout.addWidget(self.tableView)
    mainLayout.addLayout(buttonLayout1)
    self.setLayout(mainLayout)

    self.connect(addButton, SIGNAL("clicked()"), self.addHeader)
    self.connect(delButton, SIGNAL("clicked()"), self.delHeader)
    self.connect(upButton, SIGNAL("clicked()"), self.upHeader)
    self.connect(downButton, SIGNAL("clicked()"), self.downHeader)
    self.connect(self.saveButton, SIGNAL("clicked()"), self.saveHeader)
    self.connect(self.discardButton, SIGNAL("clicked()"), self.discard)
    self.connect(self.model, SIGNAL("dataModified"), \
        self.dataModified)
    self.connect(self.model, SIGNAL("headerDataError"), self.headerDataError)
    self.connect(self.tableView, SIGNAL("entered(const QModelIndex&)"), self.checkDataModified)

  def checkDataModified(self):
    if self.model.checkDataModified():
      ret = QMessageBox.question(self, u"文件'%s'被修改." % \
        self.__filename + define.HEADER_FILE_SUF,
        u"是否保存载入数据?",
        QMessageBox.Ok | QMessageBox.Cancel)
      if ret == QMessageBox.Cancel:
        return
      self.model.reload()

  def updatePath(self, path):
    self.model.updatePath(path)

  def headerDataError(self, errorTitle, info):
    QMessageBox.information(self, errorTitle, info)

  def addHeader(self):
    indexes = self.tableView.selectedIndexes()
    if not len(indexes):
      row = self.model.rowCount()
    else:
      row = indexes[0].row() + 1
    self.model.insertRows(row)
    index = self.model.index(row, 0)
    self.tableView.setCurrentIndex(index)
    self.tableView.edit(index)
    self.dataModified()  
  
  def upHeader(self):
    indexes = self.tableView.selectedIndexes()
    if not len(indexes):
      return
    row = indexes[0].row()
    if row == 0:
      return
    rowInfo = self.model.getRowInfo(row)
    self.model.removeRows(row)
    self.model.insertRows(row - 1, 1, [rowInfo])
    self.tableView.setCurrentIndex(self.model.index(row - 1, 0))
    self.setEnableSaveAndDiscard()    

  def downHeader(self):
    indexes = self.tableView.selectedIndexes()
    if not len(indexes):
      return
    row = indexes[0].row()
    if row == self.model.rowCount() - 1:
      return
    rowInfo = self.model.getRowInfo(row)
    self.model.removeRows(row)
    self.model.insertRows(row + 1, 1, [rowInfo])
    self.tableView.setCurrentIndex(self.model.index(row + 1, 0))
    self.setEnableSaveAndDiscard()    

  def delHeader(self):
    indexes = self.tableView.selectedIndexes()
    if not len(indexes):
      return
    rowSet = set()
    for idx in indexes:
      rowSet.add(idx.row())
    self.model.removeRows(min(rowSet), len(rowSet))
    self.dataModified()
    
  def saveHeader(self):
    try:
      res = self.model.checkHeaderData()
      if res is None:
        if self.__parent.updateHeaderInfo(self.headerInfo().clone()):
          self.model.saveHeaderData()
          self.setEnableSaveAndDiscard(False)
          self.emit(SIGNAL("headerSaved"))
          self.__dirty = False
      else:
        QMessageBox.information(self, u"表头错误", res)
    except Exception, e:
      log.error_log(u"%s" % e)
      log.error_log(traceback.format_exc().decode(define.CODEC))
      self.headerDataError(u"保存文件错误", u"%s" % e)

  def discard(self):
    self.model.discard()
    self.setEnableSaveAndDiscard(False)
    self.__dirty = False
    self.emit(SIGNAL("headerSaved"), None)

  def dataModified(self):
    self.setEnableSaveAndDiscard()
    self.__dirty = True
    self.emit(SIGNAL("headerModified"))

  def setEnableSaveAndDiscard(self, isEnable = True):
    self.discardButton.setEnabled(isEnable)
    self.saveButton.setEnabled(isEnable)

  def headerInfo(self):
    return self.model.headerInfo()

  def okToContinue(self):
    if not self.__dirty:
      return True

    ret = QMessageBox.question(self, u"文件'%s'修改." % \
        os.path.basename(self.__filename),
        u"是否保存表头?",
        QMessageBox.Save | QMessageBox.Cancel | QMessageBox.Discard)
    if ret == QMessageBox.Save:
      self.saveHeader()
      return True
    return QMessageBox.Discard == ret

class KHeaderTableModel(QAbstractTableModel):
  def __init__(self, filename, parent=None):
    super(KHeaderTableModel, self).__init__(parent)
    self.__headerDataContainer = KHeaderDataContainer(filename)
    self.__dataBK = None
    self.__dirty = False

  def headerInfo(self):
    return self.__headerDataContainer

  def rowCount(self, index=QModelIndex()):
    return len(self.__headerDataContainer)

  def columnCount(self, index=QModelIndex()):
    return define.HEADER_DATA_COLUMN_COUNT
  
  def headerCount(self, index=QModelIndex()):
    return define.HEADER_DATA_COLUMN_COUNT

  def flags(self, index):
    if not index.isValid():
      return Qt.ItemIsEnabled
    hd = self.__headerDataContainer[index.row()]
    if index.column() == define.REFADDR and \
        hd.dataType != define.DATA_TYPES[define.INT_IDX] and \
        hd.dataType != define.DATA_TYPES[define.INT_ARR_IDX]:
      return QAbstractTableModel.flags(self, index)
    return Qt.ItemFlags(QAbstractTableModel.flags(self, index) |
        Qt.ItemIsEditable)

  def data(self, index, role=Qt.DisplayRole):
    if not index.isValid() or \
        not (0 <= index.row() < len(self.__headerDataContainer)):
          return QVariant()
    hd = self.__headerDataContainer[index.row()]
    column = index.column()
    if role == Qt.DisplayRole:
      if column == define.NAME:
        return QVariant(hd.name)
      if column == define.DATATYPE:
        return QVariant(hd.dataType)
      if column == define.CS:
        return QVariant(hd.cs)
      if column == define.ISUNIQUIE:
        return QVariant(define.CHECKED_TEXT 
            if hd.isUnique == define.YES_TXT
            else define.UNCHECKED_TEXT)
      if column == define.IS_I18N:
        return QVariant(define.CHECKED_TEXT 
            if hd.isI18n == define.YES_TXT
            else define.UNCHECKED_TEXT)
      if column == define.REFADDR:
        return QVariant(hd.ref)
      if column == define.ALLOWEMPTY:
        return QVariant(define.CHECKED_TEXT 
            if hd.allowEmpty == define.YES_TXT
            else define.UNCHECKED_TEXT)
      if column == define.NOTE:
        return QVariant(hd.note)

    return QVariant()

  def headerData(self, section, orientation, role=Qt.DisplayRole):
    if role == Qt.TextAlignmentRole:
      if orientation == Qt.Horizontal:
        return QVariant(int(Qt.AlignLeft | Qt.AlignVCenter))
      return QVariant(int(Qt.AlignRight | Qt.AlignVCenter))
    if role != Qt.DisplayRole:
      return QVariant()
    if orientation == Qt.Horizontal:
      if section == define.NAME:
        return QVariant(u'名称')
      if section == define.DATATYPE:
        return QVariant(u'数据类型')
      if section == define.CS:
        return QVariant(u'目的数据')
      if section == define.ISUNIQUIE:
        return QVariant(u'唯一')
      if section == define.IS_I18N:
        return QVariant(u'i18n')
      if section == define.REFADDR:
        return QVariant(u'引用地址')
      if section == define.ALLOWEMPTY:
        return QVariant(u'允许空值')
      if section == define.NOTE:
        return QVariant(u'注释')
    return QVariant(int(section + 1))

  def setData(self, index, value, role=Qt.EditRole):
    if index.isValid() and 0 <= index.row() < len(self.__headerDataContainer):
      isModified = False
      strData = unicode(value.toString())
      hd = self.__headerDataContainer[index.row()]
      section = index.column()
      if section == define.NAME:
        if index.row() == 0 and strData != "id":
            self.emit(SIGNAL("headerDataError"), u"表头错误", u"第一个属性名称为'id'")
            return False
        if hd.name != strData:
          if self.__headerDataContainer.hasHeaderName(strData):
            self.emit(SIGNAL("headerDataError"), u"表头错误", u"'%s' 重复" % strData)
            return False
          self.dataModified()
          hd.name = strData
          isModified = True
      if section == define.CS:
        if hd.cs != strData:
          self.dataModified()
          hd.cs = strData
          isModified = True
      if section == define.DATATYPE:
        if index.row() == 0 and strData != define.DATA_TYPES[define.INT_IDX]:
            self.emit(SIGNAL("headerDataError"), u"表头错误", u"第一个属性类型必须为'int'")
            return False
        if hd.dataType != strData:
          if not len(strData):
            self.emit(SIGNAL("headerDataError"), u"数据错误",
                u"%s 数据类型不能为空" % hd.name)
            return False
          self.dataModified()
          hd.dataType = strData
          isModified = True
      if section == define.ISUNIQUIE:
        isUnique = define.YES_TXT if strData == define.CHECKED_TEXT \
            else define.NO_TXT
        if hd.isUnique != isUnique:
          self.dataModified()
          hd.isUnique = isUnique
          isModified = True
      if section == define.REFADDR:
        if hd.ref != strData:
          self.dataModified()
          hd.ref = strData
          isModified = True
      if section == define.ALLOWEMPTY:
        allowEmpty = define.YES_TXT if strData == define.CHECKED_TEXT \
            else define.NO_TXT
        if hd.allowEmpty != allowEmpty:
          self.dataModified()
          hd.allowEmpty = allowEmpty
          isModified = True
      if section == define.IS_I18N:
        isI18n = define.YES_TXT if strData == define.CHECKED_TEXT \
            else define.NO_TXT
        if hd.isI18n != isI18n:
          self.dataModified()
          hd.isI18n = isI18n
          isModified = True
      if section == define.NOTE:
        if hd.note != strData:
          self.dataModified()
          hd.note = strData
          isModified = True
      if isModified:
        self.emit(SIGNAL("dataChanged(QModelIndex, QModelIndex)"), index,
          index)
        self.emit(SIGNAL("dataModified"))
      return True
    return False

  def insertRows(self, position, rows = 1, rowList = None, index=QModelIndex()):
    self.dataModified()
    self.beginInsertRows(QModelIndex(), position,
        position + rows - 1)
    self.__headerDataContainer.insert(position, rowList)
    self.endInsertRows()
    return True

  def dataModified(self):
    if not self.__dirty:
      self.__dataBK = self.__headerDataContainer.clone()
      self.__dirty = True
      self.emit(SIGNAL("dataModified"))

  def reload(self):
    self.__headerDataContainer.load()

  def removeRows(self, position, rows = 1, index = QModelIndex()):
    self.dataModified()
    self.beginRemoveRows(QModelIndex(), position,
        position + rows - 1)
    self.__headerDataContainer.remove(position, rows)
    self.endRemoveRows()
    return True

  def createEditor(self, parent, option, index):
    lineedit = QLineEdit(parent)
    return lineedit

  def setEditorData(self, editor, index):
    value = index.model().data(index, Qt.DisplayRole).toString()
    editor.setText(value)

  def loadHeaderData(self):
    self.__headerDataContainer.load()

  def saveHeaderData(self):
    self.__headerDataContainer.save()
    self.__dirty = False
    self.__dataBK = []

  def checkHeaderData(self):
    return self.__headerDataContainer.check()

  def discard(self):
    self.removeRows(0, self.rowCount())
    self.insertRows(0, len(self.__dataBK), self.__dataBK)
    self.__dirty = False
 
  def getRowInfo(self, rowIdx):
    return self.__headerDataContainer[rowIdx]

  def updatePath(self, path):
    self.__headerDataContainer.setFilename(path)

  def checkDataModified(self):
    return self.__headerDataContainer.checkDataModified()

class KHeaderData(object):
  def __init__(self, name, dataType, cs, isUnique, allowEmpty, ref, note, isI18n=False, id = 0):
    self.name = name
    self.dataType = dataType
    self.cs = cs
    self.isUnique = isUnique
    self.allowEmpty = allowEmpty
    self.ref = ref
    self.note = note
    self.id = id
    self.isI18n = isI18n

  def isArray(self):
    dataType = define.DATA_TYPES.index(self.dataType)
    return dataType == define.INT_ARR_IDX or \
        dataType == define.FLOAT_ARR_IDX or \
        dataType == define.STR_ARR_IDX;

  def isStr(self):
    dataType = define.DATA_TYPES.index(self.dataType)
    return dataType == define.STR_IDX or dataType == define.STR_ARR_IDX

  def clone(self):
    return KHeaderData(self.name, self.dataType, self.cs, self.isUnique, \
        self.allowEmpty, self.ref, self.note, self.isI18n, self.id)

  def __str__(self):
    return self.name + "\n" + self.dataType + "\n" + self.cs + "\n" + self.note

  def __eq__(self, other):
    return self.id == other.id
    
  def canConvert2(self, other):
    if self.id != other.id:
      return False

    if self.name != other.name:
      print "self.name=%s,other.name=%s" % (self.name, other.name)

    if self.name != other.name:
    	return False
    
    if self.dataType == other.dataType:
      return True
 
    selftype = -1
    if self.dataType in define.DATA_TYPES:
      selftype = define.DATA_TYPES.index(self.dataType)
    othertype = -1
    if other.dataType in define.DATA_TYPES:
      othertype = define.DATA_TYPES.index(other.dataType)

    return (othertype == define.INT_ARR_IDX and selftype == define.INT_IDX) or \
        (othertype == define.FLOAT_ARR_IDX and selftype == define.FLOAT_IDX) or \
        (othertype == define.STR_ARR_IDX and selftype == define.STR_IDX) or \
        (othertype == define.FLOAT_IDX and selftype == define.INT_IDX) or \
        (othertype == define.FLOAT_ARR_IDX and selftype == define.INT_ARR_IDX)

  def __gt__(self, other):
    return self.id > other.id

  def __le__(self, other):
    return not self.__gt__(other)

  def __lt__(self, other):
    return self.id < other.id

  def __ge__(self, other):
    return not self.__lt__(other)

class KHeaderDataContainer(object):
  COLUMN_NAME_IDX = 1

  HEADER_ID_GENERATOR = 0

  def __init__(self, filename):
    if filename is None:
      raise IOError, u"请输入文件名"
    self.__filename = filename
    self.__headerDatas = []
    self.load()

  def __len__(self):
    return len(self.__headerDatas)

  def __iter__(self):
    for hd in self.__headerDatas:
      yield hd

  def __getitem__(self, k):
    return self.__headerDatas[k]

  def setFilename(self, filename):
    self.__filename = filename

  def checkDataModified(self):
    lmtime = os.path.getmtime(self.__filename + define.HEADER_FILE_SUF)
    if lmtime != self.__lastSaveTime:
      return True
    return False

  def hasHeaderName(self, name):
    for h in self.__headerDatas:
      if h.name == name:
        return True
    return False

  def remove(self, position, rows):
    del self.__headerDatas[position:position + rows]

  def insert(self, position, rows = None):
    if rows is None:
      self.__headerDatas.insert(position,
        KHeaderData('column%d' % KHeaderDataContainer.COLUMN_NAME_IDX,
          define.DATA_TYPES[0], "cs", define.NO_TXT, define.YES_TXT, '', '',
          False, KHeaderDataContainer.HEADER_ID_GENERATOR))

      KHeaderDataContainer.COLUMN_NAME_IDX = \
          KHeaderDataContainer.COLUMN_NAME_IDX + 1
      KHeaderDataContainer.HEADER_ID_GENERATOR = \
          KHeaderDataContainer.HEADER_ID_GENERATOR + 1
    elif len(rows) > 0:
      rowth = position
      for row in rows:
        self.__headerDatas.insert(rowth, row)
        rowth = rowth + 1
    return 0
  
  def clone(self):
    return [x.clone() for x in self.__headerDatas]

  def load(self):
    self.__headerDatas = KDataWarehouse.getHeaderData(self.__filename)
    self.__lastSaveTime = os.path.getmtime(self.__filename +
        define.HEADER_FILE_SUF)
    KHeaderDataContainer.HEADER_ID_GENERATOR = len(self.__headerDatas)

  def check(self):
    checkSet = set()
    if len(self.__headerDatas) == 0:
      return None
    firstHeader = self.__headerDatas[0]
    if firstHeader.name != "id" or \
        firstHeader.dataType != define.DATA_TYPES[define.INT_IDX]:
      return u"第一个属性必须为'id'，类型为int"
    for h in self.__headerDatas:
      name = h.name
      if name in checkSet:
        return u"'%s'重复" % name
      checkSet.add(name)
    return None

  def save(self):
    #KPersistHeader.store(self.__headerDatas, self.__filename)
    KDataWarehouse.setHeaderData(self.__filename, self.__headerDatas)
    KDataWarehouse.saveHeader(self.__filename)
    self.__lastSaveTime = os.path.getmtime(self.__filename +
        define.HEADER_FILE_SUF)
    return None

  def rowCount(self):
    return len(self)

  def columnCount(self):
    return len(self.__data) - 1

  def getData(self, row, column):
    return self.__data[column][row]
