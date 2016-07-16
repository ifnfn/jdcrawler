#! /usr/bin/python3
# -*- coding: utf-8 -*-

import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup as bs, Tag
import tornado.escape

from .engines import EngineBase, KolaParser
from .fetchTools import RegularMatchUrl

# 获取商品价格
#https://p.3.cn/prices/mgets?callback=jQuery2818475&type=1&area=1_72_4137&skuIds=J_1005131698%2CJ_1005388333

# 获取商品介绍
# https://d.3.cn/desc/1247820412?cdn=2&callback=showdesc

# https://item.jd.com/2004260.html
class ParserGoodsDetailed(KolaParser):
    def __init__(self, url=None, data=None):
        super().__init__()
        if url:
            self.cmd['source'] = url
            self.cmd['cache']  = True
            if data:
                self.cmd['private'] = data

    def CmdParser(self, js):
        data = js['private']
        soup = bs(js['data'], "html.parser")  # , from_encoding = 'GBK')

        # 大图浏览
        # <div class="spec-items">
        #     <ul class="lh">
        #         <li>
        #             <img class='img-hover' alt='珍享 新西兰皇后红玫瑰苹果 6个 单果约220g 自营水果' src='//img10.360buyimg.com/n5/jfs/t2794/56/2909137585/171700/73700eff/5779c08bN2987c800.jpg' data-url='jfs/t2794/56/2909137585/171700/73700eff/5779c08bN2987c800.jpg' data-img='1' width='50' height='50'>
        #         </li>
        #         <li>
        #             <img alt='珍享 新西兰皇后红玫瑰苹果 6个 单果约220g 自营水果' src='//img10.360buyimg.com/n5/jfs/t2944/353/1205674983/145905/64bc3794/5779c08cN4af2a285.jpg' data-url='jfs/t2944/353/1205674983/145905/64bc3794/5779c08cN4af2a285.jpg' data-img='1' width='50' height='50'>
        #         </li>
        #         <li>
        #             <img alt='珍享 新西兰皇后红玫瑰苹果 6个 单果约220g 自营水果' src='//img10.360buyimg.com/n5/jfs/t2929/53/1193086082/117523/8cfc41b3/5779c08dNf266dc74.jpg' data-url='jfs/t2929/53/1193086082/117523/8cfc41b3/5779c08dNf266dc74.jpg' data-img='1' width='50' height='50'>
        #         </li>
        #     </ul>
        # </div>
        spec_items = soup.findAll('div', {'class' : 'spec-items'})
        if spec_items:
            images = []
            for i in spec_items[0].findAll('img', {'data-img': '1'}):
                images.append(i['data-url'])
            if images:
                data['images'] = images

        # 选择种类
        # <div id="choose-color" class="li choose-color-shouji p-choose">
        #     <div class="dt">选择种类：</div>
        #     <div class="dd">
        #         <div class="item">
        #             <b></b><a href="//item.jd.com/2004259.html" title="2个装" clstag="shangpin|keycount|product|yanse-2个装"><img data-img="1" src="//img14.360buyimg.com/n9/jfs/t2782/112/2922531867/118140/b939110f/5779c073N1f6a5b7b.jpg" width="25" height="25" alt="2个装"><i>2个装</i></a>
        #         </div>
        #         <div class="item">
        #             <b></b><a href="//item.jd.com/2004260.html" title="6个装" clstag="shangpin|keycount|product|yanse-6个装"><img data-img="1" src="//img10.360buyimg.com/n9/jfs/t2794/56/2909137585/171700/73700eff/5779c08bN2987c800.jpg" width="25" height="25" alt="6个装"><i>6个装</i></a>
        #         </div>
        #         <div class="item">
        #             <b></b><a href="//item.jd.com/2004281.html" title="12个装" clstag="shangpin|keycount|product|yanse-12个装"><img data-img="1" src="//img11.360buyimg.com/n9/jfs/t2911/99/1399269561/167936/6ef1354a/577f6b4fN4f3ca4c9.jpg" width="25" height="25" alt="12个装"><i>12个装</i></a>
        #         </div>
        #     </div>
        # </div>        
        choose_color = soup.findAll('div', {'id' : 'choose-color'})
        if choose_color:
            chooses = []
            for a in choose_color[0].findAll('a'):
                chooses.append(urljoin('https://list.jd.com', a['href']))
            if chooses:
                data['choose-color'] = chooses

        # 商品参数
        # <div class="p-parameter" clstag="shangpin|keycount|product|canshuqu_2">
        #   <ul id="parameter-brand" class="p-parameter-list">
        #     <li title='珍享'>品牌： 
        #       <a href='//list.jd.com/list.html?cat=12218,12221,13554&ev=exbrand_113411' clstag='shangpin|keycount|product|pinpai_2' target='_blank'>珍享</a>
        #       <a href="#none" clstag='shangpin|keycount|product|guanzhupinpai' class="follow-brand btn-def"><b>&hearts;</b>关注</a>
        #     </li>
        #   </ul>
        #   <ul id="parameter2" class="p-parameter-list">
        #     <li title='珍享新西兰皇后红玫瑰苹果'>商品名称：珍享新西兰皇后红玫瑰苹果</li>
        #     <li title='2004260'>商品编号：2004260</li>
        #     <li title='1.57kg'>商品毛重：1.57kg</li>
        #     <li title='新西兰'>商品产地：新西兰</li>
        #     <li title='1kg-2kg'>重量：1kg-2kg</li>
        #     <li title='红玫瑰'>分类：红玫瑰</li>
        #     <li title='80mm-85mm'>果实直径：80mm-85mm</li>
        #     <li title='礼盒装'>包装：礼盒装</li>
        #     <li title='进口'>国产/进口：进口</li>
        #     <li title='新西兰'>原产地：新西兰</li>
        #   </ul>
        #   <p class="more-par"><a href="#product-detail" class="J-more-param">更多参数&gt;&gt;</a><p>
        # </div>
        parameter = soup.findAll('div', {'class' : 'p-parameter'})
        if parameter:
            param = {}
            for p in parameter[0].findAll('li'):
                t = p.text.replace('\n♥关注\n', '')
                k,v = t.split('：')
                param[k] = v
            if param:
                data['parameter'] = param

        # 商品详细介绍（图片列表）
        desc = re.findall("desc: '([\s\S]*?)',", js['data'])
        if desc:
            url = urljoin('https://d.3.cn/desc/', desc[0])
            text = RegularMatchUrl(url, "showdesc\((.*)\)")
            if text:
                showdesc = tornado.escape.json_decode(text)
                data['content'] = showdesc['content']

        return True, data

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

        data = []
        goodsList = soup.findAll('div', {'class' : 'gl-i-wrap j-sku-item'})
        for p in goodsList:
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

            goods = {}
            if 'data-sku' in p.attrs:
                goods['data-sku'] = p.attrs['data-sku']
            if 'venderid' in p.attrs:
                goods['venderid'] = p.attrs['venderid']

            # 取图片信息
            data_img = p.findAll('img', {'data-img': '1'})
            if data_img:
                if 'src' in data_img[0]:
                    goods['data-img'] = urljoin('https://list.jd.com', data_img[0]['data-lazy-img'])
                elif 'data-lazy-img' in data_img[0]:
                    goods['data-img'] = urljoin('https://list.jd.com', data_img[0]['data-lazy-img'])
                pass

            # 取商品名称与详细介绍
            p_name = p.findAll('div', {'class': 'p-name'})
            if p_name:
                goods['p-name'] = p_name[0].text.strip()

            if type(p_name[0]) == Tag:
                for t in p_name[0].contents:
                    if type(t) == Tag:
                        url = urljoin('https://list.jd.com', t['href'])
                        goods['desc'] = url
                        ParserGoodsDetailed(url, goods).Execute()
            data.append(goods)

        # 下一页
        # [<a class="pn-next" href="/list.html?cat=12218,12221&amp;page=2&amp;go=0&amp;JL=6_0_0">下一页<i>&gt;</i></a>]
        next_text = soup.findAll('a', {'class' : 'pn-next'})
        for a in next_text:
            href = "https://list.jd.com" + a.attrs['href']
            ParserGoodsList(href).Execute()
            print(href)

        return True, None

# JD 搜索引擎
class JDEngine(EngineBase):
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
