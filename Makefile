SRC := .

test: typecheck
	@echo "Formatting with black ..."
	black .
	@echo "Linting with pylint ..."
	python -m pylint --rcfile=pylintrc geojson_validator tests
	@echo "Running tests with pytest"
	python -m pytest

typecheck:
	@echo "Type checking with mypy ..."
	python -m mypy

redownload-testfiles:
	@echo "Redownloading test files from https://github.com/chrieke/geojson-invalid-geometry"
	python tests/scripts/redownload_testfiles.py

