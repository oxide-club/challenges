/* SPDX-License-Identifier: MIT.
 * Supervisor de teste Linux x86-64. O kernel observa TRACEME e recebe EPERM.
 * Não intercepta libc nem lê ponteiros do candidato. Não é um sandbox hostil.
 */
#define _GNU_SOURCE
#include <linux/audit.h>
#include <linux/filter.h>
#include <linux/seccomp.h>
#include <sys/ioctl.h>
#include <sys/ptrace.h>
#include <sys/prctl.h>
#include <sys/syscall.h>
#include <sys/wait.h>
#include <fcntl.h>
#include <poll.h>
#include <signal.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <errno.h>

static double now(void) {
    struct timespec t;
    if (clock_gettime(CLOCK_MONOTONIC, &t) < 0) {
        perror("clock_gettime");
        exit(125);
    }
    return (double)t.tv_sec + (double)t.tv_nsec / 1e9;
}
static int unavailable(int e) {
    return e == EPERM || e == EACCES || e == ENOSYS || e == EOPNOTSUPP;
}
static void wakeup(int number) { (void)number; }
static int setup_error(const char *operation) {
    int e = errno;
    perror(operation);
    return unavailable(e) ? 77 : 125;
}
/* Estas chamadas usam operações e flags fixas. EINVAL nas consultas indica
 * interface ausente; EBUSY ao instalar indica listener herdado. Não se aplica
 * a prctl, alocação, abertura de arquivo nem ao uso do listener instalado. */
static int seccomp_setup_error(const char *operation, int installing) {
    int e = errno;
    perror(operation);
    return unavailable(e) || (!installing && e == EINVAL) || (installing && e == EBUSY) ? 77 : 125;
}
static int parent_of(unsigned pid) {
    char path[64], line[256];
    int parent = -1;
    snprintf(path, sizeof(path), "/proc/%u/status", pid);
    FILE *f = fopen(path, "r");
    if (!f)
        return -1;
    while (fgets(line, sizeof(line), f))
        if (sscanf(line, "PPid:%d", &parent) == 1)
            break;
    fclose(f);
    return parent;
}
static void cleanup(pid_t candidate, FILE *log) {
    /* Somente o grupo iniciado por este instrumento. O subreaper permite
     * identificar filhos que o candidato deixou pendentes, sem aprová-los. */
    kill(-candidate, SIGKILL);
    double deadline = now() + 1;
    for (;;) {
        int status;
        pid_t pid = waitpid(-1, &status, WNOHANG);
        if (pid > 0) {
            fprintf(log, "{\"type\":\"orphan\",\"pid\":%d}\n", pid);
            continue;
        }
        if (pid < 0 && errno == ECHILD)
            break;
        if (pid < 0 && errno != EINTR)
            break;
        if (now() >= deadline) {
            fprintf(log, "{\"type\":\"cleanup_timeout\"}\n");
            break;
        }
        struct timespec pause = {0, 1000000};
        nanosleep(&pause, NULL);
    }
}
int main(int argc, char **argv) {
    if (argc < 3) {
        fputs("uso: notify_ptrace REGISTRO PROGRAMA [ARG...]\n", stderr);
        return 2;
    }
    uint32_t action = SECCOMP_RET_USER_NOTIF;
    if (syscall(SYS_seccomp, SECCOMP_GET_ACTION_AVAIL, 0, &action) < 0)
        return seccomp_setup_error("SECCOMP_GET_ACTION_AVAIL", 0);
    struct seccomp_notif_sizes sizes;
    if (syscall(SYS_seccomp, SECCOMP_GET_NOTIF_SIZES, 0, &sizes) < 0)
        return seccomp_setup_error("SECCOMP_GET_NOTIF_SIZES", 0);
    if (sizes.seccomp_notif < sizeof(struct seccomp_notif) ||
        sizes.seccomp_notif_resp < sizeof(struct seccomp_notif_resp))
        return 125;
    struct seccomp_notif *request = calloc(1, sizes.seccomp_notif);
    struct seccomp_notif_resp *response = calloc(1, sizes.seccomp_notif_resp);
    if (!request || !response) {
        perror("calloc");
        free(request);
        free(response);
        return 125;
    }
    if (prctl(PR_SET_CHILD_SUBREAPER, 1) < 0)
        return setup_error("PR_SET_CHILD_SUBREAPER");
    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) < 0)
        return setup_error("PR_SET_NO_NEW_PRIVS");
    struct sock_filter filter[] = {
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, offsetof(struct seccomp_data, arch)),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_X86_64, 1, 0),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, offsetof(struct seccomp_data, nr)),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_ptrace, 0, 3),
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, offsetof(struct seccomp_data, args[0])),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, PTRACE_TRACEME, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_USER_NOTIF),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),
    };
    struct sock_fprog program = {.len = sizeof(filter) / sizeof(filter[0]), .filter = filter};
    int listener = (int)syscall(SYS_seccomp, SECCOMP_SET_MODE_FILTER,
                                SECCOMP_FILTER_FLAG_NEW_LISTENER, &program);
    if (listener < 0)
        return seccomp_setup_error("SECCOMP_FILTER_FLAG_NEW_LISTENER", 1);
    int fd = open(argv[1], O_WRONLY | O_CREAT | O_TRUNC | O_CLOEXEC, 0600);
    if (fd < 0) {
        perror("registro do supervisor");
        close(listener);
        return 125;
    }
    FILE *log = fdopen(fd, "w");
    if (!log) {
        perror("fdopen");
        close(fd);
        close(listener);
        return 125;
    }
    pid_t child = fork();
    if (child < 0) {
        perror("fork");
        fclose(log);
        close(listener);
        return 125;
    }
    if (child == 0) {
        close(listener);
        close(fd);
        if (setpgid(0, 0) < 0)
            _exit(125);
        execvp(argv[2], argv + 2);
        perror("exec do candidato");
        _exit(126);
    }
    if (setpgid(child, child) < 0 && errno != EACCES && errno != ESRCH) {
        perror("setpgid");
        kill(child, SIGKILL);
        waitpid(child, NULL, 0);
        fclose(log);
        close(listener);
        return 125;
    }
    fprintf(log, "{\"type\":\"started\",\"candidate_pid\":%d}\n", child);
    fflush(log);
    struct sigaction timer = {0};
    timer.sa_handler = wakeup;
    sigemptyset(&timer.sa_mask);
    if (sigaction(SIGALRM, &timer, NULL) < 0) {
        perror("sigaction");
        cleanup(child, log);
        fclose(log);
        close(listener);
        return 125;
    }
    alarm(7); /* Interrompe também RECV se a notificação for cancelada após poll. */
    int result = 125, status = 0;
    double deadline = now() + 7;
    for (;;) {
        pid_t got = waitpid(child, &status, WNOHANG);
        if (got == child) {
            result = WIFEXITED(status) ? WEXITSTATUS(status) : 128 + WTERMSIG(status);
            break;
        }
        if (got < 0 && errno != EINTR) {
            perror("waitpid candidato");
            break;
        }
        if (now() >= deadline) {
            fputs("prazo do supervisor esgotado\n", stderr);
            result = 124;
            break;
        }
        struct pollfd event = {.fd = listener, .events = POLLIN};
        int ready = poll(&event, 1, 20);
        if (ready < 0) {
            if (errno == EINTR)
                continue;
            perror("poll listener");
            break;
        }
        if (!ready || !(event.revents & POLLIN))
            continue;
        memset(request, 0, sizes.seccomp_notif);
        if (ioctl(listener, SECCOMP_IOCTL_NOTIF_RECV, request) < 0) {
            if (errno == EINTR || errno == ENOENT)
                continue;
            perror("SECCOMP_IOCTL_NOTIF_RECV");
            break;
        }
        if (request->data.arch != AUDIT_ARCH_X86_64 || request->data.nr != SYS_ptrace ||
            request->data.args[0] != PTRACE_TRACEME || !request->pid) {
            fputs("notificação inesperada\n", stderr);
            break;
        }
        int ppid = parent_of(request->pid);
        if (ppid < 0) {
            perror("identidade do solicitante");
            break;
        }
        memset(response, 0, sizes.seccomp_notif_resp);
        response->id = request->id;
        response->error = -EPERM;
        if (ioctl(listener, SECCOMP_IOCTL_NOTIF_SEND, response) < 0) {
            if (errno == ENOENT) {
                fputs("{\"type\":\"cancelled\"}\n", log);
                continue;
            }
            perror("SECCOMP_IOCTL_NOTIF_SEND");
            break;
        }
        fprintf(
            log,
            "{\"type\":\"denied\",\"pid\":%u,\"ppid\":%d,\"request\":0,\"result\":-1,\"errno\":%d}\n",
            request->pid, ppid, EPERM);
        if (fflush(log)) {
            perror("gravar testemunho");
            break;
        }
    }
    cleanup(child, log);
    alarm(0);
    fclose(log);
    close(listener);
    free(request);
    free(response);
    return result;
}
