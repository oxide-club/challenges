/* SPDX-License-Identifier: MIT. Nega acct com EPERM; mantém ptrace permitido.
 * Controle positivo: a presença de seccomp, sozinha, não é indisponibilidade. */
#define _GNU_SOURCE
#include <linux/filter.h>
#include <linux/seccomp.h>
#include <linux/audit.h>
#include <sys/prctl.h>
#include <sys/syscall.h>
#include <stddef.h>
#include <errno.h>
#include <unistd.h>
#include <stdio.h>
int main(int c, char **v) {
    (void)c;
    struct sock_filter f[] = {BPF_STMT(BPF_LD | BPF_W | BPF_ABS, offsetof(struct seccomp_data, nr)),
                              BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_acct, 0, 1),
                              BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | EPERM),
                              BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW)};
    struct sock_fprog p = {4, f};
    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) || prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, &p)) {
        perror("seccomp");
        return 1;
    }
    execv(v[1], v + 1);
    perror("execv");
    return 1;
}
