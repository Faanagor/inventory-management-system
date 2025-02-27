POETRY = poetry
PYTHON = $(POETRY) run python
UVICORN = $(POETRY) run uvicorn
TEST = $(POETRY) run pytest
TEST_DIR = tests/
COV_REPORT_TERM = --cov-report=term-missing
COV_REPORT_HTML = --cov-report=html
APP = inventory_management_system
COV_PACKAGE = --cov=$(APP)
COV_FAILED_PERCENT = 80
COV_FAILED_UNDER = --cov-fail-under=$(COV_FAILED_PERCENT)
BLACK = $(POETRY) run black
ISORT = $(POETRY) run isort
FLAKE8 = $(POETRY) run flake8
MYPY = $(POETRY) run mypy
PRE_COMMIT = $(POETRY) run pre-commit

.PHONY: install
install:
	which $(POETRY) || pip install $(POETRY)
	$(POETRY) install --with dev,test
	$(PRE_COMMIT) install

.PHONY: pre-commit
pre-commit:
	$(PRE_COMMIT) run --all-files

.PHONY: test
test:
	$(TEST)

.PHONY: test-coverage

test-coverage:
	$(TEST) $(COV_PACKAGE) $(COV_REPORT_TERM) $(COV_FAILED_UNDER) $(APP)/$(TEST_DIR)

.PHONY: test-coverage-html
test-coverage-html:
	$(TEST) $(COV_PACKAGE) $(COV_REPORT_HTML) $(TEST_DIR) 

.PHONY: format
format:
	$(BLACK) . && $(ISORT) .

.PHONY: lint
lint:
	$(FLAKE8)

.PHONY: run
run:
	$(UVICORN) $(APP).main:app --reload --host 127.0.0.1 --port 8000

.PHONY: clean
clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -exec rm -rf {} +

.PHONY: all
all: format lint test
