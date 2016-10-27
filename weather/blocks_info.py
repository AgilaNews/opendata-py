#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
# @Date    : 2016-10-27 12:55:04
# @Author  : CCcc (chencong2232@163.com)
# @Link    : ${link}
# @Describe:
"""

import os
import traceback
import urllib
import hashlib
import requests
import Geohash
import itertools
from sqlalchemy import engine, MetaData, create_engine
from sqlalchemy import select
from sqlalchemy import insert
from sqlalchemy import update
from sqlalchemy import and_
import math
import collections

engine = create_engine("mysql://%s:%s@%s:%s/%s?charset=%s&use_unicode=0" \
                       % ("root", "", "localhost", 3306, "banews", "utf8"), \
                       pool_reset_on_return=None, pool_size=10, pool_recycle=600, \
                       encoding="utf8", \
                       execution_options={"autocommit": True})

meta = MetaData()
meta.reflect(bind=engine)

base32 = '0123456789bcdefghjkmnpqrstuvwxyz'


def nearbyCity(cities, lat, lng, standard = 0.1):
    """
    :param cities: 附近城市列表
    :param lat: Geohash 的纬度
    :param lng: Geohash 的经度
    :param standard: 判读geohash是否在city附近标准
    :return: Boolean
    """
    distance =[]
    for city in cities:
        cityLat = city['latitude']
        cityLng = city['latitude']
        #经纬度差平方和开根作为距离判据
        distance.append(math.sqrt((cityLng-lng) * (cityLng-lng) + (cityLat-lat) * (cityLat-lat)))
    mindistance = min(distance)
    if mindistance < standard:
        return cities[distance.index(mindistance)]['id']
    return 0


def getCityTBID(cityName, provinceName, lat, lng):
    """
    如果根据cityname，provinceName查到了数据，返回表ID
    否则，查询province下所有城市中，如果存在与当前lat, lng的误差小于一个范围的城市，返回误差最小的表ID
    否则，返回0
    """
    city_table = meta.tables['tb_city']
    city_cols = city_table.c
    select_city = select([city_table]).where(city_cols.city_name == cityName)
    city = engine.execute(select_city).first()
    if city:
        return city['id']
    select_province = select([city_table]).where(city_cols.city_name == provinceName)

    cities = engine.execute(select_province).fetchall()
    if cities:
        return nearbyCity(cities,lat,lng)
    return 0


def saveBlockInfo(geohash, city_tb_id):
    """
    存储信息到block_info表中
    """
    table = meta.tables["block_info"]
    if city_tb_id == 0:
        status_info = 0
    else:
        status_info = 1
    value={
        'geohash' : geohash,
        'status_info' : status_info,
        'city_id' : city_tb_id
    }
    insert_blocks = insert(table).values(**value)
    engine.execute(insert_blocks)


def nearbyGeohash(geohash):
    """
    :某个geohash周边的geohash的解码出经纬度和该geohash经纬度差值为一定的值
    :param geohash:
    :return: nearby
    ：
    """
    nearby=[]
    (lat, lng, lat_err, lng_err) = Geohash.decode_exactly(geohash)
    nearby.append(Geohash.encode(lat - 2 * lat_err, lng - 2*lat_err,5))
    nearby.append(Geohash.encode(lat - 2 * lat_err, lng,5))
    nearby.append(Geohash.encode(lat - 2 * lat_err, lng + 2 * lat_err,5))
    nearby.append(Geohash.encode(lat, lng - 2 * lat_err,5))
    nearby.append(Geohash.encode(lat, lng + 2 * lat_err,5))
    nearby.append(Geohash.encode(lat + 2 * lat_err, lng - 2 * lat_err,5))
    nearby.append(Geohash.encode(lat + 2 * lat_err, lng,5))
    nearby.append(Geohash.encode(lat + 2 * lat_err, lng + 2 * lat_err,5))
    return nearby


def maxTimes(list):
    """
    :求众数
    :param list:输入yigelist
    :return:
    """
    valueCounter = collections.Counter(list)
    maxNumber = valueCounter.most_common(1)
    return maxNumber[0][0]


def notMapping():
    """
    处理block_info表中的数据
    """
    block_table = meta.tables["block_info"]
    block_cols=block_table.c
    select_blocks = select([block_table]).where(block_cols.status_info == 0)
    blocks = engine.execute(select_blocks).fetchall()
    flag = 0                                    #判断是否进入死循环
    if blocks is not None:
        for block in blocks:
            nearby = nearbyGeohash(block['geohash'])
            block_list = [] #存储周围Geohash信息
            for nearby_geohash in nearby:
                select_info = select([block_table]).where(block_cols.geohash == nearby_geohash)
                block_info = engine.execute(select_info).first()
                if block_info is not None and block_info['status_info'] != 0:         #当该geohash存在block_info表中且上一轮中status已经为1时记录到block——list中
                    block_list.append(block_info['city_id'])
            if block_list:                        #block_list有信息，取其众数为该geohash的city_id
                flag = 1
                block_city_id = maxTimes(block_list)
                value = {
                    'city_id': block_city_id
                }
                update_block = update(block_table).where(block_cols.geohash == block['geohash']).values(**value)
                engine.execute(update_block)

        if flag == 0:         #循环一轮后 没有改变flag的值，进入死循环，跳出
            return True

        #循环一轮后将 由0 变为正常的city_id 的block的status_info设为1
        status_value = {
            'status_info': 1
        }
        update_blocks = update(block_table).where(and_(block_cols.city_id != 0, block_cols.status_info == 0)).values(
            **status_value)
        engine.execute(update_blocks)
        return False
    else:
        return True


def main():
    table = meta.tables["tb_baidu_block"]
    select_blocks = select([table])
    blocks = engine.execute(select_blocks).fetchall()
    for block in blocks:
        cityName = block['cityName']
        provinceName = block['provinceName']
        (lat, lng, lat_err, lng_err) = Geohash.decode_exactly(block['geohash'])
        city_tb_id = getCityTBID(cityName, provinceName,lat,lng)
        saveBlockInfo(block['geohash'], city_tb_id)
    while True:
        if notMapping() :
            break

if __name__ == '__main__':
    main()