## 环境要求：
1.服务器为Linux环境中（Centos6.5以上或RHEL Linux）
2.服务器IP需在CNKI认证范围内（即，通过该IP确保可以自由下载CNKI论文）

## 安装步骤
 1. 拷贝cnki-release.tar.gz文件到服务器，解压后进入目录
 2. 执行命令: 
    make install_source_pyenv
 3. 修改配置config.py 默认采集5页 支持列表期刊搜索,修改dest_url
 4. 执行命令: 
    make run
 5. 查看论文下载结果（在cnki-release/res目录）

## 可配置项说明
1. 本程序默认下载《中国电机工程学报》最近100篇论文。如果需要调整期刊或下载篇数，可修改config.py文件。包括：
“dest_url” 修改为需要下载的期刊首页（如《中国电机工程学报》对应"http://navi.cnki.net/knavi/JournalDetail?pcode=CJFD&pykm=ZGDC"）
“spidernum”修改为需要下载的列表页数（每页20篇）







