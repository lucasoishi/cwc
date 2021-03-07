PROJECT_NAME=cwc
LINES=79

clean:  ## Clean python bytecodes, optimized files, logs, cache, coverage...
	@find . -name "*.pyc" | xargs rm -rf
	@find . -name "*.pyo" | xargs rm -rf
	@find . -name "__pycache__" -type d | xargs rm -rf
	@find . -name ".pytest_cache" -type d | xargs rm -rf
	@rm -f .coverage
	@rm -rf htmlcov/
	@rm -f coverage.xml
	@rm -f *.log
	@find . -name "celerybeat-schedule*" | xargs rm -rf

env: ## Create .env file
	@cp -n localenv .env

style: clean
	@black -S -t py39 -C -l ${LINES} .
	@isort .

style-check:
	@black --check -C -S -t -l ${LINES} py39 .

type-check:
	@mypy .

pylint-check:
	@cd ${PROJECT_NAME}/ pylint ./

flake8-check:
	@flake8 ${PROJECT_NAME}/

mypy-check:
	@cd ${PROJECT_NAME} && mypy .

shell: clean
	@cd ${PROJECT_NAME} && ipython

test: clean
	@cd ${PROJECT_NAME} && python -m pytest . -s -v

