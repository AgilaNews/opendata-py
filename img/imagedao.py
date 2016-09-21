#-*- coding: utf-8 -*-
import time
import env

from sqlalchemy import select
from sqlalchemy import insert
from sqlalchemy import update
from sqlalchemy import func
from sqlalchemy import bindparam
from sqlalchemy import and_

image_table = env.meta.tables["tb_news_images"]
cols = image_table.c

def get_unsaved_images(offset, limit):
    global image_table, cols
    s = select([image_table], offset = offset, limit = limit).\
        where(cols.saved_url == "")

    return env.engine.execute(s)

def get_all():
    global image_table, cols
    s = select([image_table])

    return env.engine.execute(s)

def update_fields(sign, f):
    global image_table, cols

    now = int(time.time())

    fields = f.copy()
    fields["update_time"] = now

    u = update(image_table).where(cols.url_sign == sign).values(**fields)

    env.engine.execute(u)
