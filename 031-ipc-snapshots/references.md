# Fontes fixadas — IPC e memória compartilhada

Conferidas em 25/10/2026. Use [Linux man-pages 6.16, arquivo oficial](https://www.kernel.org/pub/linux/docs/man-pages/man-pages-6.16.tar.xz), lançado em 29/10/2025. Os links do enunciado fixam a tag `man-pages-6.16`.

| Fonte | Leitura e pergunta | Licença da fonte |
| --- | --- | --- |
| `man/man7/unix.7`, man-pages 6.16 | Permissões, `SO_PEERCRED`, `SCM_RIGHTS` e `MSG_CTRUNC`. Transferir um descritor transfere qual capacidade? | Linux-man-pages-1-para |
| `man/man2/memfd_create.2`, man-pages 6.16 | Tamanho inicial e lifetime. Por que o nome diagnóstico não é mecanismo de autenticação? | GPL-2.0-or-later |
| `man/man3/pthread_mutexattr_getpshared.3` e alias `pthread_mutexattr_setpshared.3`, man-pages 6.16 | `PTHREAD_PROCESS_SHARED`. Por que o atributo padrão não serve a esta região entre processos? | Linux-man-pages-copyleft |
| `man/man3/pthread_mutexattr_setrobust.3`, man-pages 6.16 | `EOWNERDEAD` concede o mutex, mas informa estado inconsistente. Destravar sem `pthread_mutex_consistent` impede reutilização. Qual é a diferença entre recuperar dados e invalidar a sessão? | Linux-man-pages-copyleft |
| [Linux v6.12, `net/unix/af_unix.c`](https://raw.githubusercontent.com/torvalds/linux/v6.12/net/unix/af_unix.c) | `unix_stream_connect`, associação do peer e credenciais. Por que os locks internos do socket não protegem o contador da aplicação? | GPL-2.0-or-later, conforme SPDX |

O contrato didático escolhe invalidar a sessão após `EOWNERDEAD`; a man-page descreve também aplicações que recuperam o estado. Essa alternativa da API não altera a decisão curricular. O código do kernel foi lido na tag v6.12, mas não foi recompilado nem testado nesta revisão. Nenhuma fonte foi copiada para o pacote. Texto deste guia: CC BY 4.0.
