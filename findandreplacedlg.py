# -*- coding: utf-8 -*-
# Author : xiaok
# 2011-08-29 11:37
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
      """
      data must implement some intefaces followed:
        getData(rowIdx, columnIdx)
        setData(rowIdx, columnIdx, data)
        rowCount()
        columnCount()
      """
      super(KFindAndReplaceDlg, self).__init__(parent)
      self.__tableData = data
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
      ccnt = self.__tableData.columnCount()
      rcnt = self.__tableData.rowCount()
      while self.__row < rcnt:
        self.__column = self.__column + 1
        if self.__column >= ccnt:
          self.__column = 0
          self.__row = self.__row + 1
        if self.__row >= rcnt:
          break
        match = regex.search(self.__tableData.getData(self.__row, self.__column))
        if match is not None:
          self.__parent.findStr(self.__row, self.__column)
          return
      self.__row = 0
      self.__column = 0
      QMessageBox.information(self, u"查找/替换", u"'%s' 查询到底" % \
          self.findLineEdit.text())

    @pyqtSignature("")
    def on_replaceButton_clicked(self):
      regex = self.makeRegex()
      match = regex.search(self.__tableData.getData(self.__row,self.__column))
      if match is None:
        return self.on_findButton_clicked()
      bk = self.__tableData.getData(self.__row,self.__column)
      self.__tableData.setData(self.__row, self.__column,
          regex.sub(unicode(self.replaceLineEdit.text()),
          self.__tableData.getData(self.__row, self.__column)))
      self.__parent.replaceStr([self.__row], [self.__column], [bk])

    @pyqtSignature("")
    def on_replaceAllButton_clicked(self):
      regex = self.makeRegex()
      ccnt = self.__tableData.columnCount()
      rcnt = self.__tableData.rowCount()
      rows = []
      columns = []
      self.__column = 0
      self.__row = 0
      bkdata = []
      while self.__row != rcnt:
        self.__column = self.__column + 1
        if self.__column >= ccnt:
          self.__column = 0
          self.__row = self.__row + 1
        if self.__row >= rcnt:
          break
        match = regex.search(self.__tableData.getData(self.__row,self.__column))
        if match is not None:
          bkdata.append(self.__tableData.getData(self.__row,self.__column))
          self.__tableData.setData(self.__row,self.__column, 
            regex.sub(unicode(self.replaceLineEdit.text()), 
              self.__tableData.getData(self.__row,self.__column)))
          rows.append(self.__row)
          columns.append(self.__column)
      self.__parent.replaceStr(rows, columns, bkdata)
      QMessageBox.information(self, u"查找/替换", u"替换完成")
       
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
    form = KFindAndReplaceDlg(text)
    form.connect(form, SIGNAL("found"), found)
    form.connect(form, SIGNAL("notfound"), nomore)
    form.show()
    app.exec_()
    print form.text()


