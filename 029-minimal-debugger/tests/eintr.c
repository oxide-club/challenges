/* SPDX-License-Identifier: MIT */
#define _GNU_SOURCE
#include <sys/types.h>
#include <sys/wait.h>
#include <dlfcn.h>
#include <errno.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
/* Injeção de falha de syscall, não implementação do debugger. */
pid_t waitpid(pid_t pid, int *status, int options) {
    static int injected;
    static pid_t (*next)(pid_t, int *, int);
    if (!next)
        *(void **)(&next) = dlsym(RTLD_NEXT, "waitpid");
    if (!next)
        _exit(125);
    if (!injected) {
        injected = 1;
        const char *path = getenv("OX_EINTR_WITNESS");
        if (!path)
            _exit(126);
        int fd = open(path, O_WRONLY | O_CREAT | O_EXCL, 0600);
        if (fd < 0)
            _exit(126);
        write(fd, "EINTR\n", 6);
        close(fd);
        errno = EINTR;
        return -1;
    }
    return next(pid, status, options);
}
