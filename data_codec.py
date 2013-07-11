# -*- coding: utf-8 -*-
# Author : xiaok
# 2011-08-05 16:12
import copy

import table_header as th

COMMA = "\u2c"
NEWLINE= "\ua"

class KHeaderCodec(object):
  """
  encode the header data
  """

  @classmethod
  def encode(c, headerData):
    note = headerData.note[:]
    return u"%s,%s,%s,%s,%s,%s,%s,%s" % (headerData.name, headerData.dataType,
        headerData.cs, headerData.isUnique, headerData.allowEmpty,
        headerData.isI18n, headerData.ref,
        note.replace(",", COMMA).replace("\n", NEWLINE))

  @classmethod
  def decode(c, strData):
    eles = strData.split(",")
    return th.KHeaderData(eles[0], eles[1], eles[2],
        eles[3], eles[4], eles[6], eles[7].replace(NEWLINE,
          "\n").replace(COMMA, ","), eles[5])

class KDataCodec(object):
  """
  enocode the row of the data
  """
  @classmethod
  def encode(c, row):
    return ",".join([t.replace(",",
      COMMA).replace("\n", NEWLINE) for t in row])

  @classmethod
  def decode(c, strData):
    eles = strData.split(",")
    return [e.replace(COMMA, ",").replace(NEWLINE, "\n") for e in eles]
