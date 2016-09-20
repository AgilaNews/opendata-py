#-*- coding: utf-8 -*-
import json
import socket
import os
import logging
import logging.handlers as ih
from img.imagesaver import ImageSaver

from sqlalchemy import engine, MetaData, create_engine

root_dir = os.path.dirname(os.path.realpath(__file__))

if socket.gethostname() == "spider-1":
    run_env = "online"
elif socket.gethostname() == "sandbox-1":
    run_env = "sandbox"
else:
    run_env = "rd"

with open(os.path.join(root_dir, "conf", "config." + run_env + ".json")) as fd:
    content = fd.read()
    conf = json.loads(content)

saver = ImageSaver("ucloud", conf["ucloud"])

class WFHandler(logging.Handler):
    def __init__(self, name):
        fm = logging.Formatter("[%(asctime)s][%(filename)s:%(lineno)d][%(levelname)s]: %(message)s")
        
        self.info = ih.WatchedFileHandler(name)
        self.info.setFormatter(fm)
        
        self.err = ih.WatchedFileHandler(name + ".wf")
        self.err.setFormatter(fm)
        logging.Handler.__init__(self)
        
    def emit(self, record):
        if record.levelno <= logging.INFO:
            self.info.emit(record)
        else:
            self.err.emit(record)
                
logging.getLogger("requests").setLevel(logging.WARNING)
rootLogger = logging.getLogger("")
rootLogger.setLevel(logging.INFO)
rootLogger.addHandler(WFHandler("/data/logs/opendata_crawler/crawler.log"))

meta = MetaData()
engine = create_engine("mysql://%s:%s@%s:%s/%s?charset=%s&use_unicode=0" \
                       %(conf["mysql"]["user"], conf["mysql"]["password"], conf["mysql"]["host"], \
                         conf["mysql"]["port"], conf["mysql"]["db"], conf["mysql"]["charset"]), \
                         pool_reset_on_return = None, pool_size = 10, pool_recycle = 600,\
                         encoding = "utf8", \
                         execution_options={"autocommit": True})

meta.reflect(bind = engine)
