# -*- coding: utf-8 -*-
# Author : xiaok
# 2011-08-05 18:02
import os
import codecs

from PyQt4.QtCore import *
from PyQt4.QtGui import  *

import data_codec as dc
import define

class KRefAddrEditor(QWidget):
  def __init__(self, projectDir, filename, parent = None):
    super(KRefAddrEditor, self).__init__(parent)
    sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    self.setSizePolicy(sizePolicy)
    self.tableCB = QComboBox()
    self.tableCB.setSizePolicy(sizePolicy)
    self.tableHeaderCB = QComboBox()
    self.tableHeaderCB.setSizePolicy(sizePolicy)
    layout = QHBoxLayout()
    layout.addWidget(self.tableCB)
    layout.addWidget(self.tableHeaderCB)
    self.setLayout(layout)
    self.__paths = [""]
    self.__headers = [[""]]
    self.__projectDir = projectDir
    self.__curFilename = filename + define.HEADER_FILE_SUF
    self.getHeaderInfo(projectDir)
    for idx in range(len(self.__paths)):
      self.tableCB.addItem(os.path.basename(self.__paths[idx]))
    self.selectTable(0)
    self.connect(self.tableCB, SIGNAL("currentIndexChanged(int)"),
        self.selectTable)

  def selectTable(self, index):
    self.tableHeaderCB.clear()
    for t in self.__headers[index]:
      self.tableHeaderCB.addItem(t)

  def getHeaderInfo(self, projectDir):
    for path in os.listdir(projectDir):
      npath = projectDir + os.sep + path
      #npath = projectDir + "/" + path
      isFile = os.path.isfile(npath)
      if isFile and \
          path.endswith(define.HEADER_FILE_SUF):
         if npath == self.__curFilename:
           continue
         f = codecs.open(npath, 'r', define.CODEC)
         types = []
         try:
           for line in f:
             eles = line.split(",")
             if eles[1] == define.DATA_TYPES[define.INT_IDX]:
               types.append(eles[0])
         except IOError, e:
           raise u"select ref-address error: %s" % e
         finally:
           if f:
            f.close()
         if len(types):
           self.__paths.append(npath[:-len(define.DATA_FILE_SUF)])
           self.__headers.append(types)
      elif not isFile:
        self.getHeaderInfo(npath)
  
  SPLIT_DEL = ";"

  def setCurrentSelected(self, value):
    if value.isEmpty():
      return
    th = unicode(value).split(KRefAddrEditor.SPLIT_DEL)
    tableName = os.path.basename(th[0])
    headerName = th[1]
    idx = self.tableCB.findText(tableName)
    if idx == -1:
      return
    self.tableCB.setCurrentIndex(idx)
    self.selectTable(idx)
    idx = self.tableHeaderCB.findText(headerName)
    if idx != -1:
      self.tableHeaderCB.setCurrentIndex(idx)

  def getRelSelectData(self):
    idx = self.tableCB.currentIndex()
    if idx == 0:
      return ""
    return self.__paths[idx][len(self.__projectDir):] + \
      KRefAddrEditor.SPLIT_DEL + \
      self.tableHeaderCB.currentText()
