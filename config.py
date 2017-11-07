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
download_pdf_interval = 0

filter_year_lst = ['2017', '2016', '2015', '2014', ]
filter_No_list = ['No.36', 'No.35', 'No.34', 'No.33', 'No.32', 'No.31', 'No.30', 'No.29',
                  'No.28', 'No.27', 'No.26', 'No.25', 'No.24', 'No.23', 'No.22',
                  'No.21', 'No.20', 'No.19', 'No.18', 'No.17', 'No.16', 'No.15',
                  'No.14', 'No.13', 'No.12', 'No.11', 'No.10', 'No.09', 'No.08',
                  'No.07', 'No.06', 'No.05', 'No.04', 'No.03', 'No.02']

# 配置爬虫地址 for v1(
#dest_url = "http://navi.cnki.net/knavi/JournalDetail?pcode=CJFD&pykm=ZGDC"

# 爬取页数5页  for v1
#spidernum = 5
