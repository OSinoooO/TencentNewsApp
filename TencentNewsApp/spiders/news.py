# -*- coding: utf-8 -*-
import re
from copy import deepcopy
import scrapy
import json
from ..settings import NEWS_ALL_PAGE, PLATES, COMMENT_ALL_PAGE
from ..items import TencentnewsappItem


class NewsSpider(scrapy.Spider):
    name = 'news'
    allowed_domains = ['inews.qq.com']
    plates_code = dict(news_news_recommend='推荐', news_news_top='要闻', news_news_ent='娱乐', news_news_19='新时代',
                       news_news_sports='体育', news_news_mil='军事', news_news_nba='NBA', news_news_game='游戏',
                       news_news_world='国际', news_news_tech='科技', news_news_finance='财经', news_news_auto='汽车',
                       news_news_movie='电影', news_news_zongyi='综艺', news_news_food='美食', news_news_orignal='眼界',
                       news_news_istock='股票', news_news_kepu='科学', news_news_health='健康', news_news_5g='5G',
                       news_news_university='追光少年', news_news_agri='三农', news_news_tencentgy='公益', news_news_acg='二次元',
                       news_news_netcourt='政法网事', news_news_twentyf='必读', news_news_nflfootball='NFL',
                       news_news_cba='CBA', news_news_icesnow='冰雪', news_news_football='足球', news_news_media='传媒',
                       news_news_music='音乐', news_news_history='历史', news_news_pet='宠物', news_news_baby='育儿',
                       news_news_visit='旅游', news_news_meirong='美容', news_news_edu='教育', news_news_astro='星座',
                       news_news_digi='数码', news_news_esport='电竞', news_news_jiaju='家居', news_news_msh='政务',
                       news_news_olympic='综合体育', news_news_pplvideo='人民视频', news_news_legal='法制',
                       news_news_workplace='职场', news_news_emotion='情感', news_news_lic='理财', news_news_fx='新国风',
                       news_news_house='房产', news_news_cul='文化', news_news_lad='时尚')
    plates = PLATES

    def start_requests(self):  # 生成起始网址
        url_model = 'https://r.inews.qq.com/getQQNewsUnreadList?chlid={}&page=0&forward=0&devid=863064010529115&appver=22_android_5.8.21'
        for plate in self.plates:
            if plate in self.plates_code.values():
                code = list(self.plates_code.keys())[list(self.plates_code.values()).index(plate)]
                yield scrapy.Request(url=url_model.format(code), callback=self.parse)

    def parse(self, response):  # 解析新闻列表页
        item = TencentnewsappItem()
        html = json.loads(response.text)
        # 提取新闻url
        news_list = html['newslist']
        for news in news_list:
            item['_id'] = news['id']
            item['url'] = news['url']
            item['title'] = news['title']
            item['time'] = news['time']
            item['uinnick'] = news['uinnick']
            item['source'] = news['source']
            item['type'] = news['realChlName']
            detail_url = 'https://r.inews.qq.com/getSimpleNews?id={}'.format(item['_id'])
            yield scrapy.Request(url=detail_url, callback=self.parse_detail, meta={'item': deepcopy(item)})
        # 下一页
        for page in range(NEWS_ALL_PAGE):
            next_url = re.sub(r'page=\d+&', 'page={}&'.format(page), response.url)
            yield scrapy.Request(url=next_url, callback=self.parse)

    def parse_detail(self, response):  # 解析新闻详情页
        item = response.meta.get('item')
        html = json.loads(response.text)
        item['comment_id'] = html['commentid']
        item['media_id'] = html['media_id']
        item['media_source'] = html['card']['chlname']
        if '<!--VIDEO_0-->' in html['content']['text']:
            item['is_video'] = 'yes'
            item['video_url'] = html['attribute']['VIDEO_0']['playurl']
        else:
            item['is_video'] = 'no'
            item['text'] = html['content']['text']
        if '<!--IMG_0-->' in html['content']['text']:
            imgs = []
            img_count = 0
            for img_info in html['attribute'].values():
                imgs.append(img_info['url'])
                img_count += 1
            item['imgs_url'] = imgs
        # 对接评论页(热评)
        comment_url = 'https://r.inews.qq.com/getQQNewsComment?showType=orig&comment_id={}'.format(item['comment_id'])
        yield scrapy.Request(url=comment_url, callback=self.parse_comment, meta={'item': item, 'commentid': item['comment_id']})

    def parse_comment(self, response):  # 解析评论页
        item = response.meta.get('item')
        commentid = response.meta.get('commentid')
        html = json.loads(response.body)
        coral_score = ''
        comment_list = html['comments']['new']
        item['comment_list'] = []
        for comment in comment_list:
            if comment is comment_list[-1]:
                coral_score = comment[0]['coral_score']
            comment_item = {}
            comment = comment[0]
            comment_item['comment_uid'] = comment['coral_uid']
            comment_item['comment_nick'] = comment['nick']
            comment_item['comment_content'] = comment['reply_content']
            comment_item['comment_agree_count'] = comment.get('agree_count', '')
            comment_item['reply_num'] = comment.get('reply_num', '')
            comment_item['reply_list'] = []
            reply_list = comment['reply_list']
            for reply in reply_list:
                reply_item = {}
                reply = reply[0]
                reply_item['reply_uid'] = reply['coral_uid']
                reply_item['reply_nick'] = reply['nick']
                reply_item['reply_content'] = reply['reply_content']
                reply_item['reply_agree_count'] = reply.get('agree_count', '')
                comment_item['reply_list'].append(reply_item)
            item['comment_list'].append(comment_item)
        # 评论翻页
        if coral_score:
            for i in range(COMMENT_ALL_PAGE):
                comment_url = 'https://r.inews.qq.com/getQQNewsComment?showType=orig&comment_id={}&coral_score={}'.format(commentid, coral_score)
                yield scrapy.Request(url=comment_url, callback=self.parse_comment, meta={'item': item})
        item['comment_count'] = html['comments']['count']
        yield item

