cp:
	scp -r ../cnki root@192.168.4.10:/tmp
cp_release:
	scp -r ./cnki-release.tar.gz root@192.168.4.10:/tmp


clean:
	rm -fr ./res 
	rm -fr ./res.txt
	rm -fr *.pyc
	rm -fr *.zip
	rm -fr cnki-release.tar.gz
	rm -fr *.log

build_env:
	cd ./depend && \
		python ./pip-9.0.1-py2.py3-none-any.whl/pip install pip-9.0.1-py2.py3-none-any.whl
	cd ./depend && \
		pip install virtualenv-15.1.0-py2.py3-none-any.whl 
	virtualenv --no-site-packages pyenv
	pip instal

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

run:
	source ./pyenv/bin/activate && \
		python main.py
