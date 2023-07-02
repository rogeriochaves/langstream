.PHONY: test doctest docs install

test:
	PYTHONPATH=$PYTHONPATH:. pytest -s -m "not integration" $(filter-out $@,$(MAKECMDGOALS))

doctest:
	python -m doctest -v litechain/utils/chain.py && python -m doctest -v litechain/**/*.py

test-integration:
	PYTHONPATH=$PYTHONPATH:. pytest -s -m integration $(filter-out $@,$(MAKECMDGOALS))

docs:
	pdoc --html -o ./docs/static/pdoc --template-dir ./docs/pdoc_template litechain --force

install:
	pip install -r requirements.txt

%:
	@: