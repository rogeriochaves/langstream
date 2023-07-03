.PHONY: test doctest test-integration docs install

test:
	PYTHONPATH=$PYTHONPATH:. pytest -s -m "not integration" $(filter-out $@,$(MAKECMDGOALS))

doctest:
	PYTHONPATH=$PYTHONPATH:. pytest --doctest-modules litechain/utils && PYTHONPATH=$PYTHONPATH:. pytest --doctest-modules litechain/core && PYTHONPATH=$PYTHONPATH:. pytest --doctest-modules litechain/contrib/llms

test-integration:
	PYTHONPATH=$PYTHONPATH:. pytest -s -m integration $(filter-out $@,$(MAKECMDGOALS))

docs:
	pdoc --html -o ./docs/static/pdoc --template-dir ./docs/pdoc_template litechain --force && cd docs && npm run build

install:
	pip install -r requirements.txt

%:
	@: