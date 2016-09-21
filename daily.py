#-*- coding: utf-8 -*-
'''
this script will crawler match of three days
'''
import standings
import teams
import datetime

if __name__ == "__main__":
    n = datetime.datetime.now()
    for i in range(0, 3):
        standings.crawl(n + datetime.timedelta(days = i))
