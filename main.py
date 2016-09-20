#-*- coding:utf-8 -*-
import standings
import teams
import datetime

if __name__ == "__main__":
    standings.crawl(datetime.datetime.now(), "2016-17")
    #teams.crawl("1610612739", "2015-16")
    
