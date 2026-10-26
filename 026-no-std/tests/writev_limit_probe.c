/* SPDX-License-Identifier: MIT. Sonda independente de writev Linux x86-64. */
#include <stddef.h>
#include <string.h>
#include <sys/uio.h>
static long call(const struct iovec *vec, size_t count) {
    const struct iovec *saved_vec = vec;
    size_t saved_count = count;
    long result;
    __asm__ volatile("syscall"
                     : "=a"(result), "+d"(count), "+S"(vec)
                     : "0"(20L), "D"(1L)
                     : "rcx", "r11", "memory");
    return vec == saved_vec && count == saved_count ? result : -999;
}
int main(int argc, char **argv) {
    const char text[] = "probe-writev\n";
    if (argc > 1 && !strcmp(argv[1], "edges")) {
        const struct iovec empty[2] = {{NULL, 0}, {NULL, 0}};
        struct iovec fault = {(void *)1, 3};
        return call(empty, 0) == 0 && call(empty, 2) == 0 && call(&fault, 1) == -14 &&
                       call(empty, 1025) == -22
                   ? 0
                   : 5;
    }
    size_t offset = 0;
    do {
        size_t remaining = sizeof(text) - 1 - offset;
        struct iovec vec[4] = {{NULL, 0},
                               {(void *)(text + offset), remaining > 2 ? 2 : remaining},
                               {NULL, 0},
                               {(void *)(text + offset + (remaining > 2 ? 2 : remaining)),
                                remaining > 2 ? remaining - 2 : 0}};
        struct iovec saved[4];
        memcpy(saved, vec, sizeof(vec));
        long n = call(vec, 4);
        if (memcmp(saved, vec, sizeof(vec)))
            return 4;
        if (n == -4)
            continue;
        if (n != 1)
            return 3;
        offset += (size_t)n;
        if (argc > 1)
            return 0;
    } while (offset < sizeof(text) - 1);
    return 0;
}
