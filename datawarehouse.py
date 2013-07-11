# -*- coding: utf-8 -*-
# Author : xiaok
# 2011-08-24 11:32
from persist import *
class KData(object):
  def __init__(self, filename):
    self.__headerInfo = []
    self.__data = []
    self.__filename = filename

  def headerInfo(self):
    return self.__headerInfo

  def setHeaderInfo(self, headerInfo):
    self.__headerInfo = headerInfo

  def data(self):
    return self.__data

  def setData(self, d):
    self.__data = d

  def id(self):
    return self.__filename

  def setID(self, filename):
    self.__filename = filename

  def contains(self, headerName, data):
    idx = 0
    for h in self.__headerInfo:
      if h.name == headerName:
        for d in data:
          if d not in self.__data[idx]:
            return False
        return True
      idx = idx + 1
    return False

class KCacheLRU(object):
  CAPACITY = 18

  def __init__(self):
    self.__swap = []

  def hit(self, filename):
    for d in self.__swap:
      if filename == d.id():
        return d

    return None

  def remove(self, filename):
    fd = None
    for d in self.__swap:
      if filename == d.id():
        fd = d
        break

    if fd is not None:
      self.__swap.remove(fd)

  def add(self, d):
    if d in self.__swap:
      self.__swap.remove(d)

    if len(self.__swap) == KCacheLRU.CAPACITY:
      del self.__swap[0]

    self.__swap.append(d)

class KCachedPolicy(object):
  KCAHCED_OPEND, KCACHED_CACHED, KCACHED_DISCARD = range(3)

class KDataWHInternal(object):
  def __init__(self):
    self.openedData = {}
    self.cached = KCacheLRU()

  def getData(self, filename):
    ans = self.openedData.get(filename, None)
    if ans is not None:
      return ans

    ans = self.cached.hit(filename)
    if ans is not None:
      return ans

    return None

  def removeData(self, filename):
    ans = self.openedData.get(filename, None)
    if ans is not None:
      del self.openedData[filename]
      return

    self.cached.remove(filename)

  def updateFilename(self, newFn, oldFn):
    d = self.openedData.get(oldFn, None)
    if d is not None:
      d.setID(newFn)
      self.openedData[d.id()] = d
      del self.openedData[oldFn]
      return
    d = self.cached.hit(oldFn)
    if d is not None:
      d.setID(newFn)
      self.cached.add(d)

class KDataWarehouse(object):
  instance = KDataWHInternal()

  @classmethod
  def getHeaderData(cls, filename, refresh = True, \
      cachedPolicy=KCachedPolicy.KCAHCED_OPEND):
    d = KDataWarehouse.openData(filename, cachedPolicy) if refresh \
        else KDataWarehouse.instance.getData(filename)
    return d.headerInfo()

  @classmethod
  def getData(cls, filename, refresh = True, \
      cachedPolicy=KCachedPolicy.KCAHCED_OPEND):
    d = KDataWarehouse.openData(filename, cachedPolicy) if refresh \
        else KDataWarehouse.instance.getData(filename)
    return d.data()
  
  @classmethod
  def updateData(cls, filename, data):
    d = KDataWarehouse.instance.getData(filename)
    d.setData(data)
    KDataWarehouse.saveData(filename)

  @classmethod
  def contains(cls, filename, headerName, data):
    d = KDataWarehouse.instance.getData(filename)
    if d is None:
      d = KDataWarehouse.openData(filename, KCachedPolicy.KCACHED_CACHED)
    return d.contains(headerName, data)

  @classmethod
  def setHeaderData(cls, filename, headerData):
    KDataWarehouse.instance.getData(filename).setHeaderInfo(headerData)

  @classmethod
  def openData(cls, filename, policy):
    d = KData(filename)
    KPersistHeader.load(d.headerInfo(), filename + define.HEADER_FILE_SUF)
    d.setData(KPersistData.load(len(d.headerInfo()),
      filename + define.DATA_FILE_SUF))
    if policy == KCachedPolicy.KCAHCED_OPEND:
      KDataWarehouse.instance.openedData[d.id()] = d
    elif policy == KCachedPolicy.KCACHED_CACHED:
      KDataWarehouse.instance.cached.add(d)
    return d

  @classmethod
  def saveHeader(cls, filename):
    d = KDataWarehouse.instance.getData(filename)
    KPersistHeader.store(d.headerInfo(), filename + define.HEADER_FILE_SUF)

  @classmethod
  def saveData(cls, filename):
    d = KDataWarehouse.instance.getData(filename)
    KPersistData.store(d.data(), filename + define.DATA_FILE_SUF)

  @classmethod
  def closeData(cls, filename):
    d = KDataWarehouse.instance.openedData.get(filename, None)
    if d is None: # must check here, since this function is called when delete file/fold and close tab
      return
    KDataWarehouse.instance.cached.add(d)
    del KDataWarehouse.instance.openedData[filename]
  
  @classmethod
  def removeData(cls, filename):
    KDataWarehouse.instance.removeData(filename)

  @classmethod
  def updateFilename(cls, newFn, oldFn):
    KDataWarehouse.instance.updateFilename(newFn, oldFn)
