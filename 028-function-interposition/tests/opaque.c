/* SPDX-License-Identifier: MIT */
#include <stdatomic.h>
#include <errno.h>
#include <unistd.h>
#include <stdlib.h>
static atomic_int calls;
/* Substituto opaco da função: não implementa divisão e não é solução. */
int calc_div(int a, int b, int *out) {
    (void)a;
    (void)b;
    atomic_fetch_add(&calls, 1);
    if (out)
        *out += 1;
    errno = 42;
    return -1;
}
__attribute__((destructor)) static void audit(void) {
    if (atomic_load(&calls) != (getenv("OX_EXPECT_CALLS") ? atoi(getenv("OX_EXPECT_CALLS")) : 4006))
        _exit(99);
}
