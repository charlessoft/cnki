# -*- coding: utf-8 -*-

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

import config

engine = create_engine(config.dbpath, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
session = db_session()
Base = declarative_base()
Base.query = db_session.query_property()

# def build_daily_history_table_repr(self):
#     return "<" + self.__tablename__ + "('{}','{}','{}','{}','{}','{}','{}','{}')>".format(self.id, self.date, self.open,
#                                                                                           self.high, self.low,
#                                                                                           self.close, self.volume,


class Periodical():
    id = Column(Integer, primary_key=True, autoincrement=True)
    year = Column(Integer)
    issue = Column(String(10))
    url = Column(String(255))
    title = Column(String(255))
    author = Column(String(100))
    organization = Column(String(100))  # 单位
    summary = Column(String(10000))  # 摘要
    keyword = Column(String(100))  # 摘要
    createtime = Column(DateTime)
    updatetime = Column(DateTime)
    # content = Column(String(10000))
    fund = Column(String(100))
    doi = Column(String(100))
    ZTCLS = Column(String(100))
    state = Column(Boolean)
    pdf = Column(String(200))
    # year issue url title createtime updatetime content
    def __repr__(self):
        return "<Article(year='%d', issue='%s', title='%s')>" % (self.year, self.issue, self.title)


def build_periodical_table(periodical):
    classname = periodical + '_auto'
    item = type(classname, (Base, Periodical), {'__tablename__': periodical})
    # ticket.__repr__ = build_daily_history_table_repr
    item.__table__.create(bind=engine, checkfirst=True)
    return item
