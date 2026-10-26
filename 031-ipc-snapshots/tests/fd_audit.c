/* SPDX-License-Identifier: MIT */
#define _GNU_SOURCE
#include <unistd.h>
#include <stdio.h>
#include <string.h>
/* Test-only destructor: detect transferred descriptors still owned at return. */
__attribute__((destructor)) static void audit(void) {
    for (int fd = 3; fd < 4096; fd++) {
        char path[64], name[256];
        snprintf(path, sizeof path, "/proc/self/fd/%d", fd);
        ssize_t n = readlink(path, name, sizeof name - 1);
        if (n < 0)
            continue;
        name[n] = 0;
        if (strstr(name, "memfd:malformed-fixture")) {
            fputs("FAIL descritor recebido não fechado\n", stderr);
            _exit(98);
        }
    }
}
