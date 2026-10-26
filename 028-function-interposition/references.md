# Fontes fixadas — interposição

Conferidas em 25/10/2026. A referência documental é [Linux man-pages 6.16, arquivo oficial](https://www.kernel.org/pub/linux/docs/man-pages/man-pages-6.16.tar.xz), lançado em 29/10/2025. Os links do enunciado apontam para a tag `man-pages-6.16`; não para a versão corrente de man7.org.

| Fonte | Leitura e pergunta | Licença da fonte |
| --- | --- | --- |
| `man/man8/ld.so.8`, man-pages 6.16 | Ordem de busca, `LD_PRELOAD`, `DT_RPATH` e `DT_RUNPATH`. Por que o cliente de teste precisa permitir que `LD_LIBRARY_PATH` selecione o substituto opaco? | Domínio público, conforme cabeçalho |
| `man/man3/dlsym.3`, man-pages 6.16 | `RTLD_NEXT` procura depois do objeto chamador; a falha deve ser consultada por `dlerror`. Por que endereço nulo e erro não são equivalentes? | GPL-2.0-or-later |
| [glibc 68608ef426b88e73e0e3178497bcfe34dd8a66ef](https://sourceware.org/pipermail/glibc-cvs/2020q1/068675.html) | `elf/dl-sym.c`, `do_sym` e a separação em `elf/dl-sym-post.h`. Como o objeto chamador afeta `RTLD_NEXT`? | LGPL-2.1-or-later, conforme cabeçalho do arquivo acrescentado |

O patch foi lido no arquivo primário `glibc-cvs`, que identifica o commit completo e inclui o diff. O loader de produção trata situações além da função didática e não é uma implementação a copiar. Não executamos build nem suíte da glibc. Nenhum trecho de fonte foi incorporado ao pacote; os links preservam as licenças próprias. Texto deste guia: CC BY 4.0.
