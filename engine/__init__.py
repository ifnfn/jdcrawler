#! /usr/bin/python3
# -*- coding: utf-8 -*-

import redis
import tornado.ioloop
import tornado.options
import tornado.web
import sys
import json
import re
import traceback


from kola import ThreadPool

from .engines import EngineCommands, VideoEngine, KolaParser
from .jd import JDEngine
from kola import GetUrl, GetCacheUrl, PostUrl


POOLSIZE = 10
MAX_TRY = 3

class KolaEngine:
    def __init__(self):
        self.thread_pool = ThreadPool(POOLSIZE)
        self.command = EngineCommands()
        self.engines = []
        self.UpdateAlbumFlag = False

        self.AddEngine(JDEngine)

    def AddEngine(self, egClass):
        self.engines.append(egClass())

    def ParserJson(self, js):
        if (js == None) or ('data' not in js):
            print("Error:", js['source'])
            return False

        for eg in self.engines:
            if eg.ParserHtml(js):
                break

        return True

    def Start(self):
        for eng in self.engines:
            eng.Start()

    def GetUrl(self, url, cached=False):
        if cached:
            return GetCacheUrl(url)
        else:
            return GetUrl(url)

    def RegularMatch(self, regular, text):
        x = ''
        for r in regular:
            res = re.finditer(r, text)
            if (res):
                for i in res:
                    if type(i.group(1)) == bytes:
                        x += i.group(1).decode("GB18030") + '\n'
                    else:
                        x += i.group(1) + '\n'
                text = x
        if x:
            x = x[0:len(x)-1]
        return x


    def ParserHtml(self, data):
        js = tornado.escape.json_decode(data)

        return self.ParserJson(js)


    # {'source'  : 'http://v.qq.com/movielist/10001/0/10004-100001/0/0/100/0/0.html', 
    #   'regular': ['(<h6.*?>[\\s\\S]*?</h6>|<a href=.*class="next".*</a>)'], 
    #   'engine' : 'engine.qq.ParserAlbumList', 
    #   'cache'  : False
    # }
    def ProcessCommand(self, cmd, times = 0):
        ret = False
        cached = True
        cache_file = ''
        found = False
        response = ''

        if times > MAX_TRY or type(cmd) != dict:
            return False
        try:

            # 获取数据 response
            if 'text' in cmd:
                response = cmd['text']
            else:
                if 'source' in cmd:
                    if 'cache' in cmd:
                        cached = cmd['cache']
                    response, cache_file, found = self.GetUrl(cmd['source'], cached)
    

            # 对数据 response 转码
            coding = 'utf8'
            try:
                if type(response) == bytes:
                    response = response.decode(coding)
            except:
                coding = 'GB18030'
                if type(response) == bytes:
                    response = response.decode(coding)

            # 数据正则匹配
            if 'regular' in cmd:
                response = self.RegularMatch(cmd['regular'], response).encode(coding)
        
            if response:
                if type(response) == bytes:
                    response = response.decode(coding)
                cmd['data'] = response
            else:
                print("[WARNING] Data is empty", cmd['source'])

            return self.ParserJson(cmd)

        except:
            t, v, tb = sys.exc_info()
            print("ProcessCommand playurl: %s, %s, %s" % (t, v, traceback.format_tb(tb)))
            return self.ProcessCommand(cmd, times + 1)

        if 'source' in cmd:
            print((ret == True and "OK:" or "ERROR:"), (found and "[IN CACHE]" or ''), cache_file, cmd['source'])

        return "{}"