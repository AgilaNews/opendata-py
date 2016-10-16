#-*- coding:utf-8 -*-
from apscheduler.schedulers.blocking import BlockingScheduler
import logging
import env
import weather


def my_job():
    logging.info("starts new crawler")
    weather.new()


weather.new()
sched = BlockingScheduler()
sched.add_job(my_job, 'interval', seconds=600)
sched.start()

