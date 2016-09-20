#-*- coding:utf-8 -*-
import time
import env

from sqlalchemy import select
from sqlalchemy import insert
from sqlalchemy import update
from sqlalchemy import func
from sqlalchemy import bindparam
from sqlalchemy import and_

team_table = env.meta.tables["tb_nba_team"]
cols = team_table.c

def save(values, id = None):
    if id:
        i = update(team_table).where(cols.team_id == id).values(**values)
    else:
        i = insert(team_table).values(**values)

    return env.engine.execute(i)

def getByTeamId(team_id):
    s = select([team_table]).where(cols.team_id == team_id)

    return env.engine.execute(s).first()
