# -*- coding: utf-8 -*-
# Author : zenk
# 2012-04-16 10:45

import itertools

def checkArrayLength(elements):
  """
  >>> checkArrayLength([["1,2"]])
  (True, 0, 0)
  >>> checkArrayLength([["1,2"], ["2"]])
  (False, 0, 1)
  >>> checkArrayLength([["1,2"], ["2,1"]])
  (True, 0, 0)
  """
  if not elements:
    return (True, 0, 0)
  for rowIdx in range(len(elements[0])):
    ele_count = -1
    columnIdx = 0
    for elist in elements:
      arrayData = elist[rowIdx].strip(',')
      cur_ele_count = len(arrayData.split(',')) if arrayData else 0
      if ele_count == -1:
        ele_count = cur_ele_count
      elif ele_count != cur_ele_count:
        return (False, rowIdx, columnIdx)
      columnIdx = columnIdx + 1
  return (True, 0, 0)

def checkResource(reses, dirs):
  """
  检查资源文件，只检查与配置表中prefab相对应的bundle文件是否存在

  >>> checkResource([["library.pdf","whatsnew.pdf"]], ["E:\doc"])
  (0, None, None) 
  """
  import os
  notexistres = []
  notexistd = []
  for res, d in zip(reses, dirs):
    if not res:
      continue
    failedres = []
    for r in res:
      found = False
      for root, dirs, files in os.walk(d):
        if r in files:
          found = True
          break
      if not found:
        failedres.append(r)

    if failedres:
      notexistres.append(failedres)
      notexistd.append(d)

  return (1, notexistres, notexistd) if notexistres else (0, None, None)

if __name__ == "__main__":
  import doctest
  doctest.testmod()
