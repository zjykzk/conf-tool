# -*- coding: utf-8 -*-
# Author : xiaok
# 2011-08-04 11:25
import os
import datetime
import collections
import traceback

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import genericdelegates as gd
import define
import data_codec as dc
import data_commands as cmd
from datawarehouse import *
from findandreplacedlg import *
import table_header as th
import log
import check_uis as cui
import ui_replace_i18n as ri18n

class KDataTabWidget(QTabWidget):
  #def __init__(self, path, root, headerWgt=None, dataWgt=None):
  def __init__(self, path, root):
    super(KDataTabWidget, self).__init__()
    self.path = path
    self.root = root
    headerWgt = th.KHeaderTableWidget(root, path[:-len(define.DATA_FILE_SUF)], self)
    dataWgt = KDataTableWidget(path[:-len(define.DATA_FILE_SUF)], root, headerWgt.headerInfo().clone(), self)
    self.__headerWgt = headerWgt
    self.__dataWgt = dataWgt

    self.addTab(headerWgt, u"表头")
    self.addTab(dataWgt, u"数据")

    self.connect(headerWgt, SIGNAL("headerModified"), self.headerModified)
    self.connect(headerWgt, SIGNAL("headerSaved"), self.headerSaved)
    self.connect(dataWgt, SIGNAL("dataModified"), self.dataModified)
    self.connect(dataWgt, SIGNAL("dataSaved"), self.dataSaved)
  
  def isMe(self, path, root):
    return self.path == path and self.root == root

  def headerModified(self):
    self.setTabText(0, u"+ 表头")

  def updateHeaderInfo(self, headerInfo):
    ret = self.__dataWgt.updateHeaderInfo(headerInfo)
    if ret[0] != KDataStatusError.STATUS_OK:
      self.setCurrentWidget(self.__dataWgt)
      self.__dataWgt.gotoIndex(ret[1] - 1, ret[2] - 1)
      QMessageBox.information(self, u"数据不一致",
          KDataStatusError.errorInfo[ret[0]] % (ret[1], ret[2]))
      return False
    return True

  def headerSaved(self):
    self.setTabText(0, u"表头")

  def dataModified(self):
    self.setTabText(1, u"+ 数据")

  def dataSaved(self):
    self.setTabText(1, u"数据")

  def okToContinue(self):
    return self.__headerWgt.okToContinue() and self.__dataWgt.okToContinue()

  def updatePath(self, path):
    self.__headerWgt.updatePath(path)
    self.__dataWgt.updatePath(path)
  
  def findReplace(self):
    self.currentWidget().findReplace()

class KTableView(QTableView):
  HIDDEN_COLUMNS = 2

  def __init__(self, parent, model, logicParent=None):
    super(KTableView, self).__init__(parent)
    self.logicParent = logicParent 
    self.model = model
    self.setModel(model)

  def contextMenuEvent(self, event):
    idxes = self.selectedIndexes()
    if len(idxes) == 0:
      return
    self.createMenu().exec_(event.globalPos())

  def createMenu(self):
    menu = QMenu(self)
    cpAction = menu.addAction(u"复制行")
    self.connect(cpAction, SIGNAL("triggered()"), self.copy)
    cutAction = menu.addAction(u"剪切行")
    self.connect(cutAction, SIGNAL("triggered()"), self.cut)
    pasteAction = menu.addAction(u"粘贴行")
    self.connect(pasteAction, SIGNAL("triggered()"), self.paste)
    if self.logicParent.isClipperEmpty():
      pasteAction.setDisabled(True)
    return menu

  def copy(self):
    self.logicParent.copy()

  def cut(self):
    self.logicParent.cut()

  def paste(self):
    self.logicParent.paste()

class KFreezeTableView(KTableView):
  def __init__(self, parent, model, logicParent):
    super(KFreezeTableView, self).__init__(parent, model, logicParent)
    self.frozenTableView = KTableView(self, model, logicParent)
    self.init()
    self.connect(self.horizontalHeader(), SIGNAL("sectionResized(int, int, int)"),
        self.updateSectionWidth)
    self.connect(self.verticalHeader(), SIGNAL("sectionResized(int, int, int)"),
        self.updateSectionHeight)
    self.connect(self.frozenTableView.verticalScrollBar(), SIGNAL("valueChanged(int)"),
        self.verticalScrollBar(), SLOT("setValue(int)"))
    self.connect(self.verticalScrollBar(), SIGNAL("valueChanged(int)"),
        self.frozenTableView.verticalScrollBar(), SLOT("setValue(int)"))
    self.connect(self.verticalHeader(), SIGNAL("valueChange(int)"),
        self.frozenTableView.verticalScrollBar(), SLOT("setValue(int)"))

  def init(self):
    self.frozenTableView.setFocusPolicy(Qt.NoFocus)
    self.frozenTableView.verticalHeader().hide()
    self.frozenTableView.horizontalHeader().setResizeMode(QHeaderView.Fixed)

    self.viewport().stackUnder(self.frozenTableView)
    self.frozenTableView.setSelectionModel(self.selectionModel())
    self.frozenTableView.setItemDelegate(self.itemDelegate())
    ccnt = self.model.columnCount() - KTableView.HIDDEN_COLUMNS
    for c in range(ccnt):
      self.frozenTableView.setColumnHidden(c + KTableView.HIDDEN_COLUMNS, True)

    for c in range(KTableView.HIDDEN_COLUMNS):
      self.frozenTableView.setColumnWidth(c, self.columnWidth(c))

    self.frozenTableView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    self.frozenTableView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    self.updateFrozenTableGeometry()
    self.frozenTableView.show()

    self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
    self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
    self.frozenTableView.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

  def updateSectionWidth(self, logicalIndex, ig, newSize):
    if logicalIndex >=0 and logicalIndex < KTableView.HIDDEN_COLUMNS:
      self.frozenTableView.setColumnWidth(logicalIndex, newSize)
      self.updateFrozenTableGeometry()

  def updateSectionHeight(self, logicalIndex, ig, newSize):
    self.frozenTableView.setRowHeight(logicalIndex, newSize)
    self.updateFrozenTableGeometry()

  def resizeEvent(self, event):
    super(QTableView, self).resizeEvent(event)
    self.updateFrozenTableGeometry()

  def moveCursor(self, cursorAction, modifiers):
    current = QTableView.moveCursor(self, cursorAction, modifiers)

    w = 0
    for c in range(KTableView.HIDDEN_COLUMNS):
      w = w + self.frozenTableView.columnWidth(c)
    if cursorAction == QAbstractItemView.MoveLeft and \
        current.column() > KTableView.HIDDEN_COLUMNS and \
        self.visualRect(current).topLeft().x() < w:
        newValue = self.horizontalScrollBar().value() + self.visualRect(current).topLeft().x() - \
            w
        self.horizontalScrollBar().setValue(newValue)

    return current;

  def scrollTo(self, index, hint):
    if index.column() > KTableView.HIDDEN_COLUMNS:
      QTableView.scrollTo(self, index, hint)

  def updateFrozenTableGeometry(self):
    w = 0
    for c in range(KTableView.HIDDEN_COLUMNS):
      w = w + self.columnWidth(c)
    ax = self.verticalHeader().width() + self.frameWidth()
    ay = self.frameWidth()
    aw = w
    ah = self.viewport().height() + self.horizontalHeader().height()
    self.frozenTableView.horizontalHeader().setFixedHeight(self.horizontalHeader().height())
    self.frozenTableView.setGeometry(ax, ay, aw, ah)
  
  def setItemDelegate(self, delegate):
    self.frozenTableView.setItemDelegate(delegate)
    super(KFreezeTableView, self).setItemDelegate(delegate)

  def updateFrozenView(self):
    '''
    这个方式有点土，就是当增加一列的时候，需要新建锁定前两列的tableview

    日后研究以后在做修改吧
    '''
    self.frozenTableView = KTableView(self, self.model, self.logicParent)
    self.init()
    self.frozenTableView.resizeRowsToContents()

  def setSelectionMode(self, mode):
    self.frozenTableView.setSelectionMode(mode)
    super(KFreezeTableView, self).setSelectionMode(mode)

  def setSelectionBehavior(self, sb):
    self.frozenTableView.setSelectionBehavior(sb)
    super(KFreezeTableView, self).setSelectionBehavior(sb)

  def setMouseTracking(self, tf):
    self.frozenTableView.setMouseTracking(tf)
    super(KFreezeTableView, self).setMouseTracking(tf)

  def setAlternatingRowColors(self, tf):
    self.frozenTableView.setAlternatingRowColors(tf)
    super(KFreezeTableView, self).setAlternatingRowColors(tf)

  def resizeColumnsToContents(self):
    self.frozenTableView.resizeColumnsToContents()
    super(KFreezeTableView, self).resizeColumnsToContents()

  def resizeRowsToContents(self):
    self.frozenTableView.resizeRowsToContents()
    super(KFreezeTableView, self).resizeRowsToContents()

  def setCurrentIndex(self, idx):
    self.frozenTableView.setCurrentIndex(idx)
    super(KFreezeTableView, self).setCurrentIndex(idx)

  '''
  def edit(self, index):
    self.frozenTableView.edit(index)
    super(KFreezeTableView, self).edit(index)
  '''


# fields 'pos'/'cnt' used when copying
# field 'datas' used when cutting, which is list contains the detail data
class Clipper(object):
  def __init__(self, pos, cnt, datas):
    self.pos = pos
    self.cnt = cnt
    self.datas = datas

class KDataTableWidget(QWidget):
  def __init__(self, filename, root, headerInfo, parent=None):
    super(KDataTableWidget, self).__init__(parent)
    self.__headerInfo = headerInfo
    self.__filename = filename
    self.__root = root
    self.__dirty = False
    self.__cmdCter = cmd.KCommandContainer()

    addButton = QPushButton(u'添加', self)
    delButton = QPushButton(u'删除', self)
    commentButton = QPushButton(u'注释', self)
    frButton = QPushButton(u'查找/替换', self)
    markButton = QPushButton(u'标记', self)
    checkButton = QPushButton(u'数组检查', self)
    resButton = QPushButton(u'资源检查', self)
    exportButton = QPushButton(u'导出i18n文本', self)
    replaceButton = QPushButton(u'替换i18n文本', self)
    self.saveButton = QPushButton(u'保存', self)    
    self.discardButton = QPushButton(u'放弃', self)
    self.discardButton.setEnabled(False)
    self.saveButton.setEnabled(False)
    self.model = KTableDataModel(headerInfo, filename, root, self)
    self.tableView = KFreezeTableView(self, self.model, self)
    self.tableView.setSelectionMode(QTableView.ContiguousSelection)
    self.tableView.setSelectionBehavior(QTableView.SelectItems)
    self.tableView.setItemDelegate(self.createDelegate())
    self.tableView.setMouseTracking(True)
    self.tableView.setAlternatingRowColors(True)
    self.tableView.resizeColumnsToContents()
    self.tableView.resizeRowsToContents()
    
    buttonLayout = QHBoxLayout()
    buttonLayout.addWidget(addButton)
    buttonLayout.addWidget(delButton)
    buttonLayout.addWidget(commentButton)
    buttonLayout.addWidget(frButton)
    buttonLayout.addWidget(markButton)
    buttonLayout.addWidget(checkButton)
    buttonLayout.addWidget(resButton)
    buttonLayout.addWidget(exportButton)
    buttonLayout.addWidget(replaceButton)
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

    self.connect(addButton, SIGNAL("clicked()"), self.doAddRow)
    self.connect(delButton, SIGNAL("clicked()"), self.doDelRows)
    self.connect(commentButton, SIGNAL("clicked()"), self.comment)
    self.connect(frButton, SIGNAL("clicked()"), self.findReplace)
    self.connect(markButton, SIGNAL("clicked()"), self.markColor)
    self.connect(checkButton, SIGNAL("clicked()"), self.checkData)
    self.connect(resButton, SIGNAL("clicked()"), self.checkRes)
    self.connect(exportButton, SIGNAL("clicked()"), self.exporti18n)
    self.connect(replaceButton, SIGNAL("clicked()"), self.replacei18n)
    self.connect(self.saveButton, SIGNAL("clicked()"), self.saveData)
    self.connect(self.discardButton, SIGNAL("clicked()"), self.discard)
    self.connect(self.model, SIGNAL("dataModified"), self.dataModified)
    self.connect(self.model, SIGNAL("addItemModifiedCmd"), self.addItemModifiedCmd)
    self.connect(self.tableView, SIGNAL("entered(const QModelIndex&)"), self.checkDataModified)
    
    self.__clipper = None

  def gotoIndex(self, row, column):
    self.tableView.setCurrentIndex(self.model.index(row, column))

  def keyPressEvent(self, event):
    key = event.key()
    modifier = event.modifiers()
    if modifier == Qt.ControlModifier and key == Qt.Key_V:
      import utils
      clipdata = utils.getClipboardText()
      print clipdata
      lineDatas = [] if not clipdata else clipdata.strip().split("\r\n")
      print lineDatas
      eles = []
      for line in lineDatas:
        eles.append(line.strip().split("\t"))
      rowCount = len(eles)
      columnCount = len(eles[0])
      firstRow, firstColumn = min(self.__getSelectedRows()), min(self.__getSelectedColumns())
      for r in range(rowCount):
        for c in range(columnCount):
          self.model.setData(self.model.index(r + firstRow, c + firstColumn), QVariant(eles[r][c]))
      return

    if modifier == Qt.ControlModifier and key == Qt.Key_C:
      selectedRows = self.__getSelectedRows()
      if not selectedRows:
        return
      import utils
      firstRow, firstColumn = min(self.__getSelectedRows()), min(self.__getSelectedColumns())
      # TODO

    # super(QWidget, self).keyPressEvent(event) FIXME

  def __getSelectedColumns(self):
    idxes = self.tableView.selectedIndexes()
    idxSet = set()
    for idx in idxes:
      idxSet.add(idx.column())
    return idxSet

  def __getSelectedRows(self):
    """
      return a sequence of row index
    """
    idxes = self.tableView.selectedIndexes()
    idxSet = set()
    for idx in idxes:
      idxSet.add(idx.row())
    return idxSet

  def copy(self):
    idxSet = self.__getSelectedRows()
    self.__clipper = Clipper(min(idxSet), len(idxSet), None)

  def cut(self):
    idxes = self.__getSelectedRows()
    pos = min(idxes)
    cnt = len(idxes)
    datas = self.model.getRows(pos, cnt)
    if self.__clipper is None:
      self.__clipper = Clipper(pos, cnt, datas)
    else:
      self.__clipper.datas = datas

    self.__delRows(pos, cnt)

  def paste(self):
    if self.__clipper is None:
      return
    idxes = self.__getSelectedRows()
    addedPos = max(idxes) + 1
    if self.__clipper.datas is not None:
      self.__addRows(addedPos, self.__clipper.cnt, self.__clipper.datas)
    elif self.__clipper.pos != -1:
      self.__addRows(addedPos, len(idxes), self.model.getRows(self.__clipper.pos,
        self.__clipper.cnt))
    self.__clipper.pos = -1
    self.__clipper.cnt = -1
    self.__clipper.datas = None

  def isClipperEmpty(self):
    return self.__clipper is None or \
        self.__clipper.pos == -1 and self.__clipper.cnt == -1 \
        and self.__clipper.datas == None

  def findReplace(self):
    form = KFindAndReplaceDlg(self.model.getFindAndReplaceData(), self)
    form.show()

  def markColor(self):
    c = QColorDialog.getColor(Qt.white, self, u'标记')
    if not c.isValid(): return
    idxes = self.__getSelectedRows()
    if not idxes: return
    rowSet = self.getSelectRowSet()
    self.__cmdCter.addCmd(cmd.KRowOpts(list(rowSet), self.getRowOpts(rowSet),
      self.model))
    self.model.setBgColor(list(rowSet), c.rgb())
    self.dataModified()

  def replacei18n(self):
    replace_i18n_dlg = ri18n.ReplaceI18NDialog(
        self.__filename[self.__filename.rindex('\\')+1:], self)
    replace_i18n_dlg.show()

  def exporti18n(self):
    filename = QFileDialog.getSaveFileName(self, "Save File",
                                          "", "Excel (*.xls)")
    if not filename:
    	return
    headers = [h for h in self.__headerInfo if int(h.isI18n) > 0]
    header_indice = [self.__headerInfo.index(h) for h in headers]
    datas = self.model.getDataList()
    i18n_datas = []
    for index in header_indice:
      i18n_datas.extend(datas[index])
    import xlwt
    book = xlwt.Workbook('utf-8')
    name = self.__filename[self.__filename.rindex('\\')+1:]
    sheet = book.add_sheet(name)
    for r, text in enumerate(i18n_datas):
      sheet.write(r, 0, text)
    book.save(unicode(filename))
  
  def replace_i18n(self, text_dic):
    headers = [h for h in self.__headerInfo if int(h.isI18n) > 0]
    header_indice = [self.__headerInfo.index(h) for h in headers]
    datas = self.model.getDataList()
    not_replaced_texts = []
    for header_index in header_indice:
      for row_index in xrange(self.model.rowCount()):
        text = datas[header_index][row_index] 
        if not text in text_dic:
          not_replaced_texts.append(text)
          continue
        print text
        self.model.setData(self.model.index(row_index, header_index),
            QVariant(text_dic[text]))
    return u'\n'.join(not_replaced_texts)

  def checkData(self):
    headers = [h for h in self.__headerInfo if h.isArray()]
    headerIdxes = [self.__headerInfo.index(h) for h in headers]
    datas = self.model.getDataList()
    checkForm = cui.ArrayLengthCheck([h.name for h in headers], \
        [datas[idx] for idx in headerIdxes], self)
    checkForm.show()

  def checkRes(self):
    from rescheckdlg import ResCheck
    headerIdxes = [idx for idx, h in enumerate(self.__headerInfo) if h.isStr()]
    datas = self.model.getUncommentedData()
    checkForm = ResCheck([self.__headerInfo[h].name for h in headerIdxes], \
        [datas[idx] for idx in headerIdxes], self)
    checkForm.setFixedSize(400, 300)
    checkForm.show()

  def getSelectRowSet(self):
    indexes = self.tableView.selectedIndexes()
    rowSet = set()
    for idx in indexes:
      rowSet.add(idx.row())
    return rowSet

  def findStr(self, row, column):
    index = self.model.index(row, column)
    self.tableView.setCurrentIndex(index)
    self.tableView.scrollTo(index)

  def replaceStr(self, rows, columns, data):
    self.model.replace(rows, columns)
    self.__cmdCter.addCmd(cmd.KReplaceCommand(rows, columns, data, self.model))

  def comment(self):
    indexes = self.tableView.selectedIndexes()
    if len(indexes) == 0:
      return
    rowSet = self.getSelectRowSet()
    self.dataModified()
    self.__cmdCter.addCmd(cmd.KRowOpts(list(rowSet), self.getRowOpts(rowSet),
      self.model))
    self.model.comment([r for r in rowSet])

  def getRowOpts(self, rowSet):
    ans = []
    for r in rowSet:
      opt = self.model.getRowOpt(r)
      nopt = KOpts()
      nopt.setComment(opt.isComment())
      nopt.setBgColor(opt.bgColor())
      ans.append(nopt)

    return ans

  def checkDataModified(self):
    if self.model.checkDataModified():
      ret = QMessageBox.question(self, u"文件'%s'被修改." % \
        self.__filename + define.DATA_FILE_SUF,
        u"是否保存载入数据?",
        QMessageBox.Ok | QMessageBox.Cancel)
      if ret == QMessageBox.Cancel:
        return
      self.model.reload()

  def createDelegate(self):
    delegate = gd.GenericDelegate(self)
    idx = 0
    for h in self.__headerInfo:
      dt = h.dataType
      if dt == define.DATA_TYPES[define.INT_IDX]:
        delegate.insertColumnDelegate(idx, \
            gd.IntegerColumnDelegate(QRegExpValidator(
              QRegExp(r"^-?(0|[1-9]\d*)$"), self)))
      elif dt == define.DATA_TYPES[define.INT_ARR_IDX]:
        delegate.insertColumnDelegate(idx,
            gd.IntegerColumnDelegate(QRegExpValidator(
              QRegExp(r"^-?(0|([1-9]\d*))(,-?(0|([1-9]\d*)))*$"), self)))
      elif dt == define.DATA_TYPES[define.BOOL_IDX]:
        delegate.insertColumnDelegate(idx, gd.BoolColumnDelegate())
      elif dt == define.DATA_TYPES[define.BOOL_ARR_IDX]:
        delegate.insertColumnDelegate(idx, gd.IntegerColumnDelegate(
          QRegExpValidator(QRegExp(r"^(0|1)(,(0|1))*$"), self)))
      elif dt == define.DATA_TYPES[define.STR_IDX]:
        delegate.insertColumnDelegate(idx, \
            gd.PlainTextColumnDelegate())
      elif dt == define.DATA_TYPES[define.STR_ARR_IDX]:
        delegate.insertColumnDelegate(idx, \
            gd.IntegerColumnDelegate(QRegExpValidator(
              QRegExp(r"^([^,]+)(,[^,]+)*$"), self)))
      elif dt == define.DATA_TYPES[define.FLOAT_IDX]:
        delegate.insertColumnDelegate(idx, \
            gd.DoubleColumnDelegate())
      elif dt == define.DATA_TYPES[define.FLOAT_ARR_IDX]:
        delegate.insertColumnDelegate(idx,
            gd.DoubleColumnDelegate(QRegExpValidator(
              QRegExp(r"^-?(0|([1-9]\d*))(\.\d+)?(,-?(0|([1-9]\d*))(\.\d+)?)*$"), self)))
      elif dt == define.DATA_TYPES[define.DATE_IDX]:
        delegate.insertColumnDelegate(idx, gd.DateColumnDelegate(parent=self))
      idx = idx + 1
    return delegate

  def __addRows(self, pos, rows, datas):
    self.model.insertRows(pos, rows, datas)
    self.__cmdCter.addCmd(cmd.KRowInsertCmd(pos, self.model, rows))
    self.dataModified()

  def doAddRow(self):
    if len(self.__headerInfo) == 0:
      return

    indexes = self.tableView.selectedIndexes()
    if not len(indexes):
      row = self.model.rowCount()
    else:
      row = indexes[0].row() + 1
    self.__addRows(row, 1, None)
    index = self.model.index(row, 0)
    self.tableView.setCurrentIndex(index)
    self.tableView.edit(index)

  def __delRows(self, pos, rows):
    self.__cmdCter.addCmd(cmd.KRowDeleteCmd(pos,self.model.getRows(pos, rows),
      self.model))
    self.model.removeRows(pos, rows)
    self.dataModified()

  def doDelRows(self):
    if len(self.__headerInfo) == 0:
      return

    indexes = self.tableView.selectedIndexes()
    if len(indexes) == 0:
      return
    rowSet = set()
    for idx in indexes:
      rowSet.add(idx.row())
    self.__delRows(min(rowSet), len(rowSet))

  def saveData(self):
    try:
      res = self.model.save()
    except Exception, e:
      log.error_log(u"%s" % e)
      log.error_log(traceback.format_exc().decode(define.CODEC))
      QMessageBox.information(self, u"数据保存错误", u"%s" % e)
      return

    resCode = res[0]
    if resCode == KDataStatusError.STATUS_OK:
      self.setEnableSaveAndDiscard(False)
      self.__dirty = False
      self.__cmdCter.clear()
      self.emit(SIGNAL("dataSaved"))
    else:
      QMessageBox.information(self, u"数据保存", \
          KDataStatusError.errorInfo[resCode] % (res[1], res[2]))
      self.tableView.setCurrentIndex(self.model.index(res[1] - 1, res[2] - 1))

  def discard(self):
    self.__cmdCter.undo()
    self.model.discard()
    self.setEnableSaveAndDiscard(False)
    self.__dirty = False
    self.emit(SIGNAL("dataSaved"))

  def dataModified(self):
    self.setEnableSaveAndDiscard()
    self.__dirty = True
    self.emit(SIGNAL("dataModified"))

  def addItemModifiedCmd(self, row, column, oldValue):
    self.__cmdCter.addCmd(cmd.KItemModifiedCmd(row, column,
          oldValue, self.model))

  def setEnableSaveAndDiscard(self, isEnable = True):
    self.discardButton.setEnabled(isEnable)
    self.saveButton.setEnabled(isEnable)

  def updateHeaderInfo(self, headerInfo):
    self.model.beginResetModel()
    ans = self.model.updateHeaderInfo(headerInfo)
    if ans[0] == KDataStatusError.STATUS_OK:
      self.__headerInfo = headerInfo
      self.tableView.setItemDelegate(self.createDelegate())
      self.tableView.updateFrozenView()
    else:
      self.discardButton.setEnabled(False)
    self.model.endResetModel()
    return ans
  
  def okToContinue(self):
    if not self.__dirty:
      return True
    ret = QMessageBox.question(self, u"文件'%s'修改." % \
        os.path.basename(self.__filename),
        u"是否保存数据?",
        QMessageBox.Save | QMessageBox.Cancel | QMessageBox.Discard)
    if ret == QMessageBox.Save:
      self.saveData()
      return True
    if QMessageBox.Discard == ret:
      self.__dirty = False
      return True
    else:
      return False

  def isMe(self, path, root):
    return self.__filename == path and self.__root == root

  def updatePath(self, path):
    self.model.updatePath(path)

class KTableDataModel(QAbstractTableModel):
  def __init__(self, headerInfo, filename, root, parent=None):
    super(KTableDataModel, self).__init__(parent)
    self.__headerInfo = headerInfo
    self.__filename = filename
    self.__datas = KTableDataContainer(filename, root, headerInfo)
    self.__dirty = False

  def updateHeaderInfo(self, headerInfo):
    ret = self.__datas.updateData(headerInfo)
    if ret[0] == KDataStatusError.STATUS_OK:
      self.__headerInfo = headerInfo
    else:
      self.__dirty = True
    return ret

  def getDataList(self):
    return self.__datas.getDataList()

  def checkDataModified(self):
    return self.__datas.checkDataModified()

  def reload(self):
    """read the data from the disk"""
    self.__datas.load(True)

  def notifyRowChanged(self, rows):
    sorted(rows)
    self.emit(SIGNAL("dataChanged(QModelIndex, QModelIndex)"),
        self.index(rows[0], 0),
        self.index(rows[-1], len(self.__headerInfo) - 1))
    self.dataModified()

  def comment(self, rows):
    for r in rows:
      self.__datas.comment(r)
    self.notifyRowChanged(rows)

  def updateRowsOpt(self, rows, opts):
    for i in range(len(opts)):
      opt = opts[i]
      row = rows[i]
      if opt.isComment():
        self.__datas.comment(row)
      self.setBgColor([row], opt.bgColor())

  def getRowOpt(self, row):
    return self.__datas.getData(row, -1)

  def replace(self, rows, columns):
    for i in range(len(rows)):
      row = rows[i]
      column = columns[i]
      index = self.index(row, column)
      self.emit(SIGNAL("dataChanged(QModelIndex, QModelIndex)"), index, index)
    self.dataModified()

  def rowCount(self, index=QModelIndex()):
    return len(self.__datas)

  def columnCount(self, index=QModelIndex()):
    return len(self.__headerInfo)
  
  def headerCount(self, index=QModelIndex()):
    return len(self.__headerInfo)

  def flags(self, index):
    return Qt.ItemFlags(QAbstractTableModel.flags(self, index) |
        Qt.ItemIsEditable)

  def data(self, index, role=Qt.DisplayRole):
    row = index.row()
    if not index.isValid() or \
        not (0 <= row < len(self.__datas)):
          return QVariant()
    if role == Qt.DisplayRole:
      d = self.__datas.getData(row, index.column())
      if self.__headerInfo[index.column()].dataType == \
        define.DATA_TYPES[define.BOOL_IDX]:
        return QVariant(define.CHECKED_TEXT if d == define.YES_TXT else \
            define.UNCHECKED_TEXT)
      return QVariant(d)
    if self.__datas.isComment(row):
      if role == Qt.FontRole:
        f = QFont()
        f.setStyle(QFont.StyleItalic)
        return QVariant(f)
      elif role == Qt.BackgroundRole:
        b = QBrush()
        b.setColor(Qt.yellow)
        b.setStyle(Qt.SolidPattern)
        return QVariant(b)
    if role == Qt.BackgroundRole:
      b = QBrush(QColor(self.__datas.getRowBGColor(row)))
      b.setStyle(Qt.SolidPattern)
      return QVariant(b)
    return QVariant()

  def headerData(self, section, orientation, role=Qt.DisplayRole):
    if role == Qt.TextAlignmentRole:
      if orientation == Qt.Horizontal:
        return QVariant(int(Qt.AlignLeft | Qt.AlignVCenter))
      return QVariant(int(Qt.AlignRight | Qt.AlignVCenter))
    if role != Qt.DisplayRole:
      return QVariant()
    if orientation == Qt.Horizontal:
      return QVariant(unicode(self.__headerInfo[section]))
    return QVariant(int(section + 1))

  def setData(self, index, value, role=Qt.EditRole):
    row = index.row()
    if index.isValid() and 0 <= row < len(self.__datas):
      column = index.column()
      d = value.toString()
      oldValue = self.__datas.getData(row, column)
      if d != oldValue:
        dt = self.__headerInfo[index.column()].dataType
        if dt == define.DATA_TYPES[define.BOOL_IDX]:
          d = define.YES_TXT if d == define.CHECKED_TEXT else define.NO_TXT
        self.__datas.setData(row, column, unicode(d))
        self.emit(SIGNAL("dataModified"))
        self.emit(SIGNAL("dataChanged(QModelIndex, QModelIndex)"), index,
          index)
        self.emit(SIGNAL("addItemModifiedCmd"), row, column, oldValue)
      return True
    return False

  def restoreData(self, rows, columns, datas):
    for row, column, data in zip(rows, columns, datas):
      index = self.index(row, column)
      self.__datas.setData(row, column, data)
      self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"), index, index)

  def insertRows(self, position, rows = 1, rowList = None, index=QModelIndex()):
    self.beginInsertRows(QModelIndex(), position,
        position + rows - 1)
    self.__datas.insert(position, rowList)
    self.endInsertRows()
    self.dataModified()

  def removeRows(self, position, rows = 1, index = QModelIndex()):
    self.beginRemoveRows(QModelIndex(), position,
        position + rows - 1)
    self.__datas.remove(position, rows)
    self.endRemoveRows()
    self.dataModified()
    return True

  def dataModified(self):
    #TODO record the command
    if not self.__dirty:
      self.__dirty = True
      self.emit(SIGNAL("dataModified"))

  def save(self):
    res = self.__datas.save()
    if res[0] == KDataStatusError.STATUS_OK:
      self.__dirty = False
    return res

  def discard(self):
    self.__dirty = False

  def setBgColor(self, rows, value):
    for i in rows:
      self.__datas.setRowBGColor(i, value)
    self.notifyRowChanged(rows)

  def getRows(self, pos, rows=1):
    """
      return the list of the data
    """
    return self.__datas.getRows(pos, rows)

  def updatePath(self, path):
    self.__datas.updatePath(path)

  def getFindAndReplaceData(self):
    return self.__datas

  def getUncommentedData(self):
    return self.__datas.getUncommentedData()

class KTableDataContainer(object):
  def __init__(self, filename, root, headerInfo):
    self.__filename = filename
    self.__headerInfo = headerInfo
    self.__root = root
    self.load()

  def getRawData(self):
    return self.__data

  def checkDataModified(self):
    lmtime = os.path.getmtime(self.__filename + define.DATA_FILE_SUF)
    if lmtime != self.__lastSaveTime:
      return True
    return False

  def updatePath(self, path):
    self.__filename = path
  
  def updateData(self, headerInfo):
    """1. adjust the order of the header
       2. add the new data of the inserted header and save
    """
    if len(self.__data) == 1 or len(self.__data[0]) == 0:
      self.__headerInfo = headerInfo
      if len(self.__data) == 1:
        for h in headerInfo:
          self.__data.insert(0, [])
      return [KDataStatusError.STATUS_OK]

    orderInfo = []
    for h in headerInfo:
      f = False
      for idx in range(len(self.__headerInfo)):
        f = self.__headerInfo[idx].canConvert2(h)
        if f:
          orderInfo.append(idx)
          break
      if not f:
        orderInfo.append([self.getDefaultValue(h.dataType) \
          for i in range(len(self.__data[0]))])
    data = []
# debug--------------
    if __debug__:
      log.debug_log("org header: %s now header: %s\n org data: %s\n" 
          % ([unicode(h) for h in self.__headerInfo],
            [unicode(h) for h in headerInfo],
            self.__data))
# debug--------------
    for o in orderInfo:
      data.append(self.__data[o] if type(o) == int else o)
    data.append(self.__data[-1])

    hbk = self.__headerInfo
    dbk = self.__data
    self.__headerInfo = headerInfo
    self.__data = data
    ret = self.save()
    if ret[0] == KDataStatusError.STATUS_OK:
      KDataWarehouse.updateData(self.__filename, self.__data)
    else:
      self.__data = dbk
      self.__headerInfo = hbk
    return ret

  def __len__(self):
    return 0 if not len(self.__data) else len(self.__data[0])

  def __iter__(self):
    for hd in [d[k] for d in self.__data]:
      yield hd

  def __getitem__(self, k):
    return [d[k] for d in self.__data]

  def insert(self, position, rows = None):
    headerCnt = len(self.__headerInfo)
    if rows is None:
      row = self.getDefaultRow()
      for i in range(headerCnt):
        self.__data[i].insert(position, row[i])
      self.__data[headerCnt].insert(position, KOpts())
    else:
      pos = position
      for row in rows:
        for i in range(headerCnt):
          self.__data[i].insert(pos, row[i])
        self.__data[headerCnt].insert(pos, KOpts())
        pos = pos + 1

  def getDefaultRow(self):
    ans = []
    for h in self.__headerInfo:
      ans.append(self.getDefaultValue(h.dataType))
    return ans

  def getDefaultValue(self, dataType):
    """
    int, bool, float <-> '0'
    date <-> today in the form of 'YYYY-MM-DD HH:mm:ss'
    array type <-> '' empty string
    """
    if dataType not in define.DATA_TYPES:
      return ""

    typeIdx = define.DATA_TYPES.index(dataType)
    if typeIdx == define.BOOL_IDX or \
        typeIdx == define.INT_IDX or \
        typeIdx == define.FLOAT_IDX:
      return define.NO_TXT
    elif typeIdx == define.DATE_IDX:
      return ""
    return ""

  def remove(self, position, rows):
    for d in self.__data:
      del d[position:position + rows]
  
  def getRows(self, position, rows=1):
    """
      return the list of the data
    """
    ans = []
    for r in range(rows):
      row = []
      for c in range(len(self.__headerInfo)):
        row.append(self.__data[c][position + r])
      ans.append(row)
    return ans

  def getData(self, row, column):
    return self.__data[column][row]

  def isComment(self, row):
    return self.__data[-1][row].isComment() & KDataFlag.COMMENT > 0

  def comment(self, row):
    opt = self.__data[-1][row]
    d = opt.isComment()
    if d & KDataFlag.COMMENT:
      d &= ~KDataFlag.COMMENT
    else:
      d |= KDataFlag.COMMENT
    opt.setComment(d)

  def getRowBGColor(self, row):
    return self.__data[-1][row].bgColor()

  def setRowBGColor(self, row, value):
    self.__data[-1][row].setBgColor(value)

  def setData(self, row, column, data):
    self.__data[column][row] = data

  def load(self, fromDisk=False):
    #headerCnt = len(self.__headerInfo)
    #self.__data = [[] for hi in range(headerCnt)]
    #KPersistData.load(headerCnt, self.__data, self.__filename)
    self.__lastSaveTime = os.path.getmtime(self.__filename +
        define.DATA_FILE_SUF)
    self.__data = KDataWarehouse.getData(self.__filename, fromDisk)
    for i in range(len(self.__data[-1])):
      self.__data[-1][i] = KOpts(self.__data[-1][i])
    
  def save(self):
    for c in range(len(self.__headerInfo)):
      cr = self.checkData(self.__data[c], self.__headerInfo[c])
      if cr[0] != KDataStatusError.STATUS_OK:
        cr.append(c + 1)
        return cr

    KDataWarehouse.saveData(self.__filename)
    self.__lastSaveTime = os.path.getmtime(self.__filename +
        define.DATA_FILE_SUF)
    return [KDataStatusError.STATUS_OK]

  def checkData(self, data, header):
    if header.isUnique == define.YES_TXT:
      cs = set()
      for i in range(len(data)):
        if data[i] in cs:
          return [KDataStatusError.STATUS_ERROR_UNIQUE, i + 1]
        else:
          cs.add(data[i])
      return [KDataStatusError.STATUS_OK]
    noEmpty = header.allowEmpty == define.NO_TXT
    if noEmpty:
      for i in range(len(data)):
        if len(data[i].strip()) == 0:
          return [KDataStatusError.STATUS_ERROR_EMPTY, i + 1]

    if len(header.ref.strip()) > 0:
      strs = header.ref.strip().split(";")
      for i in range(len(data)):
        if not noEmpty and not data[i].strip():
          continue;
        if not KDataWarehouse.contains(self.__root + strs[0],
            strs[1], data[i].split(",")):
          return [KDataStatusError.STATUS_ERROR_REF, i + 1]
    return [KDataStatusError.STATUS_OK]

  def rowCount(self):
    return len(self)

  def columnCount(self):
    return len(self.__data) - 1

  def getDataList(self):
    return self.__data

  def getUncommentedData(self):
    ans = [[] for h in self.__headerInfo]
    for rowIdx in range(len(self.__data[0])):
        if not self.isComment(rowIdx):
          for c in range(len(self.__headerInfo)):
            ans[c].append(self.__data[c][rowIdx])
    return ans

class KDataStatusError(object):
  errorInfo = ["", u"数值重复, 行 %d, 列 %d", \
      u"数值不能为空, 行 %d, 列 %d", u"数值引用错误, 行 %d, 列 %d"]
  STATUS_OK, STATUS_ERROR_UNIQUE, \
    STATUS_ERROR_EMPTY, STATUS_ERROR_REF = range(len(errorInfo))

class KDataFlag(object):
  COMMENT = 1

class KOpts(object):
  def __init__(self, optsStr=''):
    self.__isComment = 0
    self.__bgColor = 0xffffff
    if optsStr:
      opts = optsStr.split(';')
      optLen = len(opts)
      self.__isComment = int(opts[0]) if optLen > 0 else 0
      self.__bgColor = int(opts[1]) if optLen > 1 else 0xffffff

  def isComment(self):
    return self.__isComment

  def setComment(self, value):
    self.__isComment = value

  def bgColor(self):
    return self.__bgColor

  def setBgColor(self, value):
    self.__bgColor = value
  '''
  @property
  def isComment(self):
    return self.__isComment

  @isComment.setter
  def isComment(self, value):
    self.__isComment = value

  @property
  def bgColor(self):
    return self.__bgColor

  @bgColor.setter
  def bgColor(self, value):
    self.__bgColor = value
  '''

  def __str__(self):
    '''
    commentFlat;colorFlag
    '''
    return "%d;%d" % (self.__isComment, self.__bgColor)

if __name__ == '__main__':
  opts = KOpts()
  print unicode(str(opts))
