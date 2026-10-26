/* SPDX-License-Identifier: MIT */
#define _GNU_SOURCE
#include "calc.h"
#include <errno.h>
#include <limits.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
static const char *mode;
static atomic_int entered;
static pthread_mutex_t output = PTHREAD_MUTEX_INITIALIZER;
int ox_trace_sink(const char *s, size_t n) {
    if (!strcmp(mode, "reenter") && atomic_exchange(&entered, 1) == 0) {
        int v = 123;
        errno = 81;
        int rc = calc_div(9, 3, &v), after = errno;
        if (getenv("OX_OPAQUE")) {
            if (rc != -1 || v != 124 || after != 42)
                _exit(91);
        } else if (rc != 0 || v != 3 || after != 81)
            _exit(91);
    }
    errno = EIO;
    if (!strcmp(mode, "fail"))
        return -1;
    pthread_mutex_lock(&output);
    size_t r = fwrite(s, 1, n, stderr);
    fflush(stderr);
    pthread_mutex_unlock(&output);
    return r == n ? 0 : -1;
}
static void one(int i, int worker, int iteration) {
    const int aa[] = {7, -7, 7, INT_MIN, 7, 7}, bb[] = {2, 2, 0, -1, 2, 0};
    int out = 123;
    errno = 71 + i;
    int rc = calc_div(aa[i], bb[i], i >= 4 ? NULL : &out);
    int after = errno;
    printf("{\"case\":%d,\"worker\":%d,\"iteration\":%d,\"rc\":%d,\"out\":%d,\"after\":%d}\n", i,
           worker, iteration, rc, out, after);
}
static void *worker(void *v) {
    for (int i = 0; i < 1000; i++)
        one(i % 6, (int)(long)v, i);
    return NULL;
}
int main(int argc, char **argv) {
    if (argc != 2)
        return 2;
    mode = argv[1];
    for (int i = 0; i < 6; i++)
        one(i, 0, i);
    pthread_t t[4];
    for (long i = 0; i < 4; i++)
        if (pthread_create(&t[i], NULL, worker, (void *)(i + 1)))
            return 1;
    for (int i = 0; i < 4; i++)
        pthread_join(t[i], NULL);
    return 0;
}
