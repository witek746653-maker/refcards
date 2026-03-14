# Makefile
up:
	./venv/bin/python3 backend/server.py

deploy:
	bash scripts/deploy.sh root@155.212.185.27

