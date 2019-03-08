MANAGE=python backend/manage.py

all: help

help:
	@echo "Usage: "
	@echo "    make build - build the application for production setting"
	@echo "    make deps  - install application dependencies"
	@echo "    make clean - clean built files"

deps:
	pip install -r requirements.txt
	cd frontend && npm install

build:
	$(MAKE) clean
	cd frontend && npm run build
	cd ../
	$(MANAGE) collectstatic --clear --noinput

clean:
	rm -rf public
	rm -rf frontend/dist