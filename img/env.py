#-*- coding: utf-8 -*-
from constants import DB_HOST as s_dbhost
from constants import DB_PORT as s_dbport
from constants import DB_USER as s_dbuser
from constants import DB_PASSWD as s_dbpasswd
from constants import DB_DB as s_dbdb
from constants import DB_MAXCONN as s_maxconn
from constants import DB_CHARSET as s_dbcharset

from sqlalchemy import MetaData
from sqlalchemy import create_engine
import logging
import logging.handlers as ih

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
rootLogger.addHandler(WFHandler("/data/logs/banews-img/banews-img.log"))

meta = MetaData()
engine = create_engine("mysql://%s:%s@%s:%s/%s?charset=%s&use_unicode=0" \
                       %(s_dbuser, s_dbpasswd, s_dbhost, s_dbport, s_dbdb, s_dbcharset),
                       pool_reset_on_return=None, pool_size=s_maxconn, pool_recycle=600,\
                       encoding=s_dbcharset, execution_options={"autocommit":True})

meta.reflect(bind = engine)
                       

        
        
        
    
