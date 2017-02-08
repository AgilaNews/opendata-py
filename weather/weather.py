#!-*- coding:utf-8 -*-
#抓起新天气情况到redis
from sqlalchemy import engine, MetaData, create_engine
from sqlalchemy import select
import json
import logging
import env
import current
import network
import future
import bs4 as BeautifulSoup
import time
import traceback

table = env.meta.tables["tb_city"]
cols = table.c
s = select([table]).where(cols.status == 1)
result=env.engine.execute(s).fetchall()

def fixData(weather_value):
    weather_value["days"][0]["weekday"] = "Today"
    if weather_value["now"]["temperature"] > weather_value["days"][0]["temperature"][0]:
        weather_value["days"][0]["temperature"][0] = weather_value["now"]["temperature"]
        
def new():
    changenum=0
    for x in result:
        city_id = x[1]
        url = 'http://weatherph.org/stations/' + str(city_id)
        try:
            res = network.req("get", str(url))
            if res.status_code != 200:
                raise Exception(str(res.status_code) + "network error")
            soup = BeautifulSoup.BeautifulSoup(res.text)
            value = current.current(soup,city_id)
            value = future.future(soup,value)
            rediskey = 'weather_' + str(city_id)
            fixData(value)
            redisvalue = json.dumps(value)
            env.redis.set(rediskey, redisvalue)
            changenum = changenum +1
            time.sleep(3)
        except Exception,e:
            errormessage= 'city_id '+str(city_id)+' weather did not change, INFO: '
            logging.info(errormessage+e.message)
            logging.info(traceback.format_exc())
    logging.info(str(changenum)+'cities weather are updated')
