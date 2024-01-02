SRC := .

test:
	@echo "Formatting with black ..."
	black .
	@echo "Running tests with pytest"
	python -m pytest --pylint --pylint-rcfile=../pylintrc

redownload-testfiles:
	@echo "Redownloading test files from https://github.com/chrieke/geojson-invalid-geometry"
	python tests/scripts/redownload_testfiles.py

