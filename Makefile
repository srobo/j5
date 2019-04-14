.PHONY: all lint type test test-cov

CMD:=poetry run
PYMODULE:=j5

all: lint type test

lint:
	$(CMD) flake8 $(PYMODULE) tests tests_hw

type:
	$(CMD) mypy $(PYMODULE) tests

test:
	$(CMD) pytest --cov=$(PYMODULE) tests

test-cov:
	$(CMD) pytest --cov=$(PYMODULE) tests --cov-report html
