# -*- coding: utf-8 -*-


class Article(object):
    def __init__(self):
        self.year = ''
        self.no = ''
        self.title = ''
        self.author = ''
        self.url = ''


class Periodical(object):
    def __init__(self):
        self.name = ''
        self.main_url = ''
        self.articles = []
        # self.year = ''
        # self.No = ''
        # self.articlelst = []
