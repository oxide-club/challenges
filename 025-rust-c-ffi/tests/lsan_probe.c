/* SPDX-License-Identifier: MIT. Controles independentes da instrumentação. */
#include <stdlib.h>
extern void club_payload_probe(void);
__attribute__((noinline)) static void context_leak(void) {
    volatile unsigned char *p = malloc(37);
    if (!p)
        abort();
    p[0] = 1;
}
int main(int argc, char **argv) {
    (void)argv;
    club_payload_probe();
    if (argc > 1)
        context_leak();
    return 0;
}
