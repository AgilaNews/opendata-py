#-*- coding: utf-8 -*-
'''
this script will crawler match of three days
'''
import env
import standings
import teams
import datetime
import logging

if __name__ == "__main__":
    logging.info("starts new crawler")
    n = datetime.datetime.now()
    for i in range(0, 3):
        standings.crawl(n + datetime.timedelta(days = i))
