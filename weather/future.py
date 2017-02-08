#-*- coding:utf-8 -*-
import datetime
import re

def future(soup,value):
    '''
    ：获取某城市的未来3天的天气状况
    :param soup: 页面文本
    :param value:当前天气情况
    :return: 当前天气状况 + 未来3天天气情况
    '''
    # 采集到的天气图片对应的天气描述
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

    #当前时间是否为凌晨
    n = datetime.datetime.now()
    hour = n.hour
    if hour > 5:
        #非凌晨
        tablelist = range(0, 3)
    else:
        #凌晨
        tablelist = range(1, 4)
    value['days'] = ['0', '1', '2']
    #第k天
    k = 0
    weeks = soup.findAll('div', {'class': 'panel forecast-row'})
    for i in tablelist:
        divs = weeks[i].findAll('div', {'class': 'forecast-col'})
        lengthtr = len(divs)
        tem = range(0, lengthtr - 1)
        desp = range(0, lengthtr - 1)
        for j in range(1, lengthtr):
            lis = divs[j].findAll('li')
            temperature = re.findall('[\.0-9]+', str(lis[9]))
            tem[j - 1] = float(temperature[0])
            desp[j - 1] = re.findall('[a-z\._]+png', str(lis[1]))
        mintem = min(tem)
        maxtem = max(tem)
        dateArray = n + datetime.timedelta(days=k)
        weekday = dateArray.strftime("%A")
        monthday = "%s/%s" % (dateArray.month, dateArray.day)
        value['days'][k] = {
            "weekday": weekday,
            "date": monthday,
            "temperature": [maxtem, mintem],
            "weather":desps[desp[0][0]]
        }
        k += 1
    return value