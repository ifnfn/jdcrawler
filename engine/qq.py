#! /usr/bin/python3
# -*- coding: utf-8 -*-

import hashlib
import re
import time
from urllib.parse import quote

from bs4 import BeautifulSoup as bs, Tag
import tornado.escape

import kola

from .engines import VideoEngine, KolaParser


global Debug
Debug = True

# 节目列表
class ParserAlbumList(KolaParser):
    def __init__(self, url=None, cid=None):
        super().__init__()
        if url and cid:
            self.cmd['source']  = url
            # self.cmd['regular'] = ['(<h6.*?>[\s\S]*?</h6>|<a href=.*class="next".*</a>)']
            self.cmd['cache']   = False

    def CmdParser(self, js):
        soup = bs(js['data'])  # , from_encoding = 'GBK')

        playlist = soup.findAll('div', {'class' : 'gl-i-wrap j-sku-item'})
        for p in playlist:
            print(p)
            print("\n\n\n\n")


        # ParserAlbumList(nexturl, js['cid']).Execute()
        return True

# QQ 搜索引擎
class QQEngine(VideoEngine):
    def __init__(self):
        super().__init__()

        self.engine_name = 'QQEngine'

        self.parserList = [
            ParserAlbumList(),
        ]

    def Start(self):
        url = 'https://list.jd.com/list.html?cat=12218%2C12221&go=0'
        ParserAlbumList(url, 1).Execute()
