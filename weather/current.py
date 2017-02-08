#-*- coding:utf-8 -*-
import re
import time

def current(soup,city_id):
    '''
    ：获取某城市的当前天气状况
    :param soup: 页面文本
    :param city_id: 所采集的城市的id
    :return: 当前天气状况
    '''
    #采集到的天气图片对应的天气描述
    desps = {
        'cloudy_light.png': 'Scattered Clouds',
        'cloudy_light_night.png': 'Scattered Clouds',
        'cloudy.png': 'Cloudy',
        'cloudy_night.png': 'Cloudy',
        'thunderstorms_heavy.png': 'Thunderstorms',
        'thunderstorms_heavy_night.png': 'Thunderstorms',
        'sunny.png': 'Sunny',
        'night.png': 'Clear Sky',
        'rainshowers.png': 'Rain Shower',
        'rainshowers_night.png': 'Rain Shower',
        'rain.png': 'Rain',
        'rain_night.png': 'Rain',
        'drizzle.png': 'Rain',
        'drizzle_night.png': 'Rain'
    }
    week = soup.find('table', {'class': 'meta'})
    tds = week.findAll('td')
    lists = []
    #温度
    temperature = re.findall('[\.0-9]+', str(tds[1]))
    if len(temperature) == 0:
        temperature = ['0']
        lists.append(1)
    #天气描述
    current_desp = soup.find('div', {'class': 'weather-icon'})
    desp = re.findall('[a-z\._]+png', str(current_desp))
    if len(desp) == 0:
        desp = ['-']
        lists.append(2)
    #风速
    speed = re.findall('[0-9]+', str(tds[0]))
    if len(speed) == 0:
        speed = ['0']
        lists.append(3)
    #风向
    direction = re.findall('[SWEN]+', str(tds[4]))
    if len(direction) == 0:
        lists.append(4)
        direction = '-'
    #gusts
    gusts = re.findall('[0-9]+', str(tds[2]))
    if len(gusts) == 0:
        gusts = ['0']
        lists.append(5)
    #湿度
    humidity = re.findall('[0-9]+', str(tds[3]))
    if len(humidity) == 0:
        humidity = [0]
        lists.append(6)
    value = {
        "timestamp": int(time.time()),
        "cityid": city_id,
        "now": {
            "temperature": float(temperature[0]),
            "weather": desps[desp[0]],
            "wind": {
                "speed": float(speed[0]),
                "direction": direction[0],
                "gusts": float(gusts[0])
            },
            "humidity": int(humidity[0])
        }
    }
    if len(lists) != 0:
        week = soup.findAll('div', {'class': 'panel forecast-row'})
        if week is None:
            raise Exception('panel forecast-row div not found')
        divs = week[0].findAll('div', {'class': 'forecast-col'})
        lis = divs[1].findAll('li')
        temperature = re.findall('[\.0-9]+', str(lis[9]))
        desp = re.findall('[a-z\._]+png', str(lis[1]))
        speed = re.findall('[0-9]+', str(lis[4]))
        direction = re.findall('[SWEN]+', str(lis[5]))
        gusts = re.findall('[0-9]+', str(lis[7]))
        humidity = re.findall('[0-9]+', str(lis[10].string))
        for i in lists:
            if i == 1:
                value['now']['temperature'] = float(temperature[0])
            elif i == 2:
                value['now']['weather'] = desps[desp[0]]
            elif i == 3:
                value['now']['wind']['speed'] = float(speed[0])
            elif i == 4:
                value['now']['wind']['direction'] = direction[0]
            elif i == 5:
                value['now']['wind']['gusts'] = float(gusts[0])
            elif i == 6:
                value['now']['humidity'] = int(humidity[0])
    return value