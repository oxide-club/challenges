CC ?= cc
CFLAGS = -std=c11 -O0 -g -Wall -Wextra
all: build/notify-ptrace build/step-trap build/arith-exec build/arith-pie build/signals build/probe build/oxdbg
build:
	mkdir -p $@
build/arith-exec: materials/arithmetic.S | build
	$(CC) -nostdlib -static -no-pie $< -o $@
build/arith-pie: materials/arithmetic.S | build
	$(CC) -nostdlib -static-pie $< -o $@
build/signals: materials/signals.c | build
	$(CC) $(CFLAGS) $< -o $@
build/probe: materials/probe.c | build
	$(CC) $(CFLAGS) $< -o $@
build/oxdbg: starter/oxdbg.c | build
	$(CC) $(CFLAGS) $< -o $@
check: all
	python3 tests/check.py build/oxdbg

build/step-trap: materials/step-trap.S | build
	$(CC) -nostdlib -static -no-pie $< -o $@

build/notify-ptrace: tests/notify_ptrace.c | build
	$(CC) $(CFLAGS) -Werror $< -o $@
