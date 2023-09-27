.PHONY: test doctest test-integration docs install

test:
	PYTHONPATH=$$PYTHONPATH:. poetry run pytest -s -m "not integration" $(filter-out $@,$(MAKECMDGOALS))

test-integration:
	PYTHONPATH=$$PYTHONPATH:. poetry run pytest -s -m integration $(filter-out $@,$(MAKECMDGOALS))

doctest:
	PYTHONPATH=$$PYTHONPATH:. poetry run pytest --doctest-modules langstream/utils && PYTHONPATH=$PYTHONPATH:. poetry run pytest --doctest-modules langstream/core && PYTHONPATH=$PYTHONPATH:. poetry run pytest --doctest-modules langstream/contrib/llms

nbtest:
	poetry run nbdoc_test --fname docs/docs/

docs:
	make pdocs && make nbdocs && cd docs && npm run build

pdocs:
	poetry run pdoc --html -o ./docs/static/reference --template-dir ./docs/pdoc_template langstream --force

nbdocs:
	poetry run nbdoc_build --srcdir docs/docs

docs-dev-server:
	cd docs && npm start

install:
	@if ! command -v poetry &> /dev/null; then \
		curl -sSL https://install.python-poetry.org | python3 -; \
	fi
	poetry install --all-extras

%:
	@: