/* SPDX-License-Identifier: MIT.
 * Linux x86-64: limita write/writev em stdout a um byte antes da syscall.
 * O kernel executa a escrita; o tracer não fabrica seu retorno nem seus bytes.
 */
#define _GNU_SOURCE
#include <sys/ptrace.h>
#include <sys/types.h>
#include <sys/user.h>
#include <sys/wait.h>
#include <sys/uio.h>
#include <sys/syscall.h>
#include <stdint.h>
#include <stddef.h>
#include <unistd.h>
#include <signal.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>

static volatile sig_atomic_t child_pid = -1;
static int unavailable(int error) { return error == EPERM || error == EACCES || error == ENOSYS; }
static void timeout(int signal_number) {
    (void)signal_number;
    if (child_pid > 0) {
        kill(child_pid, SIGKILL);
        waitpid(child_pid, NULL, 0);
    }
    _exit(124);
}
static int wait_child(int *status) {
    pid_t result;
    do {
        result = waitpid(child_pid, status, 0);
    } while (result < 0 && errno == EINTR);
    return result == child_pid;
}
static int failed(const char *operation, int code) {
    perror(operation);
    kill(child_pid, SIGKILL);
    waitpid(child_pid, NULL, 0);
    return code;
}
int main(int argc, char **argv) {
    if (argc < 2)
        return 2;
    pid_t pid = fork();
    if (pid < 0) {
        perror("fork");
        return 125;
    }
    if (pid == 0) {
        if (ptrace(PTRACE_TRACEME, 0, NULL, NULL) < 0) {
            int error = errno;
            perror("probe PTRACE_TRACEME");
            _exit(unavailable(error) ? 77 : 125);
        }
        execv(argv[1], argv + 1);
        perror("execv");
        _exit(126);
    }
    child_pid = pid;
    struct sigaction action = {0};
    action.sa_handler = timeout;
    sigemptyset(&action.sa_mask);
    if (sigaction(SIGALRM, &action, NULL) < 0)
        return failed("sigaction", 125);
    alarm(5);
    int status;
    if (!wait_child(&status))
        return failed("waitpid inicial", 125);
    if (WIFEXITED(status)) {
        alarm(0);
        child_pid = -1;
        return WEXITSTATUS(status);
    }
    if (WIFSIGNALED(status)) {
        alarm(0);
        child_pid = -1;
        return 128 + WTERMSIG(status);
    }
    if (!WIFSTOPPED(status) || WSTOPSIG(status) != SIGTRAP)
        return failed("parada de exec ausente", 125);
    if (ptrace(PTRACE_SETOPTIONS, pid, NULL, (void *)(PTRACE_O_TRACESYSGOOD | PTRACE_O_EXITKILL)) <
        0)
        return failed("PTRACE_SETOPTIONS", unavailable(errno) ? 77 : 125);
    int entering = 1, deliver = 0;
    unsigned writes = 0, limited = 0;
    unsigned long long original_count = 0;
    int restore_count = 0;
    unsigned long long original_vector = 0;
    uintptr_t length_address = 0;
    unsigned long saved_length = 0;
    int restore_vector = 0;
    for (;;) {
        if (ptrace(PTRACE_SYSCALL, pid, NULL, (void *)(long)deliver) < 0)
            return failed("PTRACE_SYSCALL", 125);
        if (!wait_child(&status))
            return failed("waitpid syscall", 125);
        if (WIFEXITED(status)) {
            alarm(0);
            child_pid = -1;
            fprintf(stderr, "write-limit: stdout_writes=%u limited=%u status=%d\n", writes, limited,
                    WEXITSTATUS(status));
            return WEXITSTATUS(status);
        }
        if (WIFSIGNALED(status)) {
            alarm(0);
            child_pid = -1;
            return 128 + WTERMSIG(status);
        }
        if (!WIFSTOPPED(status))
            return failed("estado inesperado", 125);
        deliver = WSTOPSIG(status);
        if (deliver == (SIGTRAP | 0x80)) {
            struct user_regs_struct regs;
            if (ptrace(PTRACE_GETREGS, pid, NULL, &regs) < 0)
                return failed("PTRACE_GETREGS", 125);
            if (entering && regs.orig_rax == SYS_write && regs.rdi == 1) {
                writes++;
                if (regs.rdx > 1) {
                    original_count = regs.rdx;
                    restore_count = 1;
                    regs.rdx = 1;
                    if (ptrace(PTRACE_SETREGS, pid, NULL, &regs) < 0)
                        return failed("PTRACE_SETREGS", 125);
                    limited++;
                }
            }
            if (entering && regs.orig_rax == SYS_writev && regs.rdi == 1) {
                writes++;
                /* IOV_MAX=1024 no recorte Linux. Contagens inválidas e vetor
                 * vazio seguem para o kernel sem modificação. */
                if (regs.rdx > 0 && regs.rdx <= 1024 &&
                    regs.rsi <= UINTPTR_MAX - regs.rdx * sizeof(struct iovec)) {
                    for (unsigned long long i = 0; i < regs.rdx; i++) {
                        uintptr_t address = (uintptr_t)regs.rsi + i * sizeof(struct iovec) +
                                            offsetof(struct iovec, iov_len);
                        errno = 0;
                        unsigned long length =
                            (unsigned long)ptrace(PTRACE_PEEKDATA, pid, (void *)address, NULL);
                        if (errno)
                            break; /* O kernel conserva o diagnóstico do vetor inválido. */
                        if (!length)
                            continue;
                        if (ptrace(PTRACE_POKEDATA, pid, (void *)address, (void *)1UL) < 0)
                            return failed("limitar iov_len", 125);
                        saved_length = length;
                        length_address = address;
                        restore_vector = 1;
                        original_vector = regs.rsi;
                        original_count = regs.rdx;
                        regs.rsi += i * sizeof(struct iovec);
                        regs.rdx = 1;
                        if (ptrace(PTRACE_SETREGS, pid, NULL, &regs) < 0)
                            return failed("limitar writev", 125);
                        limited++;
                        break;
                    }
                }
            }
            if (!entering && restore_vector) {
                /* Restaure vetor e registradores antes de retomar o filho;
                 * rax continua sendo o retorno real de writev. */
                if (ptrace(PTRACE_POKEDATA, pid, (void *)length_address, (void *)saved_length) < 0)
                    return failed("restaurar iov_len", 125);
                regs.rsi = original_vector;
                regs.rdx = original_count;
                if (ptrace(PTRACE_SETREGS, pid, NULL, &regs) < 0)
                    return failed("restaurar writev", 125);
                restore_vector = 0;
            }
            if (!entering && restore_count) {
                /* write preserva o registrador de entrada. O compilador pode
                 * reutilizá-lo depois de asm!: restaure-o, mantendo rax real. */
                regs.rdx = original_count;
                if (ptrace(PTRACE_SETREGS, pid, NULL, &regs) < 0)
                    return failed("restaurar rdx", 125);
                restore_count = 0;
            }
            entering = !entering;
            deliver = 0;
        }
        /* Entrega sinais reais; somente paradas de syscall são consumidas. */
    }
}
