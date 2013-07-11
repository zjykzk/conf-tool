#!/usr/bin/env python
# Copyright (c) 2007-8 Qtrac Ltd. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 2 of the License, or
# version 3 of the License, or (at your option) any later version. It is
# provided for educational purposes and is distributed in the hope that
# it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
# the GNU General Public License for more details.

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import richtextedit
import define

class GenericDelegate(QItemDelegate):
  def __init__(self, parent=None):
    super(GenericDelegate, self).__init__(parent)
    self.delegates = {}

  def insertColumnDelegate(self, column, delegate):
    delegate.setParent(self)
    self.delegates[column] = delegate

  def removeColumnDelegate(self, column):
    if column in self.delegates:
      del self.delegates[column]

  def paint(self, painter, option, index):
    delegate = self.delegates.get(index.column())
    if delegate is not None:
      delegate.paint(painter, option, index)
    else:
      QItemDelegate.paint(self, painter, option, index)

  def createEditor(self, parent, option, index):
    delegate = self.delegates.get(index.column())
    if delegate is not None:
      return delegate.createEditor(parent, option, index)
    else:
      return QItemDelegate.createEditor(self, parent, option,
                                            index)
  def setEditorData(self, editor, index):
    delegate = self.delegates.get(index.column())
    if delegate is not None:
      delegate.setEditorData(editor, index)
    else:
      QItemDelegate.setEditorData(self, editor, index)

  def setModelData(self, editor, model, index):
    delegate = self.delegates.get(index.column())
    if delegate is not None:
      delegate.setModelData(editor, model, index)
    else:
      QItemDelegate.setModelData(self, editor, model, index)

class DateColumnDelegate(QItemDelegate):
  def __init__(self, format="yyyy-MM-dd hh:mm:ss", parent=None):
    super(DateColumnDelegate, self).__init__(parent)
    self.format = QString(format)

  def createEditor(self, parent, option, index):
    dateEdit = QDateTimeEdit(parent)
    #dateEdit.setMinimumDate(QDate.currentDate().addDays(-365));
    #dateEdit.setMaximumDate(QDate.currentDate().addDays(365));
    dateEdit.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
    dateEdit.setDisplayFormat(self.format)
    dateEdit.setCalendarPopup(True)
    return dateEdit

  def setEditorData(self, editor, index):
    data = index.model().data(index, Qt.DisplayRole)
    value = QVariant("1999-01-01 00:00:00").toDateTime() if not unicode(data.toString()) else data.toDateTime()
    editor.setDateTime(value)

  def setModelData(self, editor, model, index):
    datetime = editor.dateTime()
    model.setData(index, QVariant(datetime.toString(self.format) if datetime.date().year() != 1999 else ""))

class KQLineEdit(QLineEdit):
  def __init__(self, parent):
    super(QLineEdit, self).__init__(parent)
    self.lastKey = 0

  """
  def keyPressEvent(self, event):
    if event.key() == Qt.Key_Return:
    return QLineEdit.keyPressEvent(self, event)
  """

  def event(self, event):
    if event.type() == QEvent.KeyPress:
      lk = self.lastKey
      self.lastKey = event.key()
      if event.key() == Qt.Key_Backspace:
        if lk == Qt.Key_Shift:
          self.insert("\n")
          return True
    return QLineEdit.event(self, event)

class PlainTextColumnDelegate(QItemDelegate):
  def __init__(self, parent=None):
    super(PlainTextColumnDelegate, self).__init__(parent)

  def createEditor(self, parent, option, index):
    lineedit = KQLineEdit(parent)
    validator = self.getValidator()
    if validator is not None:
      lineedit.setValidator(validator)
    return lineedit

  def setEditorData(self, editor, index):
    value = index.model().data(index, Qt.DisplayRole).toString()
    editor.setText(value)

  def setModelData(self, editor, model, index):
    model.setData(index, QVariant(editor.text()))

  def getValidator(self):
    return None

class BoolColumnDelegate(QItemDelegate):
  def __init__(self, parent=None):
    super(BoolColumnDelegate, self).__init__(parent)

  def createEditor(self, parent, option, index):
    booledit = QCheckBox(parent)
    return booledit

  def setEditorData(self, editor, index):
    value = index.model().data(index, Qt.DisplayRole).toString()
    editor.setChecked(self.getCheckState(value) == \
          Qt.Checked)

  def setModelData(self, editor, model, index):
    model.setData(index, QVariant(self.getCheckText(editor.checkState())))

  def getCheckText(self, checked):
    return define.CHECKED_TEXT if Qt.Checked == checked \
        else define.UNCHECKED_TEXT

  def getCheckState(self, text):
    return Qt.Checked if text == define.CHECKED_TEXT else \
        Qt.Unchecked

class RichTextColumnDelegate(QItemDelegate):

  def __init__(self, parent=None):
    super(RichTextColumnDelegate, self).__init__(parent)

  def paint(self, painter, option, index):
    text = index.model().data(index, Qt.DisplayRole).toString()
    palette = QApplication.palette()
    document = QTextDocument()
    document.setDefaultFont(option.font)
    if option.state & QStyle.State_Selected:
        document.setHtml(QString("<font color=%1>%2</font>") \
                .arg(palette.highlightedText().color().name()) \
                .arg(text))
    else:
      document.setHtml(text)
      painter.save()
      color = palette.highlight().color() \
          if option.state & QStyle.State_Selected \
          else QColor(index.model().data(index,
                  Qt.BackgroundColorRole))
      painter.fillRect(option.rect, color)
      painter.translate(option.rect.x(), option.rect.y())
      document.drawContents(painter)
      painter.restore()

  def sizeHint(self, option, index):
    text = index.model().data(index).toString()
    document = QTextDocument()
    document.setDefaultFont(option.font)
    document.setHtml(text)
    return QSize(document.idealWidth() + 5,
                   option.fontMetrics.height())

  def createEditor(self, parent, option, index):
    lineedit = richtextedit.RichTextLineEdit(parent)
    return lineedit

  def setEditorData(self, editor, index):
    value = index.model().data(index, Qt.DisplayRole).toString()
    editor.setHtml(value)

  def setModelData(self, editor, model, index):
    model.setData(index, QVariant(editor.toSimpleHtml()))

class DoubleColumnDelegate(PlainTextColumnDelegate):
  def __init__(self, validator = QDoubleValidator(),  parent=None):
    super(DoubleColumnDelegate, self).__init__(parent)
    self.__validator = validator
  def getValidator(self):
    return self.__validator

class IntegerColumnDelegate(PlainTextColumnDelegate):
  def __init__(self, validator = QIntValidator(), parent=None):
    super(IntegerColumnDelegate, self).__init__(parent)
    self.__validator = validator

  def getValidator(self):
    return self.__validator

