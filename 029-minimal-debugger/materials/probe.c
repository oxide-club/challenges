/* SPDX-License-Identifier: MIT */
#define _GNU_SOURCE
#include <sys/ptrace.h>
#include <sys/wait.h>
#include <unistd.h>
#include <signal.h>
#include <stdio.h>
#include <errno.h>
#include <string.h>
int main(void) {
    pid_t p = fork();
    if (p < 0) {
        perror("fork");
        return 1;
    }
    if (!p) {
        if (ptrace(PTRACE_TRACEME, 0, 0, 0) < 0) {
            int e = errno;
            fprintf(stderr, "PTRACE_TRACEME errno=%d: %s\n", e, strerror(e));
            _exit(e == EPERM || e == EACCES ? 77 : 1);
        }
        raise(SIGSTOP);
        _exit(0);
    }
    int s;
    if (waitpid(p, &s, 0) < 0)
        return 1;
    if (WIFEXITED(s) && WEXITSTATUS(s) == 77)
        return 77;
    if (!WIFSTOPPED(s)) {
        fprintf(stderr, "probe: filho não parou; status=%d\n", s);
        return 1;
    }
    if (ptrace(PTRACE_SETOPTIONS, p, 0, PTRACE_O_TRACEEXEC | PTRACE_O_EXITKILL) < 0) {
        perror("PTRACE_SETOPTIONS");
        kill(p, SIGKILL);
        waitpid(p, &s, 0);
        return 1;
    }
    if (ptrace(PTRACE_CONT, p, 0, 0) < 0) {
        kill(p, SIGKILL);
        waitpid(p, &s, 0);
        return 1;
    }
    if (waitpid(p, &s, 0) < 0 || !WIFEXITED(s) || WEXITSTATUS(s) != 0)
        return 1;
    puts("PASS TRACEME, STOP, TRACEEXEC|EXITKILL, CONT e waitpid");
    return 0;
}
