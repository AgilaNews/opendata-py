#-*- coding:utf-8 -*-
import datetime
import logging
import re

def future(soup,value):
    week = soup.find('div', {'class': 'week-forecast'})

    if week is None:
        raise Exception('week-forecast div not found')
    table = week.findAll('table')

    n = datetime.datetime.now()
    hour=n.hour
    if hour>5:
        tablelist=range(0,3)
    else:
        tablelist=range(1,4)

    value['days']=['0','1','2']
    k=0
    for i in tablelist:
        tr = table[i].findAll('tr')
        lengthtr = len(tr)
        tem = range(0, lengthtr - 1)
        desp = range(0, lengthtr - 1)
        for j in range(1, lengthtr):
            td = tr[j].findAll('td')
            temperature = re.findall('[\.0-9]+', str(td[2]))
            tem[j - 1] = float(temperature[0])
            desp[j - 1] = td[1].span.attrs['title']
        mintem = min(tem)
        maxtem = max(tem)
        dateArray = n + datetime.timedelta(days=k)
        weekday = dateArray.strftime("%A")
        monthday = "%s/%s" % (dateArray.month, dateArray.day)

        value['days'][k] = {
                            "weekday": weekday,
                            "date": monthday,
                            "temperature": [maxtem, mintem],
                            "weather": desp[0]
                        }
        k +=1
    return value