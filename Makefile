.PHONY: install-build install-dev format test check clean prcheck bump

install-build:
	python -m pip install -r requirements-build.txt

install-dev:
	python -m pip install -r requirements-test.txt
	python -m pip install -r requirements-docs.txt
	python -m pip install -e .

format:
	python -m black src/ test/

test:
	pytest test/

check:
	black --check src/ test/
	mypy --show-error-codes src/

prcheck: check test

dist: install-build
	python setup.py sdist
	python setup.py bdist_wheel

clean:
	rm -rf dist

bump:
	bumpver update --no-fetch --patch --no-push --commit --tag-commit

bump-dry:
	bumpver update --no-fetch --patch --no-push --commit --tag-commit --dry
