.PHONY: update validate report test

update:
	python3 scripts/update.py

validate:
	python3 scripts/validate.py

report:
	python3 scripts/report.py

test:
	python3 -m unittest discover -s tests -v

