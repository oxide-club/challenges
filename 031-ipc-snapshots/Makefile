CC ?= cc
CFLAGS = -std=c11 -O0 -g -Wall -Wextra -I materials -pthread
all: build/target build/observer build/region-probe
build:
	mkdir -p $@
build/target: starter/target.c materials/region.h | build
	$(CC) $(CFLAGS) $< -o $@
build/observer: starter/observer.c materials/region.h | build
	$(CC) $(CFLAGS) $< -o $@
build/region-probe: materials/region_probe.c materials/region.h | build
	$(CC) $(CFLAGS) $< -o $@
check: all
	python3 tests/check.py build/target
