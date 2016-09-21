import requests
import subprocess32 as subprocess
import shlex
import json
import os.path
import traceback
import tempfile
from urlparse import urlsplit

def generate_mp4_file(url, datapath="/data/tmp/"):
     try:
         urlinfo = urlsplit(url)
         ext = os.path.splitext(urlinfo.path)[1]
         resp = requests.get(url)
         fsize = len(resp.content)
         if resp.status_code != 200:
             return (None, 0)

         videofile = tempfile.NamedTemporaryFile(prefix=datapath, suffix=ext)
         videofile.write(resp.content)
         videofile.seek(0)
         if ext == ".mp4":
             return (videofile, fsize)
         elif ext == ".webm":
             return (None, 0)
         elif ext == ".gif":
             convert_file = convert_gif_to_mp4(videofile.name)
             videofile.close()
             return (convert_file, fsize)
         else:
             return (None, 0)
     except:
        traceback.print_exc()
        return (None, 0)

def convert_gif_to_mp4(input):
    try:
        cmd = 'ffmpeg -i %s -c:v libx264 -pix_fmt yuv420p -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" %s'%(videofile, videofile)
    except:
        return None
    return None

def get_video_meta(video_file):
     try:
         cmd = "ffprobe -v quiet -print_format json -show_streams"
         args = shlex.split(cmd)
         args.append(video_file)
         # run the ffprobe process, decode stdout into utf-8 & convert to JSON
         ffprobeOutput = subprocess.check_output(args, timeout=60).decode('utf-8')
         ffprobeOutput = json.loads(ffprobeOutput)
     except:
         traceback.print_exc()
         return None
     return ffprobeOutput

def get_cover_photo(video_file, meta, datapath="/data/tmp/"):
     try:
         start_time = meta["streams"][0].get("start_time")
         coverfile = tempfile.NamedTemporaryFile(prefix=datapath, suffix=".jpg")
         cmd = "ffmpeg -i %s -ss %s -vframes 1 %s -v quiet -y"%(video_file, start_time, coverfile.name)
         args = shlex.split(cmd)
         subprocess.call(args, timeout=60)
     except:
        traceback.print_exc()
        return None
     coverfile.seek(0)
     return coverfile

