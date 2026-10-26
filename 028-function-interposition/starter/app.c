/* SPDX-License-Identifier: MIT */
#include "calc.h"
#include <stdio.h>
#include <errno.h>
int ox_trace_sink(const char *s, size_t n) { return fwrite(s, 1, n, stderr) == n ? 0 : -1; }
int main(void) {
    int value = 123;
    errno = 71;
    int rc = calc_div(7, 2, &value);
    int after = errno;
    printf("rc=%d value=%d errno=%d\n", rc, value, after);
    /* TODO: cenários, concorrência e comparação automática com baseline. */
    return rc != 0;
}
