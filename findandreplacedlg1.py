#!/usr/bin/env python

# -*- coding: utf-8 -*-
import re
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import ui_findandreplacedlg

MAC = "qt_mac_set_native_menubar" in dir()


class KFindAndReplaceDlg(QDialog,
        ui_findandreplacedlg.Ui_FindAndReplaceDlg):

    def __init__(self, data, parent=None):
      super(KFindAndReplaceDlg, self).__init__(parent)
      self.__data = data
      self.__parent = parent
      self.__row = 0
      self.__column = 0
      self.setupUi(self)
      if not MAC:
          self.findButton.setFocusPolicy(Qt.NoFocus)
          self.replaceButton.setFocusPolicy(Qt.NoFocus)
          self.replaceAllButton.setFocusPolicy(Qt.NoFocus)
          self.closeButton.setFocusPolicy(Qt.NoFocus)
      self.updateUi()

    @pyqtSignature("QString")
    def on_findLineEdit_textEdited(self, text):
      self.updateUi()

    def makeRegex(self):
      findText = unicode(self.findLineEdit.text())
      if unicode(self.syntaxComboBox.currentText()) == "Literal":
          findText = re.escape(findText)
      flags = re.MULTILINE|re.DOTALL|re.UNICODE
      if not self.caseCheckBox.isChecked():
          flags |= re.IGNORECASE
      if self.wholeCheckBox.isChecked():
          findText = r"\b%s\b" % findText
      return re.compile(findText, flags)


    @pyqtSignature("")
    def on_findButton_clicked(self):
      regex = self.makeRegex()
      ccnt = len(self.__data)
      rcnt = len(self.__data[0])
      while self.__row < rcnt:
        match = regex.search(self.__data[self.__column][self.__row])
        if match is not None:
          self.__parent.findStr(self.__row, self.__column)
          return
        self.__column = self.__column + 1
        if self.__column >= ccnt:
          self.__column = 0
          self.__row = self.__row + 1
      self.__row = 0
      self.__column = 0
      QMessageBox.information(self, u"finds/repace", u"cannot find'%s'" % \
          self.findLineEdit.text())

    @pyqtSignature("")
    def on_replaceButton_clicked(self):
      regex = self.makeRegex()
      self.__data[self.__row][self.__column] = \
        regex.sub(unicode(self.replaceLineEdit.text()), \
          self.__data[self.__row][self.__column])
      self.__parent.replaceStr([self.__row], [self.__column])

    @pyqtSignature("")
    def on_replaceAllButton_clicked(self):
      regex = self.makeRegex()
      ccnt = len(self.__data)
      rcnt = len(self.__data[0])
      rows = []
      columns = []
      while row != rcnt:
        match = regex.search(self.__data[self.__row][self.__column])
        if match is not None:
          self.__data[self.__row][self.__column] = \
            regex.sub(unicode(self.replaceLineEdit.text()), 
              self.__data[self.__row][self.__column])
          rows.append(self.__row)
          columns.append(self.__column)
        self.__column = self.__column + 1
        if self.__column >= ccnt:
          self.__column = 0
          self.__row = self.__row + 1
      self.__parent.replaceStr(rows, columns)
      QMessageBox.information(self, u"find/replace", u"replace finished")
       
    def updateUi(self):
      enable = not self.findLineEdit.text().isEmpty()
      self.findButton.setEnabled(enable)
      self.replaceButton.setEnabled(enable)
      self.replaceAllButton.setEnabled(enable)

if __name__ == "__main__":
    import sys

    text = """US experience shows that, unlike traditional patents,
software patents do not encourage innovation and R&D, quite the
contrary. In particular they hurt small and medium-sized enterprises
and generally newcomers in the market. They will just weaken the market
and increase spending on patents and litigation, at the expense of
technological innovation and research. Especially dangerous are
attempts to abuse the patent system by preventing interoperability as a
means of avoiding competition with technological ability.
--- Extract quoted from Linus Torvalds and Alan Cox's letter
to the President of the European Parliament
http://www.effi.org/patentit/patents_torvalds_cox.html"""

    def found(where):
        print "Found at %d" % where

    def nomore():
        print "No more found"

    app = QApplication(sys.argv)
    form = FindAndReplaceDlg(text)
    form.connect(form, SIGNAL("found"), found)
    form.connect(form, SIGNAL("notfound"), nomore)
    form.show()
    app.exec_()
    print form.text()

