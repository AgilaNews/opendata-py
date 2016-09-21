#-*- coding:utf-8 -*-
import time
import env

from sqlalchemy import select
from sqlalchemy import insert
from sqlalchemy import update
from sqlalchemy import func
from sqlalchemy import bindparam
from sqlalchemy import and_

table = env.meta.tables["tb_nba_match"]
cols = table.c

def getByGameId(game_id):
    s = select([table]).where(cols.game_id == game_id)
    return env.engine.execute(s).first()

def save(values, game_id = None):
    if game_id:
        s = update(table).where(cols.game_id == game_id).values(**values)
    else:
        s = insert(table).values(**values)

    return env.engine.execute(s)
        
