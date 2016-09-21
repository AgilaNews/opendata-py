#!/usr/bin/env python

import env
import logging
import imagedao
import grequests
import json

from constants import FETCH_TIMEOUT
import imagesaver

saver = imagesaver.ImageSaver("ucloud", {
    "public_key": "UUztwD49TCzQ39diGb2T4a/0uYMwE6/PWII6fWwtuCiDQRQBfslLNg==",
    "private_key": "ef1716513ea5eb553737d08ce056e30ed9510d72",
    "bucket": "agilanews",
    "proxy": ".hk.ufileos.com",
    "download": ".ufile.ucloud.com.cn",
})

offset = 0
limit = 50

while True:
    imgs = [_ for _ in imagedao.get_unsaved_images(offset, limit)]
    if not imgs:
        break
    
    offset += len(imgs)
    saved_images = saver.save([{"url": img.source_url, "name": img.url_sign} for img in imgs])

    for i in range(0, len(saved_images)):
        img = imgs[i]
        saved = saved_images[i]
        if saved:
            logging.info("[sign:%s][url:%s][updated:%s]" %(img.url_sign, img.source_url, json.dumps(saved)))
            imagedao.update_fields(img.url_sign, {"saved_url": json.dumps(saved)})
        else:
#            logging.warn("[sign:%s][url:%s] is deadlink" %(img.url_sign, img.source_url))
            imagedao.update_fields(img.url_sign, {"is_deadlink": 1})
