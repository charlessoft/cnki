# -*- coding: utf-8 -*-
import logging
import logging.handlers
# logging.basicConfig(level=logging.DEBUG,
#                     format="%(asctime)s %(threadName)s %(filename)s %(funcName)s %(lineno)s %(levelname)s - %(message)s",
#                     datefmt='%m-%d %H:%M',
#                     filename='spiderlog.log',
#                     filemode='ab')

formatter = logging.Formatter(
    "%(asctime)s %(threadName)s %(filename)s %(funcName)s %(lineno)s %(levelname)s - %(message)s")
fh = logging.handlers.RotatingFileHandler('spiderlog.log', maxBytes=200*1024*1024, backupCount=9)
fh.setLevel(logging.DEBUG)

fh.setFormatter(formatter)


logger = logging.getLogger('cnki')
# 设置logger的level为DEBUG
logger.setLevel(logging.DEBUG)
# 创建一个输出日志到控制台的StreamHandler
hdr = logging.StreamHandler()
# formatter = logging.Formatter('[%(asctime)s] %(name)s:%(levelname)s: %(message)s')
formatter = logging.Formatter(
    "%(asctime)s  %(filename)s %(funcName)s %(lineno)s %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S")
hdr.setFormatter(formatter)
# 给logger添加上handler
logger.addHandler(hdr)
logger.addHandler(fh)