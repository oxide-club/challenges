/* SPDX-License-Identifier: MIT */
#define _GNU_SOURCE
#include "region.h"
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <stddef.h>
int main(int argc, char **argv) {
    if (argc == 1) {
        printf("{\"size\":%zu,\"mutex_offset\":%zu,\"mutex_size\":%zu}\n", sizeof(struct ox_region),
               offsetof(struct ox_region, mutex), sizeof(pthread_mutex_t));
        return 0;
    }
    if (argc != 3)
        return 2;
    int fd = atoi(argv[1]);
    struct stat st;
    if (fstat(fd, &st) || st.st_size != sizeof(struct ox_region))
        return 1;
    struct ox_region *r = mmap(0, sizeof *r, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    if (r == MAP_FAILED)
        return 1;
    if (!strcmp(argv[2], "initialize-v1") || !strcmp(argv[2], "initialize-v2")) {
        pthread_mutexattr_t attr;
        if (pthread_mutexattr_init(&attr))
            return 1;
        int e = pthread_mutexattr_setpshared(&attr, PTHREAD_PROCESS_SHARED);
        if (!e)
            e = pthread_mutexattr_setrobust(&attr, PTHREAD_MUTEX_ROBUST);
        if (!e)
            e = pthread_mutex_init(&r->mutex, &attr);
        pthread_mutexattr_destroy(&attr);
        if (e)
            return 1;
        if (pthread_mutex_lock(&r->mutex))
            return 1;
        r->version = !strcmp(argv[2], "initialize-v2") ? 2 : 1;
        r->generation = 0;
        r->counter = 0;
        r->counter_xor = UINT64_MAX;
        pthread_mutex_unlock(&r->mutex);
        munmap(r, sizeof *r);
        close(fd);
        return 0;
    }
    struct timespec end;
    clock_gettime(CLOCK_MONOTONIC, &end);
    end.tv_sec += 2;
    int e = pthread_mutex_clocklock(&r->mutex, CLOCK_MONOTONIC, &end);
    if (e) {
        fprintf(stderr, "mutex: %d\n", e);
        if (e == EOWNERDEAD)
            pthread_mutex_unlock(&r->mutex);
        munmap(r, sizeof *r);
        return 1;
    }
    int status = 0;
    if (!strcmp(argv[2], "read"))
        printf("%llu %llu %llu %llu\n", (unsigned long long)r->version,
               (unsigned long long)r->generation, (unsigned long long)r->counter,
               (unsigned long long)r->counter_xor);
    else if (!strcmp(argv[2], "generation-max"))
        r->generation = UINT64_MAX;
    else if (!strcmp(argv[2], "owner-death"))
        _exit(0);
    else if (!strcmp(argv[2], "hold")) {
        puts("LOCKED");
        fflush(stdout);
        sleep(3);
    } else
        status = 2;
    pthread_mutex_unlock(&r->mutex);
    munmap(r, sizeof *r);
    close(fd);
    return status;
}
