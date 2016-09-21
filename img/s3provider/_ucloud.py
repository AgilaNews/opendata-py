#-*- coding: utf-8 -*-
import httplib
import requests
import ucloud
import logging
import urllib
import ucloud.ufile.config as cf

from io import BytesIO
from ucloud.ufile import putufile
from ucloud.compact import b

class Provider:
    def __init__(self, conf):
        try:
            self._public_key = str(conf["public_key"])
            self._private_key = str(conf["private_key"])
            self._bucket = str(conf["bucket"])
            self._url_proxy = str(conf["url_proxy"])
        except KeyError:
            assert(False)

        if "proxy" in conf:
            cf.set_default(uploadsuffix = str(conf["proxy"]))
            self._proxy = conf["proxy"]
        if "download" in conf:
            cf.set_default(downloadsuffix = str(conf["download"]))
            self._download = conf["download"]
        if "connection_timeout" in conf:
            cf.set_default(connection_timeout = int(conf["connection_timeout"]))

        self.handler = putufile.PutUFile(self._public_key,
                                         self._private_key)

    def save_object_stream(self, directory, name, data, mime_type="image/jpeg"):
        if isinstance(data, str):
            data = BytesIO(data)
        ret, resp = self.handler.putstream(self._bucket, directory + '/' + name, data, mime_type=mime_type)
        if resp.status_code != 200:
            raise Exception(resp.error)
        return 'http://{0}{1}/{2}'.format(self._bucket, self._url_proxy, directory + "/" + urllib.quote(name, safe=""))
