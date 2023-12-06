SRC := .

test:
	black .
	python -m pytest --pylint --pylint-rcfile=../pylintrc

