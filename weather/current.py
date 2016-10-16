#-*- coding:utf-8 -*-
import re
import time
import logging

def current(soup,city_id):
    week = soup.find('div', {'class': 'current-detail-condition '})
    flag = 1
    list=[]
    if week is not None:
        flag = 0
        current_tem = soup.find('div', {'class': 'temp-highlight'})
        if current_tem is None:
            current_tem = soup.find('div', {'class': 'temp-highlight-alt'})
        temperature = re.findall('[\.0-9]+', current_tem.string)
        if len(temperature) == 0:
            temperature=['0']
            flag = 1
            list.append(1)

        current_desp = soup.find('div', {'class': 'condition-highlight'})
        if current_desp is not None:
            desp = current_desp.span.attrs['title']
            if desp == 'Could not be determined':
                flag = 1
                list.append(2)
        else:
            flag = 1
            desp = 'Could not be determined'
            list.append(2)

        current_left = soup.find('div', {'class': 'current-detail-table'})
        td = current_left.findAll('td')
        speed = re.findall('[0-9]+ ', str(td[0]))
        if len(speed) == 0:
            speed=['0']
            flag = 1
            list.append(3)
        direct = re.findall('[SWEN]+', str(td[0]))

        if len(direct) == 0:
            flag=1
            list.append(4)
        direction = ''.join(direct)

        gusts = re.findall('[0-9]+ ', str(td[1]))
        if len(gusts) == 0:
            gusts=['0']
            flag=5
            list.append(5)
        humidity=re.findall('[0-9]+',str(td[3].string))
        if len(humidity)==0:
            humidity=[0]
            list.append(6)

        value = {
            "timestamp":int(time.time()),
            "cityid": city_id,
            "now": {
                "temperature": float(temperature[0]),
                "weather": desp,
                "wind": {
                    "speed": float(speed[0]),
                    "direction": direction,
                    "gusts": float(gusts[0])
                },
                "humidity": int(humidity[0])
            }
        }
    if flag == 1:
        week = soup.find('div', {'class': 'week-forecast'})
        if week is None:
            raise Exception('week-forecast div not found')
        table = week.findAll('table')
        tr = table[0].findAll('tr')
        td = tr[1].findAll('td')

        speed = re.findall('[0-9]+ ', str(td[6]))
        if len(speed) == 0:
            speed = ['0 ','0']
        elif len(speed) == 1:
            speed = [speed[0],'0']


        direct = re.findall('from [a-zA-Z\s]+', str(td[6]))
        if len(direct) ==0:
            direction='-'
        else:
            directs= re.findall('[SWEN]+', direct[0])
            direction = ''.join(directs)



        temperature = re.findall('[\.0-9]+', str(td[2]))
        desp = td[1].span.attrs['title']
        humidity = re.findall('[0-9]+', str(td[4].string))
        if len(list) == 0:
            value = {
                "time": int(time.time()),
                "cityid": city_id,
                "now": {
                    "temperature": float(temperature[0]),
                    "weather": desp,
                    "wind": {
                        "speed": float(speed[0]),
                        "direction": direction,
                        "gusts": float(speed[1])
                    },
                    "humidity": int(humidity[0])
                },
            }
        else:
            for i in list:
                if i == 1:
                    value['now']['temperature'] = float(temperature[0])
                elif i == 2:
                    value['now']['weather'] = desp
                elif i == 3:
                    value['now']['wind']['speed'] = float(speed[0])
                elif i == 4:
                    value['now']['wind']['direction'] = direction
                elif i == 5:
                    value['now']['wind']['gusts'] = float(speed[1])
                elif i == 6:
                    value['now']['humidity'] = int(humidity[0])

    return value
