#! /usr/bin/python3
# -*- coding: utf-8 -*-

import hashlib
import re
import time
from urllib.parse import quote, urljoin

from bs4 import BeautifulSoup as bs, Tag
import tornado.escape

import kola

from .engines import VideoEngine, KolaParser


global Debug
Debug = True


# <div class="spec-items">

# 获取商品价格
#https://p.3.cn/prices/mgets?callback=jQuery2818475&type=1&area=1_72_4137&skuIds=J_1005131698%2CJ_1005388333


class ParserGoodsDetailed(KolaParser):
    def __init__(self, url=None, data=None):
        super().__init__()
        if url:
            self.cmd['source']   = url
            # self.cmd['regular'] = ['(<h6.*?>[\s\S]*?</h6>|<a href=.*class="next".*</a>)']
            self.cmd['cache']    = True
            if data:
                self.cmd['data'] = data

    def CmdParser(self, js):
        soup = bs(js['data'], "html.parser")  # , from_encoding = 'GBK')

        # 大图浏览
        playlist = soup.findAll('div', {'class' : 'spec-items'})
        print(playlist)

        # 选择各类
        playlist = soup.findAll('div', {'id' : 'choose-color'})
        print(playlist)

        # 商品参数
        playlist = soup.findAll('div', {'id' : 'p-parameter'})
        print(playlist)

        # 商品详细介绍（图片列表）
        playlist = soup.findAll('div', {'id' : 'J-detail-content'})
        print(playlist)

# 解析商品列表
class ParserGoodsList(KolaParser):
    def __init__(self, url=None):
        super().__init__()
        if url:
            self.cmd['source'] = url
            self.cmd['cache']  = True
            # self.cmd['regular'] = ['(<h6.*?>[\s\S]*?</h6>|<a href=.*class="next".*</a>)']

    def CmdParser(self, js):
        soup = bs(js['data'], "html.parser")  # , from_encoding = 'GBK')

        data = {}
        playlist = soup.findAll('div', {'class' : 'gl-i-wrap j-sku-item'})
        for p in playlist:
            # <div class="gl-i-wrap j-sku-item" data-sku="2728940" jdzy_shop_id="1000013923" venderid="1000013923">
            #     <div class="p-img">
            #         <a href="//item.jd.com/2728940.html" target="_blank">
            #             <img data-img="1" height="220" src="//img10.360buyimg.com/n7/jfs/t2821/239/381741115/358017/c17e621e/57104694Nd47d0613.jpg" width="220">
            #             </img>
            #         </a>
            #     </div>
            #     <div class="p-price">
            #         <strong class="J_price"><em></em><i></i></strong>
            #         <div class="p-icons J-pro-icons">
            #         </div>
            #     </div>
            #     <div class="p-name">
            #         <a href="//item.jd.com/2728940.html" target="_blank" title="">
            #             <em>佳沛zespri 新西兰进口金奇异果猕猴桃 16粒装 36#果 自营水果</em>
            #             <i class="promo-words"></i>
            #         </a>
            #     </div>
            #     <div class="p-shop hide" data-done="1" data-reputation="0" data-score="4" data-shopid=""></div>
            #     <div class="p-commit"><strong>已有<a href="//item.jd.com/2728940.html#comment" target="_blank">5141</a>人评价</strong></div>
            #     <div class="p-operate">
            #         <a class="p-o-btn contrast J_contrast" data-sku="2728940" href="javascript:;">
            #             <i></i>对比
            #         </a>
            #         <a class="p-o-btn focus J_focus" data-sku="2728940" href="javascript:;">
            #             <i></i>关注
            #         </a>
            #         <a class="p-o-btn addcart" href="//gate.jd.com/InitCart.aspx?pid=2728940&amp;pcount=1&amp;ptype=1" target="_blank">
            #             <i></i>加入购物车
            #         </a>
            #     </div>
            #     <div class="p-stock" data-isdeliveryable="5" style="display: none;"></div>
            # </div>

            if 'data-sku' in p.attrs:
                data['data-sku'] = p.attrs['data-sku']
            if 'venderid' in p.attrs:
                data['venderid'] = p.attrs['venderid']

            # 取图片信息
            data_img = p.findAll('img', {'data-img': '1'})
            if data_img:
                if 'src' in data_img[0]:
                    data['data-img'] = urljoin('https://list.jd.com', data_img[0]['data-lazy-img'])
                elif 'data-lazy-img' in data_img[0]:
                    data['data-img'] = urljoin('https://list.jd.com', data_img[0]['data-lazy-img'])
                pass

            # 取商品名称与详细介绍
            p_name = p.findAll('div', {'class': 'p-name'})
            if p_name:
                data['p-name'] = p_name[0].text.strip()

            if type(p_name[0]) == Tag:
                for t in p_name[0].contents:
                    if type(t) == Tag:
                        url = urljoin('https://list.jd.com', t['href'])
                        data['desc'] = url
                        ParserGoodsDetailed(url, data).Execute()

        # 下一页
        # [<a class="pn-next" href="/list.html?cat=12218,12221&amp;page=2&amp;go=0&amp;JL=6_0_0">下一页<i>&gt;</i></a>]
        # next_text = soup.findAll('a', {'class' : 'pn-next'})
        # for a in next_text:
        #     href = "https://list.jd.com" + a.attrs['href']
        #     ParserGoodsList(href).Execute()

        return True

# JD 搜索引擎
class JDEngine(VideoEngine):
    def __init__(self):
        super().__init__()

        self.engine_name = 'QQEngine'

        self.parserList = [
            ParserGoodsList(),
            ParserGoodsDetailed(),
        ]

    def Start(self):
        url = 'https://list.jd.com/list.html?cat=12218%2C12221&go=0'
        ParserGoodsList(url).Execute()
