# Fontes fixadas — controle de processos

Conferidas em 25/10/2026. Use [Linux man-pages 6.16, arquivo oficial](https://www.kernel.org/pub/linux/docs/man-pages/man-pages-6.16.tar.xz), lançado em 29/10/2025. Os links do enunciado fixam a tag `man-pages-6.16`.

| Fonte | Leitura e pergunta | Licença da fonte |
| --- | --- | --- |
| `man/man2/ptrace.2`, man-pages 6.16 | Estados de parada, `PTRACE_O_TRACEEXEC`, `PTRACE_O_EXITKILL` e reinjeção. Qual dado distingue um evento de exec de um signal-delivery-stop? | GPL-2.0-or-later |
| `man/man2/wait.2` e alias `waitpid.2`, man-pages 6.16 | Separar saída normal, sinal terminador e parada. Por que o status do alvo não é o da ferramenta? | Linux-man-pages-copyleft |
| `man/man2/sigaction.2`, man-pages 6.16 | `siginfo` e `si_code`. Por que apenas observar SIGTRAP não identifica a causa? | Linux-man-pages-copyleft |
| [GDB, commit 6a534f85cbdb065a307aa96fbbb670948ee135c8](https://sourceware.org/pipermail/gdb-cvs/2023-November/057012.html) | `linux_handle_extended_wait` em `gdb/linux-nat.c` e `gdb/testsuite/gdb.threads/threads-after-exec.exp`. O que acontece às listas internas quando uma thread que não é líder executa exec? | GPL-3.0-or-later, conforme cabeçalho do teste acrescentado |
| [Linux v6.12, `kernel/signal.c`](https://raw.githubusercontent.com/torvalds/linux/v6.12/kernel/signal.c) | `signal_delivered` chama `ptrace_notify` quando há stepping. Por que essa parada interna não corresponde a um segundo sinal do alvo? | GPL-2.0-only, conforme SPDX |
| [Manual GDB na mesma revisão, `gdb/doc/gdb.texinfo`](https://gnu.googlesource.com/binutils-gdb/+/6a534f85cbdb065a307aa96fbbb670948ee135c8/gdb/doc/gdb.texinfo) | Nó `Machine Code`, comandos `info line` e `disassemble`. Como relacionar instruções, símbolos e endereços sem fixar um endereço absoluto? | GFDL-1.3-or-later, com seções invariantes e textos de capa definidos em `@copying` |

O commit e o diff foram confirmados no arquivo primário `gdb-cvs`; o patch publicado em 13/11/2023 tem Change-Id `I21ec18072c7750f3a972160ae6b9e46590376643`. O manual foi lido no espelho GNU da mesma revisão. A consulta gitweb retornou HTTP 403, mas o arquivo da lista e o espelho forneceram as fontes, portanto não resta pendência de leitura desse patch.

O exemplo de produção trata múltiplas threads, fora do núcleo do desafio. Não compilamos GDB nem executamos seu testcase; os resultados narrados pelo autor não são resultados locais. Nenhuma fonte foi copiada para o pacote. Texto deste guia: CC BY 4.0.
