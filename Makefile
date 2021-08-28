.PHONY: init
init:
	pip install -r requirements.txt
	python -m ash_unofficial_covid19.import_patients
	python -m ash_unofficial_covid19.import_medical_institutions

formatter:
	isort --force-single-line-imports .
	autoflake -ri --remove-all-unused-imports --ignore-init-module-imports --remove-unused-variables .
	black .
	isort --multi-line 3 .
