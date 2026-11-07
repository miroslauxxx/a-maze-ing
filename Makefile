SHELL := /bin/bash
VENV := .venv
PYTHON := $(shell if [ -f $(VENV)/bin/python3 ]; then echo $(VENV)/bin/python3; else echo python3; fi)
FLAKE8 := $(shell if [ -f $(VENV)/bin/flake8 ]; then echo $(VENV)/bin/flake8; else echo flake8; fi)
MYPY := $(shell if [ -f $(VENV)/bin/mypy ]; then echo $(VENV)/bin/mypy; else echo mypy; fi)
PYTEST := $(shell if [ -f $(VENV)/bin/pytest ]; then echo $(VENV)/bin/pytest; else echo pytest; fi)

CONFIG := config.txt

.PHONY: all install run debug clean lint lint-strict build test help

all: run

help:
	@echo "A-Maze-ing Makefile Commands:"
	@echo "  make install     - Setup virtualenv and install package & dependencies"
	@echo "  make run         - Run the interactive Terminal UI maze program"
	@echo "  make lint        - Run flake8 and mypy with strict flags"
	@echo "  make lint-strict - Run full strict linting over all project files"
	@echo "  make build       - Build the reusable mazegen wheel & source distribution"
	@echo "  make clean       - Remove caches, build artifacts, and output files"
	@echo "  make test        - Run automated pytest suite"

install:
	@if [ ! -d "$(VENV)" ]; then \
		echo "Creating virtual environment in $(VENV)..."; \
		python3 -m venv $(VENV); \
	fi
	@echo "Installing package and development dependencies..."
	@$(VENV)/bin/pip install --upgrade pip setuptools wheel build flake8 mypy pytest
	@$(VENV)/bin/pip install -e .
	@echo "Installation complete."

run:
	@$(PYTHON) a_maze_ing.py $(CONFIG)

lint:
	@echo " Running flake8..."
	@$(FLAKE8) .
	@echo " Running mypy with subject flags..."
	@$(MYPY) . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	@echo " Running strict flake8..."
	@$(FLAKE8) .
	@echo " Running strict mypy over repository..."
	@$(MYPY) --strict .
	@echo "All strict lint checks passed successfully!"

build:
	@echo "Building reusable mazegen distribution package..."
	@$(PYTHON) -m build --no-isolation
	@cp dist/mazegen-*.whl .
	@echo "Build complete. Package available at root and in dist/."

test:
	@echo "Running test suite..."
	@PYTHONPATH=. $(PYTEST) tests/

clean:
	@echo "Cleaning up build, cache, and artifact files..."
	@rm -rf build dist *.egg-info .mypy_cache .pytest_cache
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.py[cod]" -delete 2>/dev/null || true
	@rm -f maze.txt
	@echo "Clean complete."
