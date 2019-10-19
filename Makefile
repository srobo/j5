.PHONY: all clean lint type test test-cov

CMD:=poetry run
PYMODULE:=j5
TESTS:=tests
SNIPPETS:=build/doc-snippets
EXTRACODE:=tests_hw tools/extract_snippets.py
GENERATEDCODE:=$(SNIPPETS)/**/*.py

all: type test lint

lint: extract_snippets
	$(CMD) flake8 $(PYMODULE) $(TESTS) $(EXTRACODE) $(GENERATEDCODE)

type: extract_snippets
	$(CMD) mypy $(PYMODULE) $(TESTS) $(EXTRACODE) $(GENERATEDCODE)

test:
	$(CMD) pytest --cov=$(PYMODULE) $(TESTS)

test-cov:
	$(CMD) pytest --cov=$(PYMODULE) $(TESTS) --cov-report html

test-ci:
	$(CMD) pytest --cov=$(PYMODULE) $(TESTS) --cov-report xml

isort:
	$(CMD) isort --recursive $(PYMODULE) $(TESTS) $(EXTRACODE)

extract_snippets:
	rm -rf $(SNIPPETS)
	mkdir -p $(SNIPPETS)/README.md
	python tools/extract_snippets.py README.md $(SNIPPETS)/README.md

clean:
	git clean -Xdf # Delete all files in .gitignore
