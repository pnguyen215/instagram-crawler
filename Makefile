run:
	python3 main.py
install:
	pip3 install -r requirements.txt
package:
	pip3 freeze > draft-requirements.txt
upgrade:
	pip3 install --upgrade -r requirements.txt
docker-build:
	docker-compose build
docker-up:
	docker-compose up
local:
	python3 main.py ./config/logger.local.yaml ./config/application.local.yaml $(username)
prod:
	python3 main.py ./config/logger.yaml ./config/application.yaml $(username)
try:
	./try.sh