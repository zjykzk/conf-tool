# -*- coding: utf-8 -*-
# Author : xiaok
# 2011-08-05 15:19
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import genericdelegates as gd
import define
import refeditor

class KNameColumnDelegate(gd.PlainTextColumnDelegate):
  def __init__(self):
    super(KNameColumnDelegate, self).__init__()
    validator = QRegExpValidator(QRegExp("^[_a-zA-Z][_a-zA-Z0-9]+$"), self)
    self.validator = validator
    
  def getValidator(self):
    return self.validator

class KDataTypeColumnDelegate(QItemDelegate):
  def __init__(self, parent=None):
    super(KDataTypeColumnDelegate, self).__init__(parent)

  def createEditor(self, parent, option, index):
    combobox = QComboBox(parent)
    for datetype in define.DATA_TYPES:
      combobox.addItem(datetype)
    return combobox

  def setEditorData(self, editor, index):
    value = index.model().data(index, Qt.DisplayRole).toString()
    editor.setCurrentIndex(editor.findText(value))

  def setModelData(self, editor, model, index):
    model.setData(index, QVariant(editor.currentText()))

class KCSColumnDelegate(gd.PlainTextColumnDelegate):
  def __init__(self):
    super(KCSColumnDelegate, self).__init__()
    validator = QRegExpValidator(QRegExp("^(c|s|cs)$"), self)
    self.validator = validator
    
  def getValidator(self):
    return self.validator

class KIsUniqueColumnDelegate(gd.BoolColumnDelegate):
  pass

class KAllowEmptyColumnDelegate(gd.BoolColumnDelegate):
  pass

class I18NEmptyColumnDelegate(gd.BoolColumnDelegate):
  pass

class KRefColumnDelegate(QItemDelegate):
  def __init__(self, projectDir, filename, parent=None):
    super(KRefColumnDelegate, self).__init__(parent)
    self.__proDir = projectDir
    self.__filename = filename

  def createEditor(self, parent, option, index):
    refEditor = refeditor.KRefAddrEditor(self.__proDir, self.__filename,\
        parent)
    return refEditor

  def setEditorData(self, editor, index):
    value = index.model().data(index, Qt.DisplayRole).toString()
    editor.setCurrentSelected(value)
    
  def setModelData(self, editor, model, index):
    model.setData(index, QVariant(editor.getRelSelectData()))

class KNoteColumnDelegate(gd.PlainTextColumnDelegate):
  def __init__(self, parent=None):
    super(KNoteColumnDelegate, self).__init__(parent)

  def createEditor(self, parent, option, index):
    lineedit = QTextEdit(parent)
    validator = self.getValidator()
    if validator is not None:
      lineedit.setValidator(validator)
    return lineedit

  def setEditorData(self, editor, index):
    value = index.model().data(index, Qt.DisplayRole).toString()
    editor.setText(value)

  def setModelData(self, editor, model, index):
    model.setData(index, QVariant(editor.toPlainText()))
