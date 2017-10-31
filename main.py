# -*- coding: utf-8 -*-
import codecs
import json
import random
import urlparse
import os

import re
import requests
import time
import sys
from pyquery import PyQuery as pq
from requests.utils import dict_from_cookiejar

import config
from logconfig import logger

debug=False
if debug:
    proxy = '10.211.55.12:8888'
    # # ip = '10.142.54.165'
    # ip = '127.0.0.1'
    g_proxies = {'http': 'http://' + proxy, 'https': 'https://' + proxy}
else:
    g_proxies = {}




class Spider(object):
    def __init__(self):
        self.count = 0
        self.s = requests.session()
        self.s.headers.update({'Referer': config.dest_url,
                               'Origin': 'http://navi.cnki.net',
                               })
        self.lid = ''

    def validateTitle(self,title):
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
                r = self.s.get(url, proxies=g_proxies, verify=False, timeout=20)
            else:
                r = self.s.post(url, data=payload, proxies=g_proxies, verify=False, timeout=20)
            tmpdict = dict_from_cookiejar(r.cookies)

            self.lid = tmpdict.get("LID", "")
            # if self.lid != "":
            #     logger.info(("good!!!!!!!!! url:{}".format(url)))

            callback(r, savefolder, **kwargs)
        except Exception, e:
            logger.error('{},{}'.format(url, e))

    def onstart(self):
        """
        开始
        :return:
        """

        linidurl = 'http://kns.cnki.net/KLogin/Request/GetKFooter.ashx?callback=jsonp{}{}'.format(int(time.time()), random.randrange(100,999))
        logger.info("get_linid ")
        self.crawl_url(linidurl, 'get', '', self.get_linid, '')



        parsed = urlparse.parse_qsl(urlparse.urlparse(config.dest_url).query)
        url = 'http://navi.cnki.net/knavi/JournalDetail/GetnfAllOutline'

        for index in range(1, config.spidernum + 1):
            self.count = 0
            logger.info("=======>crawl page index: {}=======!".format(index))
            pagefoder = os.path.join(config.dest_folder, 'page' + str(index))
            if not os.path.exists(pagefoder):
                os.mkdir(os.path.join(pagefoder))

            payload = {
                'pageIdx': index,
                'type': 1
            }
            payload.update(dict([(k, v) for k, v in parsed]))
            logger.info("dest_url: " + url)
            self.crawl_url(url, "post", payload, self.get_list_root_page, pagefoder)

    def get_linid(self,response,savefolder,**kwargs):
        """
        获取linid
        :param response:
        :param savefolder:
        :param kwargs:
        :return:
        """
        logger.info("get lid {} !!".format(response.cookies.get('LID', 'not found')))
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
            self.crawl_url(each.attr('href'), "get", '', self.detail_page, savefolder, **kwargs)

    def down_pdf(self, response, savefolder, **kwargs):
        """
        下载pdf
        :param response:
        :param savefolder:
        :param kwargs:
        :return:
        """
        title = self.validateTitle(kwargs['filename'])+".pdf"
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

    def detail_page(self, response, savefolder, **kwargs):
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
        url = response.url
        content = doc(".wxBaseinfo > p").text()
        self.count += 1
        savefolder = os.path.join(savefolder, '%02d' % self.count)
        if not os.path.exists(savefolder):
            os.mkdir(savefolder)
        logger.info("download pdf: {}".format(pdf_url))

        pdf_url = self._generate_pdf_downloadurl(pdf_url)
        logger.info("download real pdf: {}".format(pdf_url))
        self.crawl_url(pdf_url, "get", '', self.down_pdf, savefolder,filename=title)

        result = {
            'title': title,
            'author': author,
            'url': url,
            'content': content,
            'pdf': os.path.join(savefolder + title + '.pdf')
        }
        # 保存当前目录
        self.dumpres(result, os.path.join(savefolder, "single.txt"), False)

        # 保存结果文件
        self.dumpres(result, config.restxt)

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
            logger.error("WARNNING no lid!!!! use default linid default linid: [{}] !".format(config.LinID))
            current_linid = config.LinID
        else:
            current_linid = self.lid
        dic = self._parse_url_query_todic(pdf_url)
        filename = dic.get('filename', 'error====______====')
        url = "http://ecppdown.cnki.net/cjfdsearch/pdfdownloadnew.asp?filename={}&filetitle=download&u={}".format(
            filename, current_linid)
        return url


if __name__ == '__main__':
    logger.info("init")
    if not os.path.exists(config.dest_folder):
        os.mkdir(config.dest_folder)
    s = Spider()
    s.onstart()
    logger.info(u"采集结束")
