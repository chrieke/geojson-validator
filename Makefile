.PHONY: check redownload-testfiles

# Same checks as CI, but black reformats instead of only reporting.
check:
	uv run black .
	uv run pylint --rcfile=pylintrc geojson_validator tests
	uv run mypy
	uv run pytest -m "not network"

redownload-testfiles:
	@echo "Redownloading test files from https://github.com/chrieke/geojson-invalid-geometry"
	uv run python tests/scripts/redownload_testfiles.py
