PYTHON ?= python3
CARGO ?= cargo
CARGO_MANIFEST := tools/oxide-test/Cargo.toml

.PHONY: check check-python check-rust check-packages build
check: check-python check-rust check-packages

check-packages:
	$(PYTHON) tools/check_packages.py

check-python:
	$(PYTHON) tools/check_catalog.py
	$(PYTHON) tools/verification_policy.py
	$(PYTHON) 001-wc/materials/generate.py --check
	$(PYTHON) 002-ppm/materials/generate.py --check
	$(PYTHON) 003-rle/materials/generate.py --check
	$(PYTHON) -m unittest discover -s tools/tests -v

check-rust:
	$(CARGO) fmt --manifest-path $(CARGO_MANIFEST) --all -- --check
	$(CARGO) clippy --manifest-path $(CARGO_MANIFEST) --locked --all-targets -- -D warnings
	$(CARGO) test --manifest-path $(CARGO_MANIFEST) --locked

build:
	$(CARGO) build --manifest-path $(CARGO_MANIFEST) --release --locked
