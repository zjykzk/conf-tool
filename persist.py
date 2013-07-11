# -*- coding: utf-8 -*-
# Author : xiaok
# 2011-08-24 10:14
import define
import data_codec as dc
import codecs
import copy

class KPersistHeader(object):
  @classmethod
  def store(cls, headerDatas, filename):
    f = codecs.open(filename, "w", define.CODEC)
    try:
      for d in  headerDatas:
        f.write(dc.KHeaderCodec.encode(d) + "\n")
    except IOError, e:
      raise WriteFileError(u"%s" % e)
    finally:
      if f:
        f.close()

  @classmethod
  def load(cls, headerDatas, filename):
    f = codecs.open(filename, "r", define.CODEC)
    try:
      id = 0
      for line in f:
        d = dc.KHeaderCodec.decode(line.strip())
        d.id = id
        headerDatas.append(d)
        id = id + 1
    except IOError, e:
      raise ReadFileError(u"%s" % e)
    finally:
      if f:
        f.close()

    return headerDatas
 
class KPersistData(object):
  @classmethod
  def store(cls, data, filename):
    columns = len(data)
    rows = len(data[0])
    finalData = []
    for i in range(rows):
      row = []
      for j in range(columns):
        row.append(u'%s' % data[j][i])
      finalData.append(dc.KDataCodec.encode(row))

    f = codecs.open(filename, "w", define.CODEC)
    try:
      f.write('\n'.join(finalData))
    except Exception, e:
      raise WriteFileError(u"写数据错误 %s" % e)
    finally:
      if f: f.close()

  @classmethod
  def load(cls, headerCnt, filename):
    f = codecs.open(filename, "r", define.CODEC)
    data = [[] for i in range(headerCnt + 1)]
    try:
      for line in f:
        row = dc.KDataCodec.decode(line.strip())
        if len(row) != headerCnt + 1:
          print len(row), row, headerCnt + 1
          raise ReadFileError(u"%s: row %d error" % (filename, len(data[0]) + 1))
        for i in range(headerCnt + 1):
          data[i].append(row[i])
    except IOError, e:
      raise ReadFileError(u"读数据错误 %s" % e)
    finally:
      if f:
        f.close()

    return data

class ReadFileError(Exception):
  def __init__(self, info):
    self.__info = info

  def __str__(self):
    return self.__info

class WriteFileError(Exception):
  def __init__(self, info):
    self.__info = info

  def __str__(self):
    return self.__info
