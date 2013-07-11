# -*- coding: utf-8 -*-
# Author : zenk
# 2012-11-01 17:38
import win32clipboard 
import win32con 

def getClipboardText(): 
  win32clipboard.OpenClipboard() 
  try:
    result = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
  except Exception:
    print 'data error'
    return ""

  win32clipboard.CloseClipboard() 
  return result 

def setClipboardText(aString):
  win32clipboard.OpenClipboard()
  win32clipboard.EmptyClipboard() 
  win32clipboard.SetClipboardData(win32con.CF_TEXT, aString) 
  win32clipboard.CloseClipboard() 

if __name__ == "__main__":
  print getClipboardText() 
  setClipboardText("test")
  print getClipboardText() 
