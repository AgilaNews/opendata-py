#!-*- coding:utf-8 -*-
#抓起新天气情况到redis
from sqlalchemy import engine, MetaData, create_engine
from sqlalchemy import select
import json
import re
import logging
import env
import current
import network
import future
import bs4 as BeautifulSoup
import time

table = env.meta.tables["tb_city"]
cols = table.c
s = select([table]).where(cols.status == 1)
result=env.engine.execute(s).fetchall()

def new():
    changenum=0
    for x in result:
        city_id = x[1]
        try:
            res = network.req("get", "http://weather.com.ph/view/" + str(city_id))
            if res.status_code != 200:
                raise Exception(str(res.status_code) + "network error")
            soup = BeautifulSoup.BeautifulSoup(res.text)
            value = current.current(soup,city_id)
            value = future.future(soup,value)
            rediskey = 'weather_' + str(city_id)
            redisvalue = json.dumps(value)
            env.redis.set(rediskey, redisvalue)
            changenum = changenum +1
            time.sleep(3)
        except Exception,e:
            errormessage= 'city_id '+str(city_id)+' weather did not change, INFO: '
            logging.info(errormessage+e.message)
    logging.info(str(changenum)+'cities weather are updated')

