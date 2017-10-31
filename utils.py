# -*- coding: utf-8 -*-
import os

import time

import datetime
import unicodecsv as csv
from sqlalchemy import exists, and_

from logconfig import logger
from models import session


def append_to_csv(path, content):
    """
    写入csv
    :param path:
    :param content:
    :return:
    """
    try:
        if not os.path.exists(path):
            with open(path, "w") as csvfile:
                writer = csv.DictWriter(csvfile, content.keys())
                writer.writeheader()
                writer.writerow(content)
                csvfile.close()
        else:
            with open(path, 'ab') as csvfile:
                writer = csv.DictWriter(csvfile, content.keys())
                writer.writerow(content)
                csvfile.close()

    except Exception, e:
        logger.error(e)


def query_crawl_success(model, urls):
    try:
        for url in urls:
            if not session.query(
                    exists().where(and_(model.url == url, model.state == 1))).scalar():
                yield url

    except Exception, e:
        logger.error(e)


def save_crawl_result(model, res):
    try:
        if not session.query(
                exists().where(and_(model.url == res['url'],model.state == res['state']))).scalar():
            session.add(model(year=res['year'], issue=res['issue'], url=res['url'],
                              title=res['title'],
                              author=res['author'],
                              organization=res['organization'],
                              summary=res['summary'],
                              keyword=res['keyword'],
                              state=res['state'],
                              createtime=datetime.datetime.now(),
                              updatetime=datetime.datetime.now()))
        else:
            res['updatetime'] = time.time()
            session.filter(model.url == res['url']).update(res)

        session.commit()
    except Exception, e:
        logger.error(e)
        session.rollback()
        session.flush()
