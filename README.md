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
1. 默认已经配置了4个期刊,直接运行







