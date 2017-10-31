cp:
	scp -r ../cnki root@192.168.4.11:/tmp
cp_release:
	scp -r ./cnki-release.tar.gz root@192.168.4.11:/tmp


clean:
	rm -fr ./res 
	rm -fr ./res.txt
	rm -fr *.pyc
	rm -fr *.zip
	rm -fr cnki-release.tar.gz
	rm -fr *.log
	mkdir ./res


build_env:
	cd ./package/depend && \
		python ./pip-9.0.1-py2.py3-none-any.whl/pip install pip-9.0.1-py2.py3-none-any.whl
	cd ./package/depend && \
		pip install virtualenv-15.1.0-py2.py3-none-any.whl 
	virtualenv --no-site-packages pyenv
	. ./pyenv/bin/activate && \
		pip install -r requirements.txt 
	cd ./pyenv && \
		virtualenv --relocatable ./


# build_env:
# 	cd ./package/depend && \
# 		python ./pip-9.0.1-py2.py3-none-any.whl/pip install pip-9.0.1-py2.py3-none-any.whl
# 	cd ./package/depend && \
# 		pip install virtualenv-15.1.0-py2.py3-none-any.whl 
# 	virtualenv --no-site-packages pyenv
# 	. ./pyenv/bin/activate && \
# 		pip install -r requirements.txt && \
# 		echo_supervisord_conf | sed -e "s#;\[include\]#\[include\]#g"  > /etc/supervisord.conf && \
# 		echo "files=${PWD}/conf/supervisor.conf" >> /etc/supervisord.conf && \
# 		sed -i "s|directory=.*|directory=${PWD}|g" ./conf/supervisor.conf



install_source:
	mkdir -p /opt/yrinfo 
	cd ./depend && \
		tar zxvf Python-2.7.14.tgz -C /opt/yrinfo
	cd /opt/yrinfo/Python-2.7.14 && \
		./configure --prefix=/opt/yrinfo/python && \
		make install
	echo "export PYTHON_HOME=/opt/yrinfo/python" > ./env.file
	echo "export PATH=$PYTHON_HOME/bin:$PATH" >> ./env.file
	echo "export PATH" >> ./env.file
	tar zxvf ./pyenv.tar.gz 
	
install_source_pyenv:
	mkdir -p /opt/yrinfo 
	tar zxvf ./package/python.tar.gz -C /opt/yrinfo
	echo "export PYTHON_HOME=/opt/yrinfo/python" > ./env.file
	echo "export PATH=$PYTHON_HOME/bin:$PATH" >> ./env.file
	echo "export PATH" >> ./env.file
	tar zxvf ./package/pyenv.tar.gz 

build_zip:
	echo "去掉代理!!!!!"
	zip -r cnki-release.zip *.py ./requirements.txt Makefile README.md

build_zip_env:
	echo "去掉代理!!!!!"
	cd .. && \
		tar zcvf cnki-release.tar.gz  \
		--exclude=cnki/cnki.iml \
		--exclude=cnki/.idea \
		./cnki
	mv ../cnki-release.tar.gz ./
push_test:
	rsync -auvz --progress --delete . root@192.168.4.11:/tmp/cnki
run:
	source ./pyenv/bin/activate && \
		python main1.py
