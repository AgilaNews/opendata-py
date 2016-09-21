#!-*- coding:utf-8 -*-
from img.s3provider._ucloud import Provider

def create(name, conf):
    return Provider(conf)
