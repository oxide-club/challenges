/* SPDX-License-Identifier: MIT */
#define _POSIX_C_SOURCE 200809L
#include <signal.h>
#include <string.h>
#include <unistd.h>
static volatile sig_atomic_t count;
static void handled(int sig) {
    (void)sig;
    ++count;
}
int main(int argc, char **argv) {
    if (argc != 2)
        return 2;
    struct sigaction sa = {0};
    sa.sa_handler = handled;
    sigemptyset(&sa.sa_mask);
    if (!strcmp(argv[1], "usr1")) {
        sigaction(SIGUSR1, &sa, 0);
        raise(SIGUSR1);
        return count == 1 ? 7 : 91;
    }
    if (!strcmp(argv[1], "trap")) {
        sigaction(SIGTRAP, &sa, 0);
        raise(SIGTRAP);
        return count == 1 ? 7 : 92;
    }
    if (!strcmp(argv[1], "term")) {
        raise(SIGTERM);
        return 93;
    }
    if (!strcmp(argv[1], "unknown-trap")) {
        __asm__ volatile("int3");
        return 95;
    }
    if (!strcmp(argv[1], "group")) {
        raise(SIGSTOP);
        return 94;
    }
    if (!strcmp(argv[1], "timeout")) {
        for (;;)
            pause();
    }
    return 2;
}
