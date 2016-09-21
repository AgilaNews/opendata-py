#-*- coding: utf-8 -*-
import time
import env

from sqlalchemy import select
from sqlalchemy import insert
from sqlalchemy import update
from sqlalchemy import func
from sqlalchemy import bindparam
from sqlalchemy import and_

table = env.meta.tables["tb_nba_season"]
cols = table.c

def getByYear(year):
    s = select([table]).where(cols.year == year)
    return env.engine.execute(s).first()
