# -*- coding: utf-8 -*-


spider_urls = [
    'http://navi.cnki.net/knavi/JournalDetail?pcode=CJFD&pykm=ZGDC',
    'http://navi.cnki.net/knavi/JournalDetail?pcode=CJFD&pykm=DWJS',
    "http://navi.cnki.net/knavi/JournalDetail?pcode=CJFD&pykm=GDYJ",
    "http://navi.cnki.net/knavi/JournalDetail?pcode=CJFD&pykm=DXXH"
]


# 保存采集结果pdf
dest_folder = "./res"

# 保存采集内容
restxt = "{}/res.txt".format(dest_folder)

# cook中获取
# LinID = 'WEEvREcwSlJHSldRa1FhcEE0NXh1akk1S002emdOVXRyNVJYRHFNRDhTWT0=$9A4hF_YAuvQ5obgVAqNKPCYcEjKensW4ggI8Fm4gTkoUKaID8j8gFw!!'
LinID=''

# 数据库存储路径
dbpath = 'sqlite:///./res/spider.db'

# 间隔5小时继续跑
interval = 900

# 下载pdf 间隔
download_pdf_interval = 10


# 配置爬虫地址 for v1(
#dest_url = "http://navi.cnki.net/knavi/JournalDetail?pcode=CJFD&pykm=ZGDC"

# 爬取页数5页  for v1
#spidernum = 5
