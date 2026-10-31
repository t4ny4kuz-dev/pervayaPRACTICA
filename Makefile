PYTHON ?= python3

.PHONY: run test

run:
	$(PYTHON) src/main.py $(ARGS)

test:
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests -v
