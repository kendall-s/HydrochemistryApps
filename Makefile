VENV_NAME?=venv
VENV_ACTIVATE=. $(VENV_NAME)/bin/activate
PYTHON=${VENV_NAME}/bin/python3


init-python: 
	sudo apt-get -y install python3.7 python3-pip
    python3 -m pip install virtualenv
    make venv

venv: 
	$(VENV_NAME)/bin/activate
	pip install -r requirements.txt

build:
	pyinstaller main.spec
	
run: venv
    ${PYTHON} main.py


