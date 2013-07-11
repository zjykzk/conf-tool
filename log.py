# -*- coding: utf-8 -*-
# Author : xiaok
# 2011-08-02 12:52
import codecs
import define

def error_log(errorStr):
  fn = codecs.open("log.log", "at", define.CODEC)
  try:
    fn.write(errorStr)
    fn.write("\n")
  finally:
    fn.close()

def debug_log(info):
  fn = codecs.open("log.log", "at", define.CODEC)
  try:
    fn.write(info)
    fn.write("\n")
  finally:
    fn.close()

if __name__ == "__main__":
  error_log(u"test测试%s" % 'test')
