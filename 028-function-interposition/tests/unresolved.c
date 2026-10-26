/* SPDX-License-Identifier: MIT */
#include <dlfcn.h>
#include <stddef.h>
int ox_trace_sink(const char *s, size_t n) {
    (void)s;
    (void)n;
    return 0;
}
int main(int argc, char **argv) {
    if (argc != 2)
        return 2;
    void *h = dlopen(argv[1], RTLD_NOW | RTLD_GLOBAL);
    if (!h)
        return 3;
    int (*f)(int, int, int *);
    *(void **)(&f) = dlsym(h, "calc_div");
    if (!f)
        return 4;
    int out = 0;
    return f(7, 2, &out);
}
