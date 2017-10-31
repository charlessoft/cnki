# -*- coding: utf-8 -*-
import codecs
import json
import random
import urlparse
import os
import sys

import re
import requests
import time
from pyquery import PyQuery as pq
from requests.utils import dict_from_cookiejar

import config
import utils
from logconfig import logger

import models

debug = False
if debug:
    # proxy = '10.211.55.12:8888'
    # proxy = '172.16.133.42:8888'
    proxy = '127.0.0.1:8888'

    # # ip = '10.142.54.165'
    # ip = '127.0.0.1'
    g_proxies = {'http': 'http://' + proxy, 'https': 'https://' + proxy}
else:
    g_proxies = {}


class Spider(object):
    def __init__(self, dest_url):
        self.count = 0
        self.s = requests.session()
        self.s.headers.update({'Referer': dest_url,
                               'Origin': 'http://navi.cnki.net',
                               })
        self.lid = ''
        self.state = True
        self.start_url = dest_url
        logger.info("start_url: {}".format(self.start_url))
        # 期刊名字
        self.periodcical_name = ''

        parsed = self._parse_url_query_todic(dest_url)
        self.pykm = parsed['pykm']

        # 创建表模型
        self.model = models.build_periodical_table(self.pykm)

    # def query_crawl_success(self,url):
    #     models.session.query(self.model).filter(and_(self.model.url == url,self.model.state=True)).count()



    def validateTitle(self, title):
        """
        过滤pdf无效名字
        :param title:
        :return:
        """
        rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/\:*?"<>|'
        new_title = re.sub(rstr, "", title)
        return new_title

    def crawl_url(self, url, method, payload, callback, savefolder, **kwargs):
        """
        crawl url 函数
        :param url:
        :param method:
        :param payload:
        :param callback:
        :param savefolder:
        :param kwargs:
        :return:
        """
        try:
            time.sleep(0.5)
            if method == "get":
                r = self.s.get(url, proxies=g_proxies, params=payload, verify=False, timeout=20)
            else:
                logger.info('url ...... post')
                r = self.s.post(url, data=payload, proxies=g_proxies, verify=False, timeout=20)
            tmpdict = dict_from_cookiejar(r.cookies)

            self.lid = tmpdict.get("LID", "")
            # if self.lid != "":
            #     logger.info(("good!!!!!!!!! url:{}".format(url)))
            # logger.info("====curl=====begin ")
            # logger.info('header={}'.format(self.s.headers))

            # # for k,v in r.cookies.items():
            # # 	logger.info("{}:{}".format(k,v))
            # logger.info("====curl=====end ")
            if callback:
                callback(r, savefolder, **kwargs)
            else:
                return r
        except Exception, e:
            logger.error('{}, {},{}'.format(e, url, e.message))
            self.state = False
            return False

    def onstart(self):
        """
        开始
        :return:
        """

        # 获取首页信息,获取期刊名字
        self.crawl_url(self.start_url, 'get', '', self.periodcial_main, '')

        # 获取授权信息
        linidurl = 'http://kns.cnki.net/KLogin/Request/GetKFooter.ashx?callback=jsonp{}{}'.format(int(time.time()),
                                                                                                  random.randrange(100,
                                                                                                                   999))
        logger.info("get_linid ")
        self.crawl_url(linidurl, 'get', '', self.get_linid, '')

        # parsed [('pcode', 'CJFD'), ('pykm', 'ZGDC')]
        parsed = self._parse_url_query_todic(self.start_url)
        # 获取年份列表.
        self.start_craw_yearissuepage_list(parsed)

    def periodcial_main(self, response, savefolder, **kwargs):
        """
        获取首页信息,获取期刊名字
        :param response:
        :param savefolder:
        :param kwargs:
        :return:
        """
        doc = pq(unicode(response.content, "utf-8"))
        self.periodcical_name = doc(".titbox").text()

    def start_craw_yearissuepage_list(self, query):
        """
        爬取年份列表
        :param query:
        :return:
        """
        url = "http://navi.cnki.net/knavi/JournalDetail/GetJournalYearList"
        params = {
            "pIdx": 0,
        }
        params.update(query)
        self.crawl_url(url, 'get', params, self.on_yearissuepage_list,
                       os.path.join(config.dest_folder, self.periodcical_name), **query)

    def on_article_list(self, response, savefolder, **kwargs):
        doc = pq(unicode(response.content, "utf-8"))
        doc.make_links_absolute("http://navi.cnki.net/knavi/")
        logger.info("on _article_ list")
        crawl_urls = []
        for each in doc(".row >span > a").items():
            # each.attr("href")
            # http://navi.cnki.net/knavi/Common/RedirectPage?sfield=FN&dbCode=CJFD&filename=ZGDC201719001&tableName=CJFDPREP&url=
            # 内部会重定向,直接构造
            # http://kns.cnki.net/kcms/detail/detail.aspx?dbcode=CJFD&filename=ZGDC201719001&dbname=CJFDPREP
            parsed = self._parse_url_query_todic(each.attr("href"))
            url = 'http://kns.cnki.net/kcms/detail/detail.aspx?dbcode={}&filename={}&dbname={}'.format(
                parsed['dbCode'],
                parsed['filename'],
                parsed['tableName']
            )
            crawl_urls.extend(utils.query_crawl_success(self.model, [url]))
        logger.info("crawl_urls: {}".format(len(crawl_urls)))
        for url in crawl_urls:
            # self.get_detail_page(url)
            # wrapper_url = '{}&uid={}'.format(url, self.lid)
            # logger.info("detail_page > {}".format(wrapper_url))

            self.crawl_url(url, 'get', '', self.on_detail_page, savefolder, **kwargs)

    def on_yearissuepage_list(self, response, savefolder, **kwargs):
        """
        返回年份列表
        :param response:
        :param savefolder:
        :param kwargs:
        :return:
        """

        # <dl id="2017_Year_Issue" class="s-dataList clearfix ">
        # <dt onclick="JournalDetail.BindYearClick(this);"><em>2017</em></dt>
        # <dd>
        # <a id="yq201719" onclick="JournalDetail.BindIssueClick(this)">No.19</a>

        doc = pq(unicode(response.content, "utf-8"))
        doc.make_links_absolute("http://navi.cnki.net/knavi/")

        for each in doc(".yearissuepage> .s-dataList").items():

            yearlstdoc = pq(each)
            year = yearlstdoc("em").text()
            for item in yearlstdoc("a").items():
                No = item.text()
                url = "http://navi.cnki.net/knavi/JournalDetail/GetArticleList?year={}&issue={}&pykm={}&pageIdx=0".format(
                    year,
                    No[3:], kwargs['pykm'])
                logger.info("get article list by year:{} issue:{}".format(year, No))
                kwargs.update(
                    {'year': year,
                     'issue': No}
                )
                self.crawl_url(url, 'get', '', self.on_article_list,
                               os.path.join(savefolder, year, No), **kwargs)

    def get_linid(self, response, savefolder, **kwargs):
        """
        获取linid
        :param response:
        :param savefolder:
        :param kwargs:
        :return:
        """
        logger.info("get lid {} !!".format(response.cookies.get('LID', 'not found')))
        # logger.info(response.content)
        # for k, v in response.cookies.items():
        #     print k,v
        pass

    def down_pdf(self, response, savefolder, **kwargs):
        """
        下载pdf
        :param response:
        :param savefolder:
        :param kwargs:
        :return:
        """
        title = self.validateTitle(kwargs['filename']) + ".pdf"
        filename = u'{}'.format(os.path.join(savefolder, title))
        # logger.error (response.status_code)
        filelen = response.headers.get('Content-Length', 1000)
        logger.info("len: {} ".format(filelen))
        if int(filelen) <= 1000:
            logger.info(response.content)
            logger.info(u"fail......fail...下载次数太多.等待{}秒重新下载".format(config.interval))
            time.sleep(int(config.interval))
            logger.info("sleep interval ....ok exit")
            sys.exit(1)
            self.state = False
            raise Exception("error filelen < 1000,may be error")

        logger.info("SSSDADADAD+#!@#@##")
        try:
            f = open(filename, 'wb')
            f.write(response.content)
            f.close()
        except Exception, e:
            self.state=False
            logger.error('write file error: ' + title + e)
            try:
                f = open('download.pdf', 'wb')
                f.write(response.content)
                f.close()
            except Exception, e:
                logger.error(e)


    def dumpres(self, result, filename, bappend=True):
        """
        输出采集结果
        :param result:
        :param filename:
        :return:
        """

        if bappend:
            f = codecs.open(filename, "ab", 'utf-8')
        else:
            f = codecs.open(filename, "wb", 'utf-8')
        json.dump(
            result, f, ensure_ascii=False)
        f.write("\r\n")
        f.close()

    def on_detail_page(self, response, savefolder, **kwargs):
        """
        详细页
        :param response:
        :param savefolder:
        :param kwargs:
        :return:
        """
        doc = pq(response.content)
        pdf_url = doc(".wxBaseinfo .icon-dlpdf").attr('href')
        title = doc(".wxTitle > .title").text()
        author = doc(".author").text()  # 作者
        summary = doc(".wxBaseinfo > p >span").text()  # 摘要
        fund = doc(".wxBaseinfo > p").eq(1)("a").text()  # 基金
        keyword = doc(".wxBaseinfo > p").eq(2).text()  # 关键字
        doi = doc(".wxBaseinfo > p").eq(3).text()  # doi
        ZTCLS = doc(".wxBaseinfo > p").eq(4).text()  # 分类号
        organization = doc(".orgn").text()
        url = response.url
        content = doc(".wxBaseinfo > p").text()
        self.count += 1
        # savefolder = os.path.join(savefolder, '%02d' % self.count)
        if not os.path.exists(savefolder):
            os.makedirs(savefolder)
        # logger.info("download pdf: {}".format(pdf_url))

        # "=======pdf"
        # self.crawl_url(pdf_url, "get", '', self.down_pdf, savefolder,filename=title)
        # 下载 pdf
        self.deal_pdf_page(url, savefolder, filename=title)
        # "=======pdf"
        if self.state == False:
            return

        result = {
            'fund':fund,
            'doi':doi,
            'ZTCLS':ZTCLS,
            'title': title,
            'author': author,
            'url': url,
            # 'content': content,
            'pdf': os.path.join(savefolder + title + '.pdf'),
            'summary': summary,
            'organization': organization,
            'keyword': keyword,
            'year': kwargs['year'],
            'issue': kwargs['issue'],
            'state': self.state
        }
        # utils.append_to_csv("{}/{}.csv".format(savefolder, self.periodcical_name), result)

        # 保存文件到csv 和数据库
        csv_path = savefolder + "/" + self.periodcical_name + "-" + str(kwargs['year']) + "-" + kwargs['issue'] + ".csv"
        utils.append_to_csv(csv_path, result)
        utils.save_crawl_result(self.model, result)

    # utils.append_to_csv("/tmp/accc.cav",result)
    # 保存当前目录
    # self.dumpres(result, os.path.join(savefolder, "single.txt"), False)

    # 保存结果文件
    # self.dumpres(result, config.restxt)


    def _parse_url_query_todic(self, url):
        """
        url 参数转字典
        :param url:
        :return:
        """
        parsed = urlparse.parse_qsl(urlparse.urlparse(url).query)
        return dict([(k, v) for k, v in parsed])

    def _generate_pdf_downloadurl(self, pdf_url):
        """
        获取真实 PDF地址
        :param pdf_url:
        :return:
        """
        if self.lid == '':
            logger.warning("WARNNING no lid!!!! use default linid default linid: [{}] !".format(config.LinID))
            current_linid = config.LinID
        else:
            current_linid = self.lid
        dic = self._parse_url_query_todic(pdf_url)
        filename = dic.get('filename', 'error====______====')
        url = "http://ecppdown.cnki.net/cjfdsearch/pdfdownloadnew.asp?filename={}&filetitle=download&u={}".format(
            filename, current_linid)
        return url

    def getlogo_gif(self):
        """
        获取登录cookie sid_kns
        :return:
        """
        url = "http://kns.cnki.net/kns/images/gb/logo.gif"
        r = self.crawl_url(url, 'get', '', None, '')

    def deal_pdf_page(self, detail_page_url, savefolder, **kwargs):
        """
        下载最终pdf
        :param detail_page_url:
        :param savefolder:
        :param kwargs:
        :return:
        """
        url = detail_page_url
        # url = 'http://kns.cnki.net/kcms/detail/detail.aspx?dbcode=CJFD&filename=ZGDC201719001&dbname=CJFDTEMP'
        self.s.headers.update({
            'Referer': url
        })
        r = self.crawl_url(url, 'get', '', None, '')
        doc = pq(r.content)
        self.pdf_url = doc(".wxBaseinfo .icon-dlpdf").attr('href').strip()
        logger.info("get pdf_url:{}".format(self.pdf_url))
        # for k,v in  r.cookies.items():
        # 	print k,v

        self.iplogin_flush()

        self.getlogo_gif()

        self.post_detail_url()

        self.start_download_pdf(savefolder, **kwargs)

    def iplogin_flush(self):
        url = "http://login.cnki.net/TopLogin/api/loginapi/IpLoginFlush?callback=jQuery111307519162754265742_{}{}&_={}{}".format(
            int(time.time()),
            random.randrange(100,
                             999),
            int(time.time()),
            random.randrange(100,
                             999))
        payload = {}
        logger.info("iplogin_flush")
        r = self.crawl_url(url, 'get', '', None, '')
        # r = self.s.get(url, proxies=g_proxies, params=payload, verify=False, timeout=20)
        # for k,v in r.cookies.items():
        # 	print k,v
        self.lid = r.cookies['LID']

    # logger.info(self.lid)

    def post_detail_url(self):
        url = "http://kns.cnki.net/kcms/detail/detail.aspx?dbcode=CJFD&filename=ZGDC201719001&dbname=CJFDTEMP"
        payload = {
            "uid": self.lid
        }
        headers = {"referer": url}

        r = self.s.post(url, proxies=g_proxies, data=payload, verify=False, timeout=20)

    # for k,v in r.cookies.items():
    # 	print k,v

    def start_download_pdf(self, savefolder, **kwargs):
        logger.info("download_pdf")
        url = self.pdf_url
        logger.info("downoad pdf url: {}".format(url))
        payload = {}
        self.crawl_url(url, 'get', '', self.down_pdf, savefolder, **kwargs)

        # r = self.s.get(url, proxies=g_proxies, data=payload, verify=False, timeout=20)
        # open("c:\\dd.pdf",'wb').write(r.content)
        # self.crawl_url(url,'get','',)


if __name__ == '__main__':
    # logger.info("init")
    # s = Spider('http://navi.cnki.net/knavi/JournalDetail?pcode=CJFD&pykm=ZGDC')
    # s.get_detail_page()
    # if not os.path.exists(config.dest_folder):
    #     os.mkdir(config.dest_folder)
    #
    while True:
        for url in config.spider_urls:
            s = Spider(url)
            s.onstart()
            #     logger.info(u"采集完毕,休息{}秒".format(config.interval))
            #     #time.sleep(config.interval)
            time.sleep(int(config.interval))


            # time.sleep(1)
    logger.info(u"采集结束")
