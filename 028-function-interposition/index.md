---
title: "Tracing por interposição de funções"
slug: "028-function-interposition"
area: systems-fundamentals
summary: "Implemente interposição de uma função própria preservando retorno, saída e errno."
publishedAt: "2026-10-25"
updatedAt: "2026-10-25"
draft: false
difficulty: "advanced"
categories: ["build"]
participation: "open"
recommendedLanguage: "C"
acceptedLanguages: ["C"]
cardTopics: ["Linking dinâmico", "Interposição de funções", "Concorrência"]
topics: ["Linking dinâmico", "Interposição de funções", "Concorrência"]
featured: false
environment: "Linux x86-64, ELF e glibc; C no núcleo"
---

**Dificuldade:** Avançado\
**Linguagem recomendada:** C\
**Linguagens aceitas:** C\
**Conceitos:** Linking dinâmico, interposição e concorrência.\
**Ambiente:** Linux x86-64, ELF e glibc; C no núcleo

Os materiais estão disponíveis no [guia local](README.md). O núcleo do starter permanece incompleto para implementação pelo participante. Consulte os requisitos e as limitações de ambiente antes de começar.

## O desafio

Construa `libcalc.so`, uma aplicação que chame sua função exportada e `libtrace.so`, que observe essa mesma função por `LD_PRELOAD` e delegue à definição real. A solução deve emitir os registros previstos e preservar o retorno, o valor de saída e `errno` nos casos de sucesso, erro, concorrência, falha do sink e reentrancy.

Use execuções equivalentes com e sem interposição como verificação funcional obrigatória. O wrapper pode registrar argumentos numéricos e resultados do alvo didático. O núcleo não intercepta `malloc`, libc em geral ou programas de terceiros; não altera instruções nem tabelas de outros processos. Inicialização e logging integram o contrato da solução.

### Por que construir esta solução

Tracing e profiling acrescentam comportamento ao caminho de execução. Se esse acréscimo altera resultados, códigos de erro ou sincronização, a instrumentação deixa de preservar o contrato do alvo. Uma função pequena, com resultados conhecidos, permite construir e verificar um wrapper que delega corretamente mesmo quando seu logging falha ou reentra.

O dynamic loader admite pré-carregamento de shared objects; `RTLD_NEXT` permite procurar uma definição posterior na ordem de busca. Esse mecanismo sustenta a solução com `LD_PRELOAD` ([ld.so](https://git.kernel.org/pub/scm/docs/man-pages/man-pages.git/plain/man/man8/ld.so.8?h=man-pages-6.16), [dlsym](https://git.kernel.org/pub/scm/docs/man-pages/man-pages.git/plain/man/man3/dlsym.3?h=man-pages-6.16)). A atividade concentra-se em software construído pelo próprio desafio.

### Antes de começar

Bibliotecas compartilhadas, símbolos ELF, ponteiros para função, ABI C, linking dinâmico e noções de threads. O participante deve conseguir chamar uma função de uma biblioteca própria e comparar stdout, status de retorno e `errno`. Preparação em ABI, calling conventions e linking dinâmico é recomendada; conhecimentos de FFI permitem uma variante posterior em Rust.

### Objetivos de aprendizagem

- Construir uma aplicação e bibliotecas compartilhadas cuja resolução de símbolos possa ser demonstrada.
- Implementar interposição que preserve o comportamento de sucesso e erro da função real.
- Verificar preservação de `errno` por thread, inclusive quando o logging falha.
- Implementar inicialização, reentrancy e logging concorrente sem recursão infinita nem mistura de registros.
- Construir um caso deliberadamente não interposto e explicar sua resolução, para delimitar o alcance da solução.

### Conceitos trabalhados

Ordem de busca de símbolos, fronteira de ABI, estado local de thread, inicialização concorrente, reentrancy e observabilidade. O exercício separa a semântica de `libcalc` da política de logging e da disponibilidade do ambiente de instrumentação.

## Especificação

A API observada é `int calc_div(int a, int b, int *out)`, com `int` de 32 bits no ambiente fixado:

- `out == NULL`: retorna −1 e define `errno = EINVAL`.
- Com `out` válido, `b == 0`: retorna −1, define `EDOM` e preserva `*out`.
- Com `out` válido, `a == INT_MIN` e `b == -1`: retorna −1, define `ERANGE` e preserva `*out`.
- Nos demais casos: retorna 0, escreve o quociente inteiro com truncamento em direção a zero e preserva o valor de `errno` da entrada.
- Essa ordem define a precedência dos erros. Ponteiros não nulos devem designar um `int` gravável; validar endereços arbitrários não faz parte da API.

A função real deve ser chamada exatamente uma vez por invocação, com os mesmos argumentos, inclusive nos casos de erro previstos. O wrapper preserva retorno, valor final de `*out` quando aplicável e `errno` final. Não se exige equivalência de tempo, ordem global entre threads ou stack traces.

Cada chamada externa gera um registro JSON por linha quando o sink funciona: `call_id` único, identificador de thread, argumentos, retorno, `errno_before`, `errno_after` e `value`. Este último é `null` no erro. Um sink fornecido pelo teste pode provocar reentrancy uma única vez: a chamada aninhada delega normalmente, sem emitir novo registro. Assim, o teste verifica uma política explícita, sem exigir logging recursivo.

Os registros não podem intercalar fragmentos de linhas. Em concorrência, a comparação usa identificadores e contagem, sem exigir ordem de conclusão. Falha do sink é best effort: pode perder o evento, mas não modifica os resultados de `calc_div`. Não há garantia de logging em signal handlers, cancelamento de threads ou término abrupto.

A resolução da função deve terminar antes de habilitar callbacks do sink; a publicação de seu estado precisa ser segura para os workers. Erro de resolução ou endereço não chamável interrompe a aplicação de teste com status 125 e diagnóstico de instrumentação. Esse estado não é disfarçado de erro aritmético. A interpretação de `dlsym` deve considerar `dlerror`, pois um ponteiro nulo sozinho não caracteriza toda falha de busca ([contrato de dlsym](https://git.kernel.org/pub/scm/docs/man-pages/man-pages.git/plain/man/man3/dlsym.3?h=man-pages-6.16)).

## Exemplo

Com `out` válido e `errno` inicial registrado, `calc_div(7, 2, out)` retorna `0`, escreve `3` e preserva `errno`. A execução com interposição deve manter esses três resultados e acrescentar um registro quando o sink funcionar.

Com divisor zero, a função retorna `-1`, define `EDOM` e preserva o valor anterior de `*out`. O campo `value` do registro é `null`.

## Requisitos

Três componentes compiláveis; comandos de execução com e sem `LD_PRELOAD`; logs estruturados; verificação automatizável de equivalência de resultados; mapa de símbolos; evidências de reentrancy e concorrência; variante de chamada direta e explicação de sua resolução.

A documentação técnica deve justificar a chamada da função real exatamente uma vez, a preservação de retorno, `*out` e `errno`, a inicialização segura e a política de logging. Identifique falha do experimento separadamente de falha funcional. Um relato de aprendizado ou comparações adicionais de mecanismos de hooking são opcionais; a demonstração de transparência exigida pelo contrato permanece obrigatória.

### Roteiro de desenvolvimento

1. Implemente `calc_div` e estabeleça a baseline, verificando precedência de erros, preservação de `*out` e diferentes valores iniciais de `errno`.
2. Construa a aplicação com a dependência dinâmica prevista. Inspecione o símbolo exportado e registre onde a definição real reside.
3. Implemente resolução e publicação segura da função real antes de habilitar callbacks do sink. Separe falha de instrumentação de erro aritmético.
4. Implemente a delegação exatamente uma vez, a preservação do estado observável e a geração dos registros JSON Lines.
5. Verifique separadamente erros aritméticos, sink que altera `errno`, falha do sink, reentrancy e concorrência. Compare automaticamente os resultados com a baseline.
6. Compile uma variante em que a implementação de `calc_div` esteja incorporada e vinculada diretamente ao executável; confirme o mesmo resultado aritmético e a ausência de eventos do wrapper, explicando a resolução da chamada.
7. Consolide os casos mínimos e a justificativa de inicialização, reentrancy, integridade dos registros e preservação de `errno`, delimitando quais chamadas a solução efetivamente interpõe.

### Materiais disponíveis

Consulte a [preparação dos materiais](materials/README.md). O guia distingue os apoios disponíveis das verificações pendentes; obrigações do clube não passam ao participante.

## Casos de teste

Exija, no mínimo:

- `7/2 = 3` e `-7/2 = -3`, mantendo sentinela de `errno`.
- Divisão por zero, overflow aritmético e ponteiro nulo; `NULL` combinado com divisor zero confirma a precedência.
- Primeira chamada e chamadas subsequentes com resultados equivalentes à baseline.
- Sink que altera `errno`, sink que falha e sink que reentra: o chamador mantém o resultado correto em todos.
- Quatro threads com mil chamadas cada: 4.000 registros externos completos, identificadores únicos e resultados por thread corretos, com sink saudável.
- Variante de chamada direta: mesmo resultado aritmético e nenhum evento do wrapper.
- Falha controlada de resolução: status 125, diagnóstico e ausência de chamada por ponteiro inválido.

A aprovação exige explicar por que uma saída aritmética correta sozinha não demonstra transparência da instrumentação.

Estes casos especificam a verificação exigida. O [guia local](README.md) identifica a cobertura executada, os comandos e as verificações ainda pendentes.

## Extensões opcionais

Opcionalmente, examine outros arranjos de linking do alvo próprio e compare seus mapas de símbolos com o caso obrigatório de chamada direta. Relate o que cada configuração permite afirmar sobre resolução, sem generalizar para toda chamada a qualquer função.

Uma comparação conceitual com Detours ou um relato sobre observabilidade pode ampliar a análise. Ela não exige implementar outro mecanismo e não substitui a verificação de equivalência com e sem interposição, a explicação da reentrancy ou a preservação de `errno`.

São extensões uma variante Rust com ABI compatível, versões de símbolos, encadeamento de wrappers e seleção de eventos. Comparar conceitualmente com Detours é possível, mas envolve outro mecanismo. Patching, funções variádicas, chamadas em signal handlers e instrumentação arbitrária exigem contratos próprios.

## Como participar

Desenvolva a solução em seu próprio repositório. Compartilhe código, ambiente, resultados e justificativa técnica na conversa do clube. Você pode apresentar uma tentativa incompleta; descreva o requisito ainda não atendido e um caso pequeno que permita reproduzir a dúvida.

Organize a memória técnica por contrato, decisões e invariantes, falhas e recursos, verificação, ambiente e limitações. Respeite os limites de páginas quando indicados nos requisitos.

### Referências orientadas

- [Linux man-pages 6.16 — ld.so](https://git.kernel.org/pub/scm/docs/man-pages/man-pages.git/plain/man/man8/ld.so.8?h=man-pages-6.16): ler `LD_PRELOAD` e secure-execution mode.
- [Linux man-pages 6.16 — dlsym](https://git.kernel.org/pub/scm/docs/man-pages/man-pages.git/plain/man/man3/dlsym.3?h=man-pages-6.16): ler `RTLD_NEXT`, tratamento de erro e atributos de thread safety.
- **Código real:** [glibc 68608ef426b88e73e0e3178497bcfe34dd8a66ef — elf/dl-sym.c e dl-sym-post.h](https://sourceware.org/pipermail/glibc-cvs/2020q1/068675.html). No snapshot histórico, acompanhar `do_sym`, o ramo `RTLD_NEXT` e a identificação do objeto chamador. Usá-lo para compreender o contexto da resolução, sem assumir que o restante do loader seja necessário ao exercício.

As referências usam Linux man-pages 6.16 e as revisões de código identificadas acima. Consulte [origem, licenças e leitura dirigida](references.md), com a conferência de 25/10/2026. A leitura de produção complementa o contrato; não amplia o núcleo.
