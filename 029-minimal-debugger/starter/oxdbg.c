/* SPDX-License-Identifier: MIT */
#include <stdio.h>
#include <string.h>
int main(int argc, char **argv) {
    if (argc < 3 || strcmp(argv[1], "--")) {
        fputs("uso: oxdbg -- alvo [args]\n", stderr);
        return 2;
    }
    /* TODO: transporte stdin; NEW/STARTING/STOPPED/RUNNING/EXITED/FAILED;
    TRACEME, exec, sinais, registradores, prazo monotônico e recolhimento. */
    fputs("oxdbg: controlador ainda não implementado\n", stderr);
    return 1;
}
