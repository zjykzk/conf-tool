# -*- coding: utf-8 -*-
# Author : zenk
# 2013-07-05 20:32
from os import path
from collections import defaultdict
import re

from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QFileDialog
from PyQt4.QtGui import QGridLayout
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QIntValidator
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QVBoxLayout

from PyQt4.QtCore import SIGNAL

import xlrd

class ReplaceI18NDialog(QDialog):
  def __init__(self, config_name, parent=None):
    super(ReplaceI18NDialog, self).__init__(parent)
    self.parent = parent
    grid_layout = QGridLayout()
    grid_layout.addWidget(QLabel(u'表单名字/序号'), 0, 0)
    self.sheet_index_input = QLineEdit(config_name, self)
    grid_layout.addWidget(self.sheet_index_input, 0, 1)

    grid_layout.addWidget(QLabel(u'列'), 1, 0)
    self.column_input = QLineEdit("1", self)
    int_validator = QIntValidator()
    int_validator.setRange(1, 100)
    self.column_input.setValidator(int_validator)
    grid_layout.addWidget(self.column_input, 1, 1)

    grid_layout.addWidget(QLabel(u'文件'), 2, 0)
    self.file_input = QLineEdit("", self)
    grid_layout.addWidget(self.file_input, 2, 1)
    select_file_btn = QPushButton(u'选择')
    grid_layout.addWidget(select_file_btn, 2, 2)

    do_btn = QPushButton(u'替换')
    main_layout = QVBoxLayout()
    main_layout.addLayout(grid_layout)
    main_layout.addWidget(do_btn)
    self.setLayout(main_layout)

    self.connect(select_file_btn, SIGNAL("clicked()"), self.select_file)
    self.connect(do_btn, SIGNAL("clicked()"), self.replace)

  def select_file(self):
    filename = unicode(QFileDialog.getOpenFileName(self, "Open File",
                                           "", "Excel (*.xls)"))
    if not path.exists(filename):
      QMessageBox.information(self, u"i18n替换",
          u'文件:%s不存在' % filename)
      return
    book = xlrd.open_workbook(filename)
    sheet_name = unicode(self.sheet_index_input.text())
    sheet = None
    if sheet_name in book.sheet_names():
      sheet = book.sheet_by_name(sheet_name)
    elif re.match("\d+", sheet_name):
      sheet = book.sheet_by_index(int(sheet_name) - 1)
    if not sheet:
      QMessageBox.information(self, u'i18n替换',
          u'表单名字/索引:%s不存在' % sheet_name)
      return
    self.text_dic = defaultdict(str)
    for k, v in zip(sheet.col_values(0),
        sheet.col_values(int(unicode(self.column_input.text())))):
        self.text_dic[k] = v
    self.file_input.setText(filename)

  def replace(self):
    not_replaced = self.parent.replace_i18n(self.text_dic)
    QMessageBox.information(self, u'i18n替换', 
        u'替换成功%s' % ('' if not not_replaced else u'\n以下字符串没有被替换:%s' % not_replaced))
    self.close()
