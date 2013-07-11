# -*- coding: utf-8 -*-
# Author : xiaok
# 2011-08-17 11:16
from collections import deque

class KCommand(object):
  def __init__(self, model):
    self.model = model

  def do(self):
    raise "unsupported operation"

  def undo(self):
    raise "unsupported operation"

class KRowInsertCmd(KCommand):
  def __init__(self, pos, model, cnt = 1):
    super(KRowInsertCmd, self).__init__(model)
    self.__pos = pos
    self.__cnt = cnt

  def do(self):
    pass

  def undo(self):
    self.model.removeRows(self.__pos, self.__cnt)

class KRowDeleteCmd(KCommand):
  def __init__(self, position, rowDatas, model):
    super(KRowDeleteCmd, self).__init__(model)
    self.position = position
    self.rowDatas = rowDatas

  def do(self):
    pass

  def undo(self):
    self.model.insertRows(self.position, len(self.rowDatas), self.rowDatas)

class KRowOpts(KCommand):
  def __init__(self, rows, opts, model):
    super(KRowOpts, self).__init__(model)
    self.rows = rows
    self.opts = opts

  def do(self):
    pass

  def undo(self):
    self.model.updateRowsOpt(self.rows, self.opts)

class KReplaceCommand(KCommand):
  def __init__(self, rows, columns, data, model):
    self.__rows = rows
    self.__columns = columns
    self.__data = data
    self.__model = model

  def do(self):
    pass
 
  def undo(self):
    self.__model.restoreData(self.__rows, self.__columns, self.__data)

class KItemModifiedCmd(KCommand):
  def __init__(self, row, column, data, model):
    """
    data must be the QString type
    """
    super(KItemModifiedCmd, self).__init__(model)
    self.row = row
    self.column = column
    self.data = data

  def do(self):
    pass

  def undo(self):
    self.model.restoreData([self.row], [self.column], [self.data])

class KCommandContainer(KCommand):
  
  CMD_COUNT_LIMITS = 99

  def __init__(self, model=None):
    super(KCommandContainer, self).__init__(model)
    self.__cmdQue = deque()

  def addCmd(self, cmd):
    if len(self) >= KCommandContainer.CMD_COUNT_LIMITS:
      self.__cmdQue.popleft()
    self.__cmdQue.append(cmd)

  def do(self):
    pass

  def undo(self):
    l = len(self)
    while l != 0:
      self.__cmdQue.pop().undo()
      l = l - 1

  def clear(self):
    self.__cmdQue.clear()

  def __len__(self):
    return len(self.__cmdQue)

if __name__ == "__main__":
  from collections import deque
  dq = deque()
  dq.append(1)
  dq.append(2)
  dq.append(3)
  print dq
  dq.append(4)
  dq.append(5)
  print dq
