#! /usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import json
import re
import traceback

from .fetchTools import GetUrl, GetCacheUrl, PostUrl, WGet, RegularMatch, RegularMatchUrl
from .engines import EngineCommands
from .jd import JDEngine
from .letv import LetvEngine

MAX_TRY = 3

class KolaEngine:
    def __init__(self):
        self.command = EngineCommands()
        self.engines = []
        self.UpdateAlbumFlag = False

        #self.AddEngine(JDEngine)
        self.AddEngine(LetvEngine)

    def GetCommand(self):
        return self.command.GetCommand()

    def AddEngine(self, egClass):
        self.engines.append(egClass())

    def ParserJson(self, js):
        if js != None and 'data' in js:
            for eg in self.engines:
                status, data = eg.ParserHtml(js)
                if status:
                    return data

        return None

    def Start(self):
        for eng in self.engines:
            eng.Start()

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
            return None
        try:
            # 获取数据 response
            if 'text' in cmd:
                response = cmd['text']
            else:
                if 'source' in cmd:
                    if 'cache' in cmd:
                        cached = cmd['cache']
                    response, cache_file, found = WGet(cmd['source'], cached)

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

        return None
