/* SPDX-License-Identifier: MIT */
#define _GNU_SOURCE
#include <sys/ptrace.h>
#include <sys/types.h>
#include <unistd.h>
#include <stdarg.h>
#include <dlfcn.h>
#include <errno.h>
#include <stdlib.h>
#include <stdio.h>
#include <fcntl.h>
/* Adaptador de observação: delega à libc e registra resultado real no filho. */
long ptrace(enum __ptrace_request request, ...) {
    static long (*next)(enum __ptrace_request, ...);
    if (!next)
        *(void **)(&next) = dlsym(RTLD_NEXT, "ptrace");
    if (!next)
        _exit(125);
    va_list ap;
    va_start(ap, request);
    pid_t pid = va_arg(ap, pid_t);
    void *addr = va_arg(ap, void *), *data = va_arg(ap, void *);
    va_end(ap);
    long result = next(request, pid, addr, data);
    int saved = errno;
    if (request == PTRACE_TRACEME) {
        const char *path = getenv("OX_PTRACE_WITNESS");
        if (!path)
            _exit(126);
        int fd = open(path, O_WRONLY | O_CREAT | O_APPEND | O_CLOEXEC, 0600);
        if (fd < 0)
            _exit(126);
        char line[160];
        int n = snprintf(line, sizeof line, "%d %d %ld %d\n", getpid(), getppid(), result, saved);
        if (write(fd, line, (size_t)n) != n)
            _exit(126);
        close(fd);
    }
    errno = saved;
    return result;
}
