.PHONY: all clean lint type test test-cov

CMD:=poetry run
PYMODULE:=j5
TESTS:=tests
SNIPPETS:=build/doc-snippets
EXTRACODE:=docs/_code tests_hw tools/*.py 
GENERATEDCODE:=$(SNIPPETS)/**/*.py

all: type test lint

lint: extract_snippets
	$(CMD) ruff $(PYMODULE) $(GENERATEDCODE) $(TESTS) $(EXTRACODE)

lint-fix: extract_snippets
	$(CMD) ruff --fix $(PYMODULE) $(GENERATEDCODE) $(TESTS) $(EXTRACODE)

type: extract_snippets
	$(CMD) mypy $(PYMODULE) $(GENERATEDCODE) $(TESTS) $(EXTRACODE)

test:
	$(CMD) pytest --cov=$(PYMODULE) $(TESTS)

test-cov:
	$(CMD) pytest --cov=$(PYMODULE) $(TESTS) --cov-report html

test-ci:
	$(CMD) pytest --cov=$(PYMODULE) $(TESTS) --cov-report xml

isort:
	$(CMD) isort $(PYMODULE) $(TESTS) $(EXTRACODE)

extract_snippets:
	rm -rf $(SNIPPETS)
	mkdir -p $(SNIPPETS)/README.md
	python3 tools/extract_snippets.py README.md $(SNIPPETS)/README.md

clean:
	git clean -Xdf # Delete all files in .gitignore
