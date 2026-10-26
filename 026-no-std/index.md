---
title: "Executável Rust com no_std e startup explícito"
slug: "026-no-std"
area: systems-fundamentals
summary: "Produza um ELF no_std com startup explícito, saída por syscalls e dependências verificáveis."
publishedAt: "2026-10-25"
updatedAt: "2026-10-25"
draft: true
difficulty: "advanced"
categories: ["build"]
participation: "open"
recommendedLanguage: "Rust"
acceptedLanguages: ["Rust"]
cardTopics: ["no_std", "ABI", "Syscalls"]
topics: ["no_std", "ABI", "Syscalls"]
featured: false
environment: "Linux x86-64; target x86_64-unknown-linux-gnu; Rust e stub assembly fornecido pelo clube"
---

**Dificuldade:** Avançado\
**Linguagem recomendada:** Rust\
**Linguagens aceitas:** Rust\
**Conceitos:** no_std, ABI, syscalls\
**Ambiente:** Linux x86-64; target x86_64-unknown-linux-gnu; Rust e stub assembly fornecido pelo clube

**Em revisão.** Os materiais de preparação estão disponíveis no [guia local](README.md). O núcleo do starter permanece incompleto. Consulte as evidências e limitações de ambiente; a publicação depende de revisão independente, piloto e aprovação editorial.

## O desafio

Produza um executável que escreva exatamente `Oxide Club: no_std\n` em stdout — 19 bytes, com um único LF final — e termine com status zero. Use `#![no_std]` e `#![no_main]`, implemente o caminho Rust e os wrappers de syscalls previstos e respeite as restrições de ELF, dependências, ABI, panic e falhas de escrita do contrato.

A entrega deve permitir reproduzir o build, testar os caminhos de execução e inspecionar o artefato. Explique como o stub transfere controle para a função Rust e como o processo termina sem retorno. A comparação com um programa convencional e as medições comparativas de tamanho são investigações complementares opcionais.

### Por que construir esta solução

`#![no_std]` substitui o prelude usual e remove o linking automático de `std`; não impede que uma dependência a introduza explicitamente. Também não significa ausência de SO ou de serviços de runtime. [R28.1](https://doc.rust-lang.org/1.98.1/reference/names/preludes.html#the-no_std-attribute). Neste desafio, o kernel Linux continua carregando o processo e atendendo suas syscalls, enquanto o startup, o caminho de panic e as dependências do executável precisam ser controlados e identificados.

A solução deve cumprir um contrato de execução e de composição do binário. Além de produzir a saída correta, precisa demonstrar quais responsabilidades cabem a `core`, ao compilador, ao linker, ao stub e ao SO. O inventário e a inspeção são evidências de conformidade; o funcionamento aparente do programa, sozinho, não comprova as restrições do artefato.

### Antes de começar

Rust intermediário, ponteiros e leitura de `unsafe`; calling conventions; stack; fundamentos de ELF, linking e syscalls Linux x86-64. Familiaridade com assembly é necessária para auditar o stub, embora o participante não precise inventar seu próprio startup. Atividades de compilação, ABI, linking e syscalls são recomendações de preparação.

### Objetivos de aprendizagem

- Construir um executável com `no_std` e `no_main` que satisfaça as restrições de formato, dependências e saída.
- Diferenciar `core`, `alloc` e `std`, identificando os serviços efetivamente usados pelo artefato.
- Explicar a passagem do entry point ELF para uma função Rust com ABI definida e justificar o alinhamento da stack.
- Realizar saída e término de processo por syscalls, com o contrato de erros e escrita parcial especificado.
- Inspecionar símbolos, dependências dinâmicas, entry point e segmentos ELF para demonstrar conformidade.
- Implementar e descrever a política de panic e identificar a origem das rotinas auxiliares presentes.

### Conceitos trabalhados

`no_std`/`no_main`; entry point; ABI de processo e de função; linker; panic handler; compiler builtins; I/O parcial; estado de saída; rastreabilidade de dependências.

## Especificação

O artefato mínimo deve ser ELF64 para Linux x86-64, com tipo `ET_EXEC`, entry point `_start`, sem `PT_INTERP`, sem entradas `DT_NEEDED` e sem símbolos obrigatórios não resolvidos. Ele não usa `std`, `alloc`, allocator global ou libc. `core` e componentes de suporte do compilador são permitidos desde que nomeados no inventário; o linker não deve ocultar erros ignorando símbolos ausentes.

O stub recebe o controle segundo a ABI de entrada do processo e faz a ponte para `extern "C" fn club_main() -> !`. O alinhamento de stack exigido nessa chamada precisa ser preservado. `_start` não é chamado como uma função C comum, e não pode terminar com retorno para um suposto chamador. A entrega deve mostrar o papel do stub e a saída não retornante, relacionando-os à especificação da plataforma. [R28.2](https://gitlab.com/x86-psABIs/x86-64-ABI/-/raw/e1ce098331da5dbd66e1ffc74162380bcc213236/x86-64-ABI/low-level-sys-info.tex).

O núcleo usa a disposição de seções do linker fornecido e uma seleção explícita de entry point; escrever um linker script completo fica como extensão. Flags para retirar CRT, escolher o formato e controlar linking constam de `tests/check.py`, sem serem apresentadas como universais para qualquer target.

`unsafe fn raw_write(fd: i32, ptr: *const u8, len: usize) -> isize` devolve a contagem escrita ou `-errno`; `raw_exit(status: u8) -> !` termina o processo. A camada `write_all(&[u8]) -> Result<(), WriteError>` escreve em stdout: vazio retorna sucesso sem syscall; escrita parcial avança apenas pelo total escrito; `EINTR` repete a parte restante; retorno zero com bytes pendentes vira `WriteZero`; outros erros viram `Syscall(errno)` com errno positivo. O programa termina com `74` se essa saída falhar, sem exigir diagnóstico em stderr.

O perfil não usa unwinding. O `#[panic_handler]` termina com status `101`, sem alocar nem tentar continuar; uma opção exclusiva de teste provoca panic antes de qualquer saída. Uma referência passada ao wrapper deve permanecer válida por toda a syscall; constraints, clobbers e efeitos de memória do assembly precisam corresponder à ABI.

`no_std` não elimina automaticamente funções auxiliares geradas pelo compilador. Se aparecerem símbolos como rotinas de memória, a entrega deve identificar quem os fornece; stubs vazios que apenas fazem o linker aceitar o binário não satisfazem o contrato. [R28.3](https://doc.rust-lang.org/1.98.1/core/).

## Exemplo

No caminho normal, stdout contém exatamente estes 19 bytes, em hexadecimal:

```text
4f 78 69 64 65 20 43 6c 75 62 3a 20 6e 6f 5f 73 74 64 0a
```

Eles representam `Oxide Club: no_std` seguido de um LF. O status é zero. O caminho de teste de panic produz stdout vazio e status `101`.

## Requisitos

Fontes; configuração e comandos de build; saídas e status observados; testes com o adaptador e o harness de subprocessos; inspeção `readelf`/`nm`; inventário de dependências e rotinas auxiliares; explicação do stub e da saída não retornante.

A justificativa técnica deve relacionar o stub à ABI da plataforma, demonstrar a preservação do alinhamento e explicar quem fornece os componentes de suporte realmente presentes. Inclua a política de escrita e de panic. Medidas comparativas de tamanho, seções e serviços de um programa com `std` pertencem à investigação complementar e não são necessárias para concluir o desafio.

### Roteiro de desenvolvimento

1. Defina o caminho kernel → `_start` → função Rust → syscall → término e marque as mudanças de ABI que a solução precisa respeitar.
2. Audite o stub fornecido, preserve o alinhamento da stack e configure o entry point e o linking segundo o starter validado.
3. Implemente os wrappers e a política de escrita; teste-a com o adaptador controlado antes da execução real, cobrindo avanços de buffer, interrupções e erros.
4. Implemente o término normal, o status de falha de saída e o panic handler sem unwinding. Execute esses caminhos em subprocessos.
5. Inspecione o ELF final com `readelf` e `nm`: confira tipo, entry point, segmentos, dependências e símbolos obrigatórios. Registre cada símbolo de suporte presente após o linking e sua origem.
6. Consolide os testes e a justificativa de ABI, validade dos buffers, constraints, clobbers e efeitos de memória do assembly. Relacione cada restrição do contrato à evidência que demonstra seu cumprimento.

### Materiais fornecidos

Consulte os [materiais fornecidos](materials/README.md). O guia distingue os apoios do clube das implementações do participante.

## Casos de teste

O caminho normal precisa produzir os 19 bytes exatos e status zero. O adaptador deve verificar buffer vazio, escrita parcial seguida de conclusão, interrupção `EINTR`, retorno zero indevido e erro definitivo. Nenhum prefixo já escrito pode ser reenviado. Com stdout fechado pelo harness, o subprocesso deve terminar com `74`; com a opção de panic, deve produzir stdout vazio e status `101`.

A inspeção deve confirmar formato, entry point e ausência das dependências dinâmicas proibidas. O participante deve explicar de onde vieram as rotinas auxiliares realmente presentes e demonstrar o papel do stub, o alinhamento da stack e o término não retornante. Stubs vazios para satisfazer o linker não são aceitos.

Não há meta fixa de tamanho nem obrigação de produzir um executável convencional. Se a comparação opcional for realizada, um binário maior que a versão com `std` continua sendo um resultado válido, desde que as condições sejam documentadas e o contrato do núcleo seja cumprido.

Estes casos especificam a verificação exigida. A suíte pública está descrita no guia local; ela não substitui a revisão das invariantes.

## Extensões opcionais

Opcionalmente, produza um programa convencional com a mesma saída e compare tamanho total, seções relevantes e serviços presentes nos dois artefatos. Registre condições equivalentes de otimização e stripping, ou justifique as diferenças, sem pressupor redução de tamanho por usar `no_std`.

Leia o startup real de `std` para localizar serviços ausentes ou substituídos no programa mínimo. [R28.4](https://doc.rust-lang.org/1.98.1/src/std/rt.rs.html). Essa comparação e um relato de aprendizado podem ampliar a análise; não substituem nem ampliam os requisitos funcionais de conclusão.

`alloc`, linker script próprio, outro target e ambiente freestanding/emulado são extensões distintas. O núcleo não constrói kernel nem substitui o loader ELF. Sinais como `SIGPIPE`, argumentos, ambiente, TLS e inicialização de threads ficam fora do contrato inicial.

## Como participar

Desenvolva a solução em seu próprio repositório. Compartilhe código, ambiente, resultados e justificativa técnica na conversa do clube. Você pode apresentar uma tentativa incompleta; descreva o requisito ainda não atendido e um caso pequeno que permita reproduzir a dúvida.

Organize a memória técnica por contrato, decisões e invariantes, falhas e recursos, verificação, ambiente e limitações. Não há limite de páginas definido para esta atividade.

### Referências orientadas

- **R28.1 — [Rust Reference: atributo `no_std`](https://doc.rust-lang.org/1.98.1/reference/names/preludes.html#the-no_std-attribute).** Ler os efeitos reais e a possibilidade de `std` participar explicitamente do linking.
- **R28.2 — [x86-64 psABI: Low Level System Information](https://gitlab.com/x86-psABIs/x86-64-ABI/-/raw/e1ce098331da5dbd66e1ffc74162380bcc213236/x86-64-ABI/low-level-sys-info.tex).** Consultar Function Calling Sequence e Process Initialization no fonte oficial da especificação; a árvore está fixada, mas o download do fonte e da licença permanece pendente. A edição renderizada consultada é identificada por hash em [AUDIT.md](materials/AUDIT.md).
- **R28.3 — [`core`: requisitos de integração](https://doc.rust-lang.org/1.98.1/core/).** Ler How to use the core library, especialmente rotinas de memória e panic handler.
- **R28.4 — [Código real: `std/rt.rs`](https://doc.rust-lang.org/1.98.1/src/std/rt.rs.html).** Localizar `lang_start`, `lang_start_internal`, inicialização e cleanup; relacionar cada responsabilidade ao programa mínimo, sem tratar essas APIs internas como estáveis.

As referências Rust abaixo usam a edição 1.98.1. O estado da proveniência externa está no guia local. A leitura de código real é complementar; a documentação necessária para interpretar o contrato continua indicada nas seções correspondentes.
