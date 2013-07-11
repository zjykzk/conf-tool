# -*- coding: utf-8 -*-
# Author : xiaok
# 2011-08-24 11:24

class Data(object):
  def __init__(self, header, data):
    self.__headerInfo = header
    self.__data = data

  def headerInfo(self):
    return self.__headerInfo

  def data(self):
    return self.__data

class CacheLRU(object):
  def __init__(self):
    self.__opened = []
    self.__swap = []

  def addOpenedData(
