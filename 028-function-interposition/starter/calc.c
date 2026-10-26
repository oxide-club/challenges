/* SPDX-License-Identifier: MIT */
#include "calc.h"
#include <errno.h>
int calc_div(int a, int b, int *out) {
    (void)a;
    (void)b;
    (void)out;
    /* TODO: precedência, overflow, divisão e preservação de errno. */
    errno = ENOSYS;
    return -1;
}
