.PHONY: all clean lint type test test-cov

CMD:=poetry run
PYMODULE:=j5

all: type test lint

lint:
	$(CMD) flake8 $(PYMODULE) tests tests_hw

type:
	$(CMD) mypy $(PYMODULE) tests tests_hw

test:
	$(CMD) pytest --cov=$(PYMODULE) tests

test-cov:
	$(CMD) pytest --cov=$(PYMODULE) tests --cov-report html

clean:
	git clean -Xdf # Delete all files in .gitignore
