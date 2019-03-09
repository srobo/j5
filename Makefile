.PHONY: all lint type test test-cov

CMD:=poetry run

all: lint type test

lint:
	$(CMD) flake8 j5 tests

type:
	$(CMD) mypy j5

test:
	$(CMD) pytest --cov=j5 tests

test-cov:
	$(CMD) pytest --cov=j5 tests --cov-report html
