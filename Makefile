.PHONY: init
init:
	pip install -r requirements.txt
	python import_data.py

formatter:
	isort --force-single-line-imports .
	autoflake -ri --remove-all-unused-imports --ignore-init-module-imports --remove-unused-variables .
	black .
	isort --multi-line 3 .
