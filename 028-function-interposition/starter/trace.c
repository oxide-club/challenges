/* SPDX-License-Identifier: MIT */
#include "calc.h"
#include <errno.h>
int calc_div(int a, int b, int *out) {
    (void)a;
    (void)b;
    (void)out;
    /* TODO: resolver RTLD_NEXT, delegar uma vez, preservar errno e emitir JSON. */
    errno = ENOSYS;
    return -1;
}
