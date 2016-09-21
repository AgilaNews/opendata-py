#!/usr/bin/env python
import json
import imagesaver

saver = imagesaver.ImageSaver("ucloud", {
    "public_key": "UUztwD49TCzQ39diGb2T4a/0uYMwE6/PWII6fWwtuCiDQRQBfslLNg==",
    "private_key": "ef1716513ea5eb553737d08ce056e30ed9510d72",
    "bucket": "agilanewssandbox",
    "proxy": ".hk.ufileos.com",
    "download": ".ufile.ucloud.com.cn",
}, timeout=100)

#print saver.save([{"url": "http://ell.h-cdn.co/assets/16/22/768x1152/gallery-1464821210-house-of-harlow-metallic.jpg", "name": "hello"}])
print saver.save_video("http://img-9gag-fun.9cache.com/photo/a1XZ6ov_460sv.mp4", "video", "girl.mp4", need_cover=True)
