# -*- coding: utf-8 -*-
# Author : xiaok
# 2011-08-02 11:15
CODEC = "utf-8"
APP_INFO_FILE = ".appinfo"
DATA_FILE_SUF = ".dk" #数据文件的扩张名
HEADER_FILE_SUF = ".zk" #表头文件的扩展名
HEADER_DATA_COLUMN_COUNT = 8
NAME, DATATYPE, CS, ISUNIQUIE, ALLOWEMPTY, IS_I18N, REFADDR, NOTE = \
  range(HEADER_DATA_COLUMN_COUNT)

CHECKED_TEXT = u"√"
UNCHECKED_TEXT = u"×"

YES_TXT = "1"
NO_TXT = "0"

DATA_TYPES = ["bool", "int", "string", "double", "date", "bool[]", \
    "int[]", "string[]", "double[]"]
BOOL_IDX, INT_IDX, STR_IDX, FLOAT_IDX, DATE_IDX, BOOL_ARR_IDX, \
    INT_ARR_IDX, STR_ARR_IDX, FLOAT_ARR_IDX = range(len(DATA_TYPES))
