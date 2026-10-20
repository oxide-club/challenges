PYTHON ?= python3
CARGO ?= cargo

.PHONY: check check-python check-rust build
check: check-python check-rust

check-python:
	$(PYTHON) tools/check_catalog.py
	$(PYTHON) -m unittest discover -s tests -v

check-rust:
	$(CARGO) fmt --all -- --check
	$(CARGO) clippy --locked --all-targets -- -D warnings
	$(CARGO) test --locked

build:
	$(CARGO) build --release --locked
