/* Test-only candidates. These are not published challenge references. */
#include <stdio.h>
#include <string.h>
#include <signal.h>

static int failed(void) { fputs("I/O or format error\n", stderr); return 1; }

int main(int argc, char **argv) {
#if CHALLENGE == 1
    (void)argc; (void)argv; (void)failed;
    unsigned long lines = 0, words = 0, bytes = 0;
    int inside = 0, c;
    while ((c = getchar()) != EOF) {
        ++bytes;
        if (c == '\n') ++lines;
        int separator = c == ' ' || (c >= '\t' && c <= '\r');
        if (!separator && !inside) ++words;
        inside = !separator;
    }
    printf("%lu %lu %lu\n", lines + MUTATION, words, bytes);
    return 0;
#elif CHALLENGE == 2
    (void)argc; (void)argv;
    if (fputs("P6\n256 256\n255\n", stdout) == EOF) return failed();
    for (int y = 0; y < 256; ++y)
        for (int x = 0; x < 256; ++x)
            if (putchar(x) == EOF || putchar(y) == EOF || putchar(MUTATION) == EOF) return failed();
    return fflush(stdout) == EOF ? failed() : 0;
#else
    if (signal(SIGPIPE, SIG_IGN) == SIG_ERR) return failed();
    if (argc != 2) return failed();
    if (strcmp(argv[1], "encode") == 0) {
        int c, previous = EOF, count = 0;
        while ((c = getchar()) != EOF) {
            if (c == previous && count < 255) { ++count; continue; }
            if (count && (putchar(count) == EOF || putchar(previous) == EOF)) return failed();
            previous = c; count = 1;
        }
        if (MUTATION && count) ++count;
        if (count && (putchar(count) == EOF || putchar(previous) == EOF)) return failed();
    } else if (strcmp(argv[1], "decode") == 0) {
        int count, c;
        while ((count = getchar()) != EOF) {
            c = getchar();
            if (!count || c == EOF) return failed();
            while (count--) if (putchar(c) == EOF) return failed();
        }
    } else return failed();
    if (ferror(stdin) || fflush(stdout) == EOF) return failed();
    return 0;
#endif
}
