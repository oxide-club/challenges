PYTHON ?= python3

.PHONY: check
check:
	$(PYTHON) tools/check_catalog.py
	$(PYTHON) -m unittest discover -s tests -v
