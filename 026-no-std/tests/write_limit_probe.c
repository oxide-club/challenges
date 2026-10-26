/* SPDX-License-Identifier: MIT. Sonda independente, sem código do participante. */
#include <stddef.h>
static long raw_write(const char *bytes, size_t *count) {
    long result;
    __asm__ volatile("syscall"
                     : "=a"(result), "+d"(*count)
                     : "0"(1L), "D"(1L), "S"(bytes)
                     : "rcx", "r11", "memory");
    return result;
}
int main(int argc, char **argv) {
    (void)argv;
    const char text[] = "probe-write\n";
    if (argc > 1) {
        size_t count = sizeof(text) - 1;
        long n = raw_write(text, &count);
        /* Não basta reduzir o retorno: rdx é preservado pela syscall. */
        return n == 1 && count == sizeof(text) - 1 ? 0 : 2;
    }
    size_t offset = 0;
    while (offset < sizeof(text) - 1) {
        size_t remaining = sizeof(text) - 1 - offset, count = remaining;
        long n = raw_write(text + offset, &count);
        if (count != remaining)
            return 4;
        if (n == -4)
            continue;
        if (n <= 0)
            return 3;
        offset += (size_t)n;
    }
    return 0;
}
