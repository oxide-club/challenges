---
title: "Debugger mínimo para execução controlada"
slug: "029-minimal-debugger"
area: binary-reverse-engineering
summary: "Controle um filho didático com ptrace, classifique paradas e preserve sinais e ciclo de vida."
publishedAt: "2026-10-25"
updatedAt: "2026-10-25"
draft: false
difficulty: "advanced"
categories: ["build"]
participation: "open"
recommendedLanguage: "C"
acceptedLanguages: ["C"]
cardTopics: ["Processos", "Sinais", "Debugging"]
topics: ["Processos", "Sinais", "Debugging"]
featured: false
environment: "Linux x86-64 com ptrace disponível; C; alvos didáticos próprios"
---

**Dificuldade:** Avançado\
**Linguagem recomendada:** C\
**Linguagens aceitas:** C\
**Conceitos:** Processos, sinais e debugging.\
**Ambiente:** Linux x86-64 com ptrace disponível; C; alvos didáticos próprios

Os materiais estão disponíveis no [guia local](README.md). O núcleo do starter permanece incompleto para implementação pelo participante. Consulte os requisitos e as limitações de ambiente antes de começar.

## O desafio

Implemente `oxdbg -- caminho-do-alvo [argumentos]` para iniciar exclusivamente um executável didático preparado pelo clube. Uma sessão acompanha um filho e uma thread; não recebe PID para anexação. A interface aceita `run`, `step`, `regs`, `continue` e `quit` e deve produzir o event log JSON Lines definido no contrato.

O alvo principal contém uma sequência aritmética curta em assembly na entrada, sem dynamic interpreter, seguida de saída controlada. Outros fixtures exercitam sinais. A solução deve classificar corretamente as paradas, entregar os sinais previstos uma vez e encerrar o filho e realizar seu child reaping nos caminhos de limpeza. Apresente três snapshots e explique uma mudança de estado observada em cada um, como evidência de execução controlada. Não implemente breakpoints no núcleo.

### Por que construir esta solução

Um debugger precisa interpretar eventos antes de exibir registradores. Classificar toda ocorrência de `SIGTRAP` como single-step, por exemplo, pode ocultar um sinal originado no programa. O desafio exige uma máquina de estados pequena, capaz de rejeitar comandos inválidos, preservar sinais ordinários e realizar o child reaping em todos os caminhos previstos.

`ptrace` oferece inspeção e controle do tracee; diferentes causas de parada precisam ser interpretadas em conjunto com as informações de espera e de sinal ([ptrace](https://git.kernel.org/pub/scm/docs/man-pages/man-pages.git/plain/man/man2/ptrace.2?h=man-pages-6.16)). O produto esperado é um controlador com registro correto da execução e limites explícitos de suporte.

### Antes de começar

`fork`/`exec`, `waitpid`, sinais, registradores x86-64, assembly e erros de syscalls; distinguir instrução de linha de código e compreender esperas interrompidas. Preparação em engenharia reversa, processos e pipes, ABI, calling conventions e syscalls é recomendada.

### Objetivos de aprendizagem

- Implementar estados explícitos de criação, execução, parada, término e falha.
- Executar single-step e obter snapshots de registradores somente em estados válidos.
- Distinguir evento de exec, trap de stepping e signal-delivery-stop.
- Preservar a entrega correta de sinais ordinários (signal delivery) previstos nos fixtures.
- Explicar endereços observados sob PIE/ASLR sem usar constantes absolutas como oráculo.
- Garantir limpeza do filho e diagnosticar indisponibilidade de `ptrace` com evidência verificável.

### Conceitos trabalhados

Protocolo tracer/tracee, modelagem de estados, interpretação de eventos, sinal pendente, snapshots, endereços relativos e ciclo de vida de recursos. O uso de assembly limita o trecho observado e torna verificável a relação entre disassembly e estado de máquina.

## Especificação

A sessão começa em `NEW`. `run` cria o filho uma única vez, passa por `STARTING` e chega à parada após exec. A partir de `STOPPED`, `step` e `continue` levam a `RUNNING`; a próxima observação leva a `STOPPED`, `EXITED` ou `FAILED`. `regs` apenas consulta `STOPPED`. Comandos inadequados são rejeitados sem ação sobre o processo. Não existe reinício na mesma sessão.

O protocolo usa `PTRACE_TRACEME` no filho, uma parada inicial de sincronização e opções para observar exec e evitar deixar o filho executando caso o tracer desapareça. O `SIGSTOP` dessa sincronização é consumido pelo protocolo. A parada de exec é identificada como evento de `ptrace`, e não reinjetada como sinal ordinário. Essas escolhas usam mecanismos documentados de `PTRACE_O_TRACEEXEC` e `PTRACE_O_EXITKILL` ([ptrace](https://git.kernel.org/pub/scm/docs/man-pages/man-pages.git/plain/man/man2/ptrace.2?h=man-pages-6.16)).

Para cada parada, registre status bruto, sinal, código de evento e, quando disponível, `siginfo`. Classifique a causa usando esses dados e a operação pendente. `SIGTRAP` sozinho é insuficiente; `TRAP_TRACE` tem significado específico nas informações de sinal ([sigaction](https://git.kernel.org/pub/scm/docs/man-pages/man-pages.git/plain/man/man2/sigaction.2?h=man-pages-6.16)). Os fixtures incluem `SIGTRAP` gerado pelo próprio alvo, que deve permanecer um signal-delivery-stop.

Um sinal ordinário fica pendente até `step` ou `continue` e é entregue uma vez nessa retomada. Traps internos de stepping e eventos do tracer são suprimidos. O núcleo não oferece edição de sinais. Group-stops, novos processos, novas threads, seccomp events e causas não reconhecidas recebem `unsupported_stop`: registre o evento e encerre controladamente o filho, sem inventar uma interpretação.

A saída é um event log JSON Lines, com número sequencial, estado, causa, PID e campos aplicáveis. `regs` inclui ao menos `RIP`, `RSP`, `RAX`, `RBX`, `RCX`, `RDX` e `RFLAGS` em hexadecimal. O término distingue status normal de sinal terminador conforme `waitpid` ([wait](https://git.kernel.org/pub/scm/docs/man-pages/man-pages.git/plain/man/man2/waitpid.2?h=man-pages-6.16)).

Cada retomada tem prazo de cinco segundos; timeout, `quit`, EOF ou falha interna acionam limpeza e o child reaping. `EINTR` não significa término. Status da ferramenta: 0 para sessão concluída, 1 para falha, 2 para uso inválido e 77 para ambiente indisponível. Os campos `signal` e `term_signal` são inteiros JSON. O término do alvo por sinal, quando acompanhado e registrado corretamente, mantém status 0 da ferramenta; timeout, `unsupported_stop` e alvo inexistente recebem 1. O status do alvo aparece separadamente no log. Status 77 exige diagnóstico verificável de política de permissão, recurso ausente no kernel ou bloqueio do ambiente, registrando operação, erro e evidência. Um errno isolado não basta. O evento `unavailable` usa `state: "FAILED"`, PID positivo do filho, `operation: "PTRACE_TRACEME"`, `errno` inteiro e `evidence: {"kind":"child_ptrace_result","child_pid":PID,"result":-1}`. O diagnóstico permanece no stderr. Esse complemento verificável foi aprovado pelo responsável na resposta à revisão 2; o teste compara o evento com a tentativa real observada no filho, inclusive sob um filtro seccomp neutro. Erros do protocolo ou da ferramenta recebem 1, sem serem convertidos em indisponibilidade.

## Exemplo

Uma sessão pode seguir esta sequência de comandos:

```text
run
regs
step
regs
continue
```

`run` deve chegar à parada após exec. O primeiro `regs` consulta esse estado. Depois de `step`, o segundo `regs` só é válido se o filho voltar a `STOPPED`. Se o alvo terminar normalmente com código 7, registre esse código no evento de término; ele não é o status da ferramenta.

## Requisitos

Debugger; receitas dos alvos; tabela de estados e predicados; transcrições JSON; três snapshots comentados; testes dos cenários, incluindo sinais, limpeza e builds ET_EXEC/PIE.

A documentação técnica descreve build, kernel, permissões observadas e limitações; explica a classificação de paradas, a política de signal delivery e a limpeza do filho. Registre como foi obtida a referência de endereços e quais invariantes permanecem válidas entre execuções. Comparações adicionais com outros debuggers e relatos de aprendizado são opcionais; as explicações de estado e de sinais são necessárias para demonstrar a correção da solução.

### Roteiro de desenvolvimento

1. Desenhe a tabela de transições, associe comandos a estados permitidos e implemente a rejeição sem efeitos sobre o filho quando o comando for inadequado.
2. Implemente criação, sincronização inicial, observação de exec e configuração das opções de `ptrace`. Mantenha distintos os eventos do protocolo e os sinais ordinários.
3. Implemente a classificação de paradas com status bruto, evento, `siginfo` quando disponível e operação pendente. Verifique separadamente o trap do alvo e o trap de single-step.
4. Implemente `step`, `continue`, `regs`, o log e a política de sinal pendente. Entregue um sinal a um handler conhecido e confira seu efeito exatamente uma vez.
5. Inspecione o fixture com disassembly, preveja três alterações de registradores e confirme-as nos snapshots, sem usar endereços absolutos como oráculo.
6. Verifique os mesmos predicados nas versões ET_EXEC e PIE com ASLR habilitado. Relacione `RIP` ao entry point ou a um símbolo do próprio módulo; não deduza uma load base universal apenas do início do primeiro mapeamento. A leitura de disassembly e endereços simbólicos pode ser conferida no [manual do GDB](https://gnu.googlesource.com/binutils-gdb/+/6a534f85cbdb065a307aa96fbbb670948ee135c8/gdb/doc/gdb.texinfo).
7. Implemente prazos e limpeza; force erro de exec, timeout, espera interrompida, `quit`, EOF e término do tracer. Confira o encerramento e o child reaping.
8. Valide os status da ferramenta e o diagnóstico de ambiente indisponível, distinguindo uma restrição comprovada de um erro do protocolo ou da implementação.

### Materiais disponíveis

Consulte a [preparação dos materiais](materials/README.md). O guia distingue os apoios disponíveis das verificações pendentes; obrigações do clube não passam ao participante.

## Casos de teste

- `regs` antes de `run` e após término é rejeitado; segundo `run` não cria outro filho.
- Três passos no trecho fornecido produzem alterações previstas sem depender de endereço absoluto.
- `SIGUSR1` chega ao handler exatamente uma vez; `SIGTRAP` do programa não é apagado como stepping.
- Saída normal com código 7 e término por `SIGTERM` geram eventos distintos.
- Alvo inexistente, espera interrompida, `quit` e timeout não deixam filhos pendentes de child reaping.
- Builds ET_EXEC e PIE satisfazem os mesmos predicados de comportamento; não se exige que ASLR produza endereços diferentes em toda repetição.
- Indisponibilidade comprovada produz status 77. Isso registra um teste não executado; a aprovação funcional exige evidências em ambiente compatível.

Estes casos especificam a verificação exigida. O [guia local](README.md) identifica a cobertura executada, os comandos e as verificações ainda pendentes.

## Extensões opcionais

Opcionalmente, confronte transcrições do mesmo alvo didático com observações de um debugger de produção e analise como ele apresenta exec, stepping e sinais ordinários. Registre diferenças de escopo e apresentação sem transformar a interface desse debugger em requisito do produto.

Também é possível aprofundar a leitura do tratamento de exec no GDB e relacioná-lo às restrições de uma thread e de ausência de reinício. Essas comparações não substituem os casos obrigatórios de sinais, snapshots, ET_EXEC/PIE, prazos e limpeza.

Breakpoints de software, symbolication e watchpoints são extensões com contratos separados, incluindo restauração da instrução original. Multithreading, attach e controle de outros usuários ficam fora do exercício. Não há requisito de evasão ou de tornar o alvo difícil de observar.

## Como participar

Desenvolva a solução em seu próprio repositório. Compartilhe código, ambiente, resultados e justificativa técnica na conversa do clube. Você pode apresentar uma tentativa incompleta; descreva o requisito ainda não atendido e um caso pequeno que permita reproduzir a dúvida.

Organize a memória técnica por contrato, decisões e invariantes, falhas e recursos, verificação, ambiente e limitações. Respeite os limites de páginas quando indicados nos requisitos.

### Referências orientadas

- [Linux man-pages 6.16 — ptrace](https://git.kernel.org/pub/scm/docs/man-pages/man-pages.git/plain/man/man2/ptrace.2?h=man-pages-6.16): ler operações, “Stopped states” e signal delivery.
- [Linux man-pages 6.16 — wait](https://git.kernel.org/pub/scm/docs/man-pages/man-pages.git/plain/man/man2/waitpid.2?h=man-pages-6.16) e [sigaction](https://git.kernel.org/pub/scm/docs/man-pages/man-pages.git/plain/man/man2/sigaction.2?h=man-pages-6.16): interpretar status e `si_code`.
- [GDB — Source and Machine Code](https://gnu.googlesource.com/binutils-gdb/+/6a534f85cbdb065a307aa96fbbb670948ee135c8/gdb/doc/gdb.texinfo): relacionar instruções, símbolos e endereços.
- **Código real:** [GDB 6a534f85cbdb065a307aa96fbbb670948ee135c8 — correção de estado após exec](https://sourceware.org/pipermail/gdb-cvs/2023-November/057012.html). Ler `linux_handle_extended_wait` e o teste associado no patch publicado; explicar por que o núcleo restringe-se a uma thread e por que exec exige tratamento próprio.

As referências usam Linux man-pages 6.16 e as revisões de código identificadas acima. Consulte [origem, licenças e leitura dirigida](references.md), com a conferência de 25/10/2026. A leitura de produção complementa o contrato; não amplia o núcleo.
