#! /usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import traceback
import redis
import threading
import tornado.escape
from kola import Singleton

global Debug
Debug = True


# 命令管理器
class KolaCommand(Singleton):
    db = redis.Redis(host='127.0.0.1', port=6379, db=0)
    mutex = threading.Lock()

    def GetCommand(self):
        ret = {}
        KolaCommand.mutex.acquire()
        cmd = KolaCommand.db.lpop('command')
        if cmd:
            ret = tornado.escape.json_decode(cmd)

        KolaCommand.mutex.release()

        return ret

# 命令管理器
class EngineCommands(KolaCommand):
    def __init__(self):
        self.urlmap = {}
        self.pipe = None

    def AddCommand(self, cmd):
        if 'source' in cmd or 'text' in cmd:
            if 'source' in cmd:
                cmd['source'] = cmd['source']
            if self.pipe == None:
                self.pipe = self.db.pipeline()
            self.pipe.rpush('command', tornado.escape.json_encode(cmd))
        return self

    def Execute(self):
        if self.pipe:
            self.pipe.execute()
            self.pipe = None

# 网页解析器
class KolaParser:
    def __init__(self):
        self.command = EngineCommands()
        self.name = self.__class__.__module__ + '.' + self.__class__.__name__

        self.cmd = {}
        self.cmd['engine'] = self.name
        self.cmd['cache']  = True

    def AddCommand(self):
        if self.cmd:
            self.command.AddCommand(self.cmd)
            self.cmd = None

    def Execute(self):
        self.AddCommand()
        self.command.Execute()

# 解析引擎
class EngineBase:
    def __init__(self):
        self.engine_name = 'EngineBase'

        self.parserList = []

    # 解析菜单网页解析
    def ParserHtml(self, js):
        try:
            for engine in self.parserList:
                if engine.name == js['engine']:
                    return engine.CmdParser(js)

        except:
            t, v, tb = sys.exc_info()
            print("VideoEngine.ParserHtml:  %s,%s, %s" % (t, v, traceback.format_tb(tb)))

        return False, None

