# -*- coding: utf-8 -*-
import codecs
import json
import random
import urlparse
import os

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
    proxy = '10.211.55.12:8888'
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
            logger.info("====curl=====begin ")
            logger.info('header={}'.format(self.s.headers))

            for k,v in r.cookies.items():
                logger.info("{}:{}".format(k,v))
            logger.info("====curl=====end ")

            callback(r, savefolder, **kwargs)
        except Exception, e:
            logger.error('{}, {},{}'.format(e, url, e.message))
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

        # parsed = urlparse.parse_qsl(urlparse.urlparse(config.dest_url).query)
        # url = 'http://navi.cnki.net/knavi/JournalDetail/GetnfAllOutline'
        #
        # for index in range(1, config.spidernum + 1):
        #     self.count = 0
        #     logger.info("=======>crawl page index: {}=======!".format(index))
        #     pagefoder = os.path.join(config.dest_folder, 'page' + str(index))
        #     if not os.path.exists(pagefoder):
        #         os.mkdir(os.path.join(pagefoder))
        #
        #     payload = {
        #         'pageIdx': index,
        #         'type': 1
        #     }
        #     payload.update(dict([(k, v) for k, v in parsed]))
        #     logger.info("dest_url: " + url)
        #     self.crawl_url(url, "post", payload, self.get_list_root_page, pagefoder)

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
            wrapper_url = '{}&uid={}'.format(url, self.lid)
            logger.info("detail_page > {}".format(wrapper_url))

            self.crawl_url(wrapper_url, 'post', {'uid':self.lid}, self.on_detail_page, savefolder, **kwargs)

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


                # http://navi.cnki.net/knavi/JournalDetail/GetArticleList?year=2017&issue=19&pykm=ZGDC&pageIdx=0

                # for item in pq(response.content)(".yearissuepage").items():
                #     print item

    def get_periodical_list(self, response, savefolder, **kwargs):
        """
        获取期刊列表
        :return:
        """
        url = "http://navi.cnki.net/knavi/JournalDetail/GetJournalYearList"
        params = {
            "pIdx": 0,
        }
        # params.update(query)
        # self

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

    def get_list_root_page(self, response, savefolder, **kwargs):
        """
        获取列表页
        :param response:
        :param savefolder:
        :param kwargs:
        :return:
        """
        doc = pq(unicode(response.content, "utf-8"))
        doc.make_links_absolute("http://navi.cnki.net/knavi/")
        for each in doc(".name > a").items():
            logger.info("index: [" + str(self.count) + "] crawl_name: " + each.text() + " url: " + each.attr("href"))
            # logger.info("index: {} crawl_name: {} url: {}".format(self.count, each.text(), each.attr('href')))
            self.crawl_url(each.attr('href'), "get", '', self.on_detail_page, savefolder, **kwargs)

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
        try:
            f = open(filename, 'wb')
            f.write(response.content)
            f.close()
        except Exception, e:
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
        author = doc(".author").text()
        summary = doc(".wxBaseinfo > p >span").text()
        organization = doc(".orgn").text()
        keyword = doc(".wxBaseinfo > p").eq(1).remove("label").text()

        url = response.url
        content = doc(".wxBaseinfo > p").text()
        self.count += 1
        # savefolder = os.path.join(savefolder, '%02d' % self.count)
        if not os.path.exists(savefolder):
            os.makedirs(savefolder)
        logger.info("download pdf: {}".format(pdf_url))

        # pdf_url = self._generate_pdf_downloadurl(pdf_url)
        # logger.info("download real pdf: {}".format(pdf_url))

        # "=======pdf"

        self.crawl_url(pdf_url, "get", '', self.down_pdf, savefolder,filename=title)
        # "=======pdf"

        result = {
            'title': title,
            'author': author,
            'url': url,
            # 'content': content,
            'pdf': os.path.join(savefolder + title + '.pdf'),
            'summary':summary,
            'organization':organization,
            'keyword':keyword,
            'year':kwargs['year'],
            'issue':kwargs['issue'],
            'state': True  # 有坑.
        }
        # utils.append_to_csv("{}/{}.csv".format(savefolder, self.periodcical_name), result)

        # 保存文件到csv 和数据库
        csv_path = savefolder + "/" + self.periodcical_name + "-" + str(kwargs['year']) + "-" + kwargs['issue'] + ".csv"
        utils.append_to_csv(csv_path , result)
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

    def test(self):
        # 获取授权信息
        linidurl = 'http://kns.cnki.net/KLogin/Request/GetKFooter.ashx?callback=jsonp{}{}'.format(int(time.time()),
                                                                                                  random.randrange(100,
                                                                                                                   999))
        logger.info("get_linid ")
        self.crawl_url(linidurl, 'get', '', self.get_linid, '')



        logger.info("begin get test====")

        # 第一次 get url 请求
        first_get_url = "http://kns.cnki.net/kcms/detail/detail.aspx?dbcode=CJFD&filename=ZGDC201718008&dbname=CJFDPREP&uid={}".format(self.lid)
        headers ={'Origin':'http://kns.cnki.net',
                  'Referer': 'http://navi.cnki.net/knavi/JournalDetail?pcode=CJFD&pykm=ZGDC'}

        r = self.s.get(first_get_url, headers=headers)
        logger.info(r.content)

        doc = pq(r.content)
        get_pdf_url = doc(".wxBaseinfo .icon-dlpdf").attr('href')
        logger.info(get_pdf_url)


        payload = {'uid':self.lid}
        headers={
            'referer':first_get_url
        }
        logger.info(u"====第2次post:{}".format(first_get_url))
        r = self.s.post(first_get_url, data=payload, headers=headers)

        deatai_url = get_pdf_url + '&tablename=CJFDPREP&dflag=pdfdown'
        logger.info("get ..pdf...pdf.. detail____url:{}".format(deatai_url))

        headers= {
            'referer':first_get_url
        }
        r = self.s.get(deatai_url,headers=headers)

        logger.info(r.status_code)
        logger.info(r.content)

    def on_get_test(self, response, savefolder, **kwargs):
        logger.info("=====on_get_test======")
        for k,v in response.cookies.items():
            logger.info("{}:{}".format(k,v))
        logger.info("cookie end....")
        logger.info(response.content)








if __name__ == '__main__':
    logger.info("init")
    s = Spider('http://navi.cnki.net/knavi/JournalDetail?pcode=CJFD&pykm=ZGDC')
    s.test()
    # if not os.path.exists(config.dest_folder):
    #     os.mkdir(config.dest_folder)
    #
    # while True:
    #     for url in config.spider_urls:
    #         s = Spider(url)
    #         s.onstart()
    #     logger.info(u"采集完毕,休息{}秒".format(config.interval))
    #     #time.sleep(config.interval)
    #     time.sleep(int(config.interval))


        # time.sleep(1)
    logger.info(u"采集结束")
