.PHONY: init
init:
	pip install -r requirements.txt
	python -m ash_unofficial_covid19.import_patients
	python -m ash_unofficial_covid19.import_medical_institutions

formatter:
	isort --profile black .
	autoflake -ri --remove-all-unused-imports --ignore-init-module-imports --remove-unused-variables .
	black .
