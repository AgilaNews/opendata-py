#!-*- coding: utf-8 -*-
import s3provider
import grequests
import requests
import json
import logging
import urllib
import tempfile
from PIL import Image
from io import BytesIO
from videoutil import *

HDPI = (480, 854)
XHDPI = (720, 1280)
XXHDPI = (1080, 1920)
THRESHOLD = (240, 170)

MAX_WIDTH_RATE = 0.97
MIN_HEIGHT_RATE = 0.2
THUMB_WIDTH_RATE = 0.31
THUMB_HEIGHT_RATE = 0.14
QUALITY = 30
THUMB_QUALITY = 50

VIDEO_SIZE_LOW_LIMIT = 10 * 1024
VIDEO_SIZE_LOW_QULITY_LIMIT = 50 * 1024
VIDEO_DURATION_UPPER_LIMIT = 20
VIDEO_WIDTH_LOW_LIMIT = 120
VIDEO_RATIO_LOW_LIMIT = 222.0/666.0
VIDEO_RATIO_HIGH_LIMIT = 994.0/666.0

class ImageSaver:
    def __init__(self, provider_name, config = {}, timeout = 3):
        self._provider = s3provider.create(provider_name, config)
        self._timeout = timeout
        logging.getLogger("UCLOUD").setLevel(logging.WARNING)

    def save(self, imgs, adjust_size=True, drop_ratio=()):
        '''
        input format
        [
            {
                "url": "http://example.com/img.jpg",
                "name": "abcdxef=",
            }
        ]
        '''
        img = imgs[0]
        url = img['url']
        base_name = img['name']
        ret = []
        if url.startswith('file://'):
            #local storage - iframe screenshots
            url = url.replace('file://','')
            try:
                image_handler = Image.open(url)
            except IOError:
                logging.warn("[RSP_BODY_ERR][url:%s][http_code:%s]" % (url, 'local storage iframe screenshot'))
                ret.append(None)
                return ret
            if image_handler.size[0] < THRESHOLD[0] or image_handler.size[1] < THRESHOLD[1]:
                #drop some low quality images
                logging.getLogger(__file__).warn("[URL:%s][DROP_IMG][LOW_QUAL:%s]" % (url, str(image_handler.size)))
                ret.append(None)
            try:
                ret.append(self.save_iframe(image_handler, "image", base_name + ".png", image_handler.size))
            except:
                logging.exception("[SaveErr][%s]" % url)
                ret.append(None)
            return ret


        rs = [grequests.get(img["url"], timeout = self._timeout) for img in imgs]
        resps = grequests.map(rs)

        for i in range(0, len(resps)):
            resp = resps[i]
            img = imgs[i]

            base_name = img["name"]
            if not resp:
                logging.warn("[REQ_ERR][url:%s]" % img["url"])
                ret.append(None)
                continue

            try:
                image_handler = Image.open(BytesIO(resp.content))
            except IOError:
                logging.warn("[RSP_BODY_ERR][url:%s][http_code:%s]" % (img["url"], resp.status_code))
                ret.append(None)
                continue

            if image_handler.size[0] < THRESHOLD[0] or image_handler.size[1] < THRESHOLD[1]:
                #drop some low quality images
                logging.getLogger(__file__).warn("[URL:%s][DROP_IMG][LOW_QUAL:%s]" % (img["url"], str(image_handler.size)))
                ret.append(None)
                continue

            if drop_ratio:
                ratio = image_handler.size[0]/float(image_handler.size[1])
                if ratio < drop_ratio[0]  or ratio > drop_ratio[1]:
                    logging.getLogger(__file__).warn("[URL:%s][DROP_IMG][RATIO:%s]" % (img["url"], str(image_handler.size)))
                    ret.append(None)
                    continue

            if adjust_size:
                try:
                    ret.append({
                        "hdpi": self.save_adjust(image_handler, "small", base_name + ".jpg", HDPI),
                        "xhdpi": self.save_adjust(image_handler, "medium", base_name + ".jpg", XHDPI),
                        "xxhdpi": self.save_adjust(image_handler, "large", base_name + ".jpg",  XXHDPI),
                        "thumb_hdpi": self.save_adjust_thumb(image_handler, "tsmall", base_name + ".jpg", HDPI),
                        "thumb_xhdpi": self.save_adjust_thumb(image_handler, "tmedium", base_name + ".jpg", XHDPI),
                        "thumb_xxhdpi": self.save_adjust_thumb(image_handler, "tlarge", base_name + ".jpg", XXHDPI),
                    })
                except:
                    logging.exception("[SaveErr][%s]" % img["url"])
                    ret.append(None)
            else:
                try:
                    ret.append(self.save_origin(resp.content, "image", base_name + ".jpg", image_handler.size))
                except:
                    logging.exception("[SaveErr][%s]" % img["url"])
                    ret.append(None)

        return ret

    def video_filter(self, fsize, metadata):
        if fsize < VIDEO_SIZE_LOW_LIMIT:
            return 0
        meta = metadata["streams"][0]
        duration = float(meta.get('duration', u'0'))
        if duration > VIDEO_DURATION_UPPER_LIMIT:
            return 0
        width = int(meta.get('width', 1.0))
        height = int(meta.get('height', 0))
        ratio = float(height) / float(width)
        if ratio < VIDEO_RATIO_LOW_LIMIT or ratio > VIDEO_RATIO_HIGH_LIMIT:
            return 0
        if width < VIDEO_WIDTH_LOW_LIMIT and fsize < VIDEO_SIZE_LOW_QULITY_LIMIT:
            return 0
        return 1

    def save_video(self, url, directory, name, need_cover=False):
        try:
            video_info = {}
            mp4file, fsize = generate_mp4_file(url, datapath='/data/tmp/')
            if not mp4file:
                return None
            metadata = get_video_meta(mp4file.name)
            streamLst = metadata.get('streams', [])
            if len(streamLst) >= 1:
                streamLst[0]["size"] = fsize
            video_info["meta"] = metadata
            video_info["cover"] = None
            if need_cover:
                coverfile = get_cover_photo(mp4file.name, metadata, datapath='/data/tmp/')
                content = coverfile.read()
                image_handler = Image.open(BytesIO(content))
                saved_url = self.save_stream(content, 'image', name + "_cover.jpg", "image/jpeg")
                video_info["cover"] = {}
                video_info["cover"]["src"] = saved_url
                video_info["cover"]["width"] = image_handler.size[0]
                video_info["cover"]["height"] = image_handler.size[1]
                coverfile.close()
            videocontent = mp4file.read()
            video_url = self.save_stream(videocontent, directory, name + ".mp4",  "video/mp4")
            video_info["video_url"] = video_url
            video_info["is_valid"] = self.video_filter(fsize, metadata)
            if not video_info["is_valid"]:
                meta = metadata["streams"][0]
                duration = meta.get('duration', u'0')
                width = meta.get('width', 0)
                height = meta.get('height', 0)
                logging.getLogger(__file__).warn("[URL:%s][DROP_VIDEO][FSIZE:%s][DURATION:%s][WIDTH:%s][HEIGHT:%s]" % \
                        (url, fsize, duration, width, height))
            mp4file.close()
        except:
            traceback.print_exc()
            return None
        return video_info

    def save_stream(self, stream, directory, name, mime_type):
        saved_url = self._provider.save_object_stream(directory, name, stream, mime_type)
        return saved_url

    def save_origin(self, image_stream, directory, name, image_size):
        saved_url = self._provider.save_object_stream(directory, name, image_stream)
        return {"src": saved_url, "height": image_size[1], "width": image_size[0]}

    def save_iframe(self, image, directory, name, image_size):
        out = BytesIO()
        image.save(out, optimize = True, format = "png")
        image_stream = out.getvalue()
        saved_url = self._provider.save_object_stream(directory, name, image_stream)
        logging.getLogger(__file__).info("[IFRAME][name:%s][url:%s]" % (name,saved_url))
        return {"src": saved_url, "height": image.size[1], \
                "width": image.size[0], "isIframe":True}

    def save_adjust(self, image, directory, name, resolution):
        new_image_stream, size = self._adjust(image, resolution)

        saved_url = self._provider.save_object_stream(directory, name, new_image_stream)
        return {"src": saved_url, "height": size[1], "width": size[0]}

    def save_adjust_thumb(self, image, directory, name, resolution):
        new_image_stream, size = self._thumbnail(image, resolution)

        saved_url = self._provider.save_object_stream(directory, name, new_image_stream)
        return {"src": saved_url, "height": size[1], "width": size[0]}

    def _thumbnail(self, image, resolution):
        target_width = int(resolution[0] * THUMB_WIDTH_RATE)
        target_height = int(resolution[1] * THUMB_HEIGHT_RATE)

        adjust_height = int((target_width * image.size[1]) / image.size[0])
        adjust_width = int((target_height * image.size[0]) / image.size[1])

        if adjust_width <=  target_width:
            # image too high
            image = image.resize((target_width, adjust_height), Image.ANTIALIAS)
            crop = float(adjust_height - target_height)
            image = image.crop((0, int(crop / 2), target_width, adjust_height - int(crop / 2)))
        else:
            # image too fat
            image = image.resize((adjust_width, target_height), Image.ANTIALIAS)
            crop = float(adjust_width - target_width)
            image = image.crop((int(crop/2), 0, adjust_width - int(crop/2), target_height))

        out = BytesIO()
        image.save(out, quality = THUMB_QUALITY, optimize = True, format = "jpeg")
        return out.getvalue(), image.size

    def _adjust(self, image, resolution):
        '''
        adjust to size (width, height)
        '''
        max_width = int(resolution[0] * MAX_WIDTH_RATE)
        min_height = int(resolution[1] * MIN_HEIGHT_RATE)

        if image.size[0] > max_width:
            adjust_height = int((max_width * image.size[1]) / image.size[0])
            if adjust_height >= min_height:
                # if larger than min height
                image = image.resize((max_width, adjust_height), Image.ANTIALIAS)
            else:
                adjust_width = int((min_height * image.size[0]) / image.size[1])
                image = image.resize((adjust_width, min_height), Image.ANTIALIAS)
                assert(adjust_width >= max_width)
                crop = float(adjust_width - max_width)
                image = image.crop((int(crop/2), 0, max_width - int(crop/2), min_height))

        out = BytesIO()
        image.save(out, quality = QUALITY, optimize = True, format = "jpeg")
        return out.getvalue(), image.size
