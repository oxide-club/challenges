CC ?= cc
CFLAGS = -std=c11 -O0 -g -fno-lto -Wall -Wextra -I materials
all: build/libcalc.so build/libtrace.so build/app build/direct
build:
	mkdir -p $@
build/libcalc.so: starter/calc.c materials/calc.h | build
	$(CC) $(CFLAGS) -fPIC -shared $< -o $@
build/libtrace.so: starter/trace.c materials/calc.h | build
	$(CC) $(CFLAGS) -fPIC -shared $< -pthread -ldl -o $@
build/app: starter/app.c build/libcalc.so
	$(CC) $(CFLAGS) -rdynamic $< -Lbuild -Wl,-rpath,'$$ORIGIN' -lcalc -pthread -o $@
build/direct: starter/app.c starter/calc.c | build
	$(CC) $(CFLAGS) -rdynamic starter/app.c starter/calc.c -pthread -o $@
check: all
	python3 tests/test.py build
