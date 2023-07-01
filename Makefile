.PHONY: test doctest docs install

test:
	python -m unittest tests/**/*.py

doctest:
	python -m doctest -v litechain/utils/chain.py && python -m doctest -v litechain/**/*.py

docs:
	pdoc --html -o ./docs/static/pdoc --template-dir ./docs/pdoc_template litechain --force

install:
	pip install -r requirements.txt