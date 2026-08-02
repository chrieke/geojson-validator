SRC := .

test: typecheck
	@echo "Formatting with black ..."
	black .
	@echo "Running tests with pytest"
	python -m pytest --pylint --pylint-rcfile=../pylintrc

typecheck:
	@echo "Type checking with mypy ..."
	python -m mypy

redownload-testfiles:
	@echo "Redownloading test files from https://github.com/chrieke/geojson-invalid-geometry"
	python tests/scripts/redownload_testfiles.py

