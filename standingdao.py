#-*- coding:utf-8 -*-
import time
import env

from sqlalchemy import select
from sqlalchemy import insert
from sqlalchemy import update
from sqlalchemy import func
from sqlalchemy import bindparam
from sqlalchemy import and_

table = env.meta.tables["tb_nba_standing"]
cols = table.c

def get_by_season_and_team(season_year, team_id):
    s = select([table]).where(
        and_(cols.season_year == season_year, cols.team_id == team_id))
    return env.engine.execute(s).first()

def save(values):
    values["update_time"] = time.time()
    if not get_by_season_and_team(values["season_year"], values["team_id"]):
        s = insert(table).values(**values)
    else:
        s = update(table).where(and_(cols.season_year == values["season_year"], cols.team_id == values["team_id"])).values(**values)

    return env.engine.execute(s)    
