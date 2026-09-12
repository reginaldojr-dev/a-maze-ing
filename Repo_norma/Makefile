PYTHON = python3
PIP = pip
MAIN = a_maze_ing.py
CONFIG = config.txt

.PHONY: all install run debug clean lint lint-strict build-pkg

all: run

install:
	$(PIP) install --upgrade pip
	$(PIP) install flake8 mypy build pytest
	@if [ -f pyproject.toml ]; then $(PIP) install -e .; fi

run:
	$(PYTHON) $(MAIN) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

clean:
	rm -rf __pycache__ */__pycache__ */*/__pycache__
	rm -rf .mypy_cache */.mypy_cache .pytest_cache
	rm -rf build dist *.egg-info
	rm -f maze_output.hex

lint:
	flake8 .
	mypy --warn-unused-ignores --ignore-missing-imports --warn-return-any --disallow-untyped-defs --check-untyped-defs a_maze_ing.py mazegen renderers

lint-strict:
	flake8 .
	mypy --strict a_maze_ing.py mazegen renderers

build-pkg:
	$(PYTHON) -m venv .venv_build
	.venv_build/bin/pip install build
	.venv_build/bin/python -m build --wheel
	cp dist/*.whl .
	rm -rf .venv_build