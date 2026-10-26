---
title: "Vetor dinâmico com gerenciamento explícito de memória"
slug: "023-mini-vec"
area: memory
summary: "Implemente MiniVec e justifique alocação, ownership, destruição e segurança nos caminhos de erro."
publishedAt: "2026-10-25"
updatedAt: "2026-10-25"
draft: false
difficulty: "advanced"
categories: ["build"]
participation: "open"
recommendedLanguage: "Rust"
acceptedLanguages: ["Rust"]
cardTopics: ["Memória", "Unsafe Rust", "Ownership"]
topics: ["Memória", "Unsafe Rust", "Ownership"]
featured: false
environment: "Linux x86_64; Rust/Cargo 1.98.1; Miri pelo canal nightly instalado; versão observada no guia"
---

**Dificuldade:** Avançado\
**Linguagem recomendada:** Rust\
**Linguagens aceitas:** Rust\
**Conceitos:** Memória, Unsafe Rust e Ownership\
**Ambiente:** Linux x86_64; Rust/Cargo 1.98.1; Miri pelo canal nightly instalado; versão observada no guia

Os materiais estão disponíveis no [guia local](README.md). O núcleo do starter permanece incompleto para implementação pelo participante. Consulte os requisitos e as limitações de ambiente antes de começar.

## O desafio

Implemente `MiniVec<T>`, um vetor genérico com criação, inserção ao final, remoção ao final e consulta imutável. Não utilize `Vec<T>` nem outro container para administrar o buffer central. A solução deve cumprir o contrato de capacidade, layout, transferência de ownership, falhas de alocação e destruição descrito abaixo.

A aceitação exige a implementação e a justificativa das invariantes que tornam sua API segura. Antes de escrever blocos `unsafe`, descreva como cada operação estabelece, usa e restaura essas invariantes. Revise todos os retornos de erro e o caso de um destrutor que entra em panic: exemplos bem-sucedidos e execução de Miri não substituem essa análise.

### Por que construir esta solução

Capacidade alocada, posições inicializadas e valores possuídos são coisas diferentes. Confundi-las pode causar leitura de memória não inicializada, double drop ou liberação incorreta. O exercício obriga a justificar a passagem entre armazenamento bruto e valores Rust. A obrigação inclui a possibilidade de panic: uma abstração `unsafe` precisa manter segurança de memória durante unwinding, mesmo que não preserve todos os efeitos lógicos da operação. [R22.1](https://doc.rust-lang.org/nomicon/exception-safety.html).

O resultado será uma estrutura deliberadamente pequena. A avaliação depende da explicação das invariantes e dos caminhos de falha, além dos exemplos que funcionam.

### Antes de começar

Ownership, generics, `Drop`, `Option`, `Result`, referências e lifetimes; noções de ponteiros, alinhamento e alocação dinâmica; capacidade de ler contratos de funções `unsafe`. Familiaridade com `NonNull<T>`, `MaybeUninit<T>` e `Layout` deve preceder a implementação. O desafio `022-typestate` e atividades de alocação de memória são preparações recomendadas, sem substituir esses conceitos.

### Objetivos de aprendizagem

- Separar comprimento, capacidade, layout e conjunto de posições inicializadas.
- Justificar cada acesso, movimentação e liberação de memória em termos de validade e ownership.
- Preservar os valores existentes e devolver o item recebido quando uma inserção falha.
- Impedir overflow de capacidade e de cálculo de layout antes de acessar o allocator.
- Demonstrar destruição correta e panic safety básica; interpretar os resultados de Miri sem tratá-los como prova universal.

### Conceitos trabalhados

Validade de ponteiros; memória não inicializada; origem e layout da alocação; transferência de ownership; destruição; falibilidade; panic safety; provas locais de `unsafe`; limites da verificação dinâmica.

## Especificação

`new() -> Result<Self, CreateError>` cria comprimento e capacidade zero. **A escolha do núcleo é rejeitar ZSTs**, inclusive `()`, retornando `UnsupportedZst` sem alocar. `push(&mut self, value: T) -> Result<(), PushError<T>>` devolve, na falha, o mesmo valor e `CapacityOverflow` ou `AllocFailed`; comprimento, capacidade e elementos anteriores permanecem intactos. Não se exige que um allocator que aborta em OOM seja convertido em erro recuperável: `AllocFailed` representa a recusa devolvida pelo adaptador ou allocator.

`pop(&mut self) -> Option<T>` remove o último elemento e transfere seu ownership; vazio retorna `None`. `get(&self, index: usize) -> Option<&T>` retorna `None` fora de `0..len`. `len()` e `capacity()` informam elementos, não bytes. A capacidade cresce de zero para um e depois dobra quando necessário, com cálculos verificados. Layout inválido deve ser rejeitado antes da alocação; `Layout` impõe limites de tamanho e alinhamento. [R22.2](https://doc.rust-lang.org/std/alloc/struct.Layout.html).

Valem sempre `len <= capacity`, inicialização exatamente em `0..len`, alinhamento adequado e uma única responsabilidade por cada valor. Capacidade zero não autoriza dereference nem liberação. Realocar preserva ownership sem clonar ou destruir os elementos transferidos.

No drop normal, os elementos remanescentes são destruídos uma vez, do último ao primeiro, e o buffer é liberado uma vez. **Panic safety básica é obrigatória:** nenhum caminho de unwind pode expor posições não inicializadas ou causar double drop. Se um destrutor panicar, o núcleo pode deixar de executar os destrutores ainda pendentes, mas deve liberar o buffer bruto uma vez e não voltar a destruir o elemento em falha. Recursos externos desses elementos podem vazar; essa concessão não autoriza UB. O destrutor do próprio mecanismo de liberação não pode panicar.

As assinaturas auxiliares fornecidas incluem `with_allocator(Allocator)` para injetar recusas e `layout_for::<T>(capacity)` para verificar limites sem alocar. Implemente essas funções e preserve suas assinaturas e o adaptador fornecido; consulte [materiais](materials/README.md).

## Exemplo

Partindo de um vetor vazio de valores `u16`, três inserções devem produzir:

| Operação | Comprimento | Capacidade |
| --- | --- | --- |
| `new()` bem-sucedido | 0 | 0 |
| `push(10)` bem-sucedido | 1 | 1 |
| `push(20)` bem-sucedido | 2 | 2 |
| `push(30)` bem-sucedido | 3 | 4 |

O próximo `pop()` devolve `Some(30)`. Este exemplo não dispensa os testes de valores não `Copy`, alinhamento, erro de alocação e unwind.

## Requisitos

- **Artefato obrigatório:** implementação, testes e registros de execução, incluindo a execução de Miri no recorte suportado.
- **Justificativa técnica obrigatória:** tabela de invariantes, comentários `SAFETY`, justificativa de cada bloco `unsafe` e auditoria de soundness dos caminhos de sucesso, erro e unwind. Explique a política de destruição e liberação, inclusive quando um destrutor panica.
- **Explorações opcionais:** comparação com a implementação real de `Vec`, conforme a seção Extensões opcionais, se realizada.

### Roteiro de desenvolvimento

1. Registre, para cada operação, quais posições contêm valores válidos antes e depois e quem detém a responsabilidade por destruí-los.
2. Modele crescimento e layout como cálculo verificável, antes de ligar o allocator.
3. Implemente o caminho vazio e as transferências de ownership; depois implemente e verifique o crescimento.
4. Injete recusa de alocação e panic em `Drop`; identifique o que continua válido em cada ponto e verifique a política contratada de liberação.
5. Revise os comentários `SAFETY` e execute Miri no recorte suportado. Seus resultados dizem respeito às execuções examinadas. [R22.3](https://github.com/rust-lang/miri).

### Materiais fornecidos

Consulte a [preparação dos materiais](materials/README.md). O clube fornece os apoios e o harness descritos; o participante implementa o núcleo e justifica suas invariantes.

## Casos de teste

Verifique vazio, `get(0)` em vazio, inserções que cruzam capacidades 1, 2 e 4, preservação da ordem e `pop` até esvaziar. Um tipo não `Copy` deve ser recuperado por `pop` e destruído somente pelo novo dono. Contadores devem confirmar descarte único dos demais elementos, inclusive após várias realocações. Um tipo com alinhamento elevado deve permanecer corretamente alinhado.

Teste `MiniVec<()>` rejeitado, recusa da primeira alocação e recusa durante crescimento, sempre com item devolvido e estado preservado. Exercite o cálculo de layout com `usize::MAX` para `u16`, sem forjar ponteiros ou estruturas inválidas. O `DropBomb` deve demonstrar a política de unwind e liberação sem exigir OOM real. Uma execução de Miri sem problemas encontrados acompanha, mas não substitui, a revisão manual.

Estes casos especificam a verificação exigida. A suíte pública está em `tests/`; consulte os comandos no guia local. Nos testes de compilação, confirme que cada cliente inválido falha pelo motivo esperado; um erro de sintaxe ou importação não comprova a propriedade. Essa regra se aplica quando houver testes de compilação no núcleo.

## Extensões opcionais

A comparação desta seção é opcional e não compõe os critérios de correção.

Compare a separação entre elementos e armazenamento na sua solução com a implementação real de `Vec`. Localize `push`, `pop` e `Drop for Vec`; observe a atualização de comprimento e a delegação da liberação a `RawVec`, sem acrescentar à solução recursos fora do escopo. [R22.4](https://doc.rust-lang.org/src/alloc/vec/mod.rs.html).

A análise de soundness, os comentários `SAFETY`, a revisão manual e a panic safety básica da própria implementação continuam obrigatórios.

Suporte a ZSTs, slices, iteradores e `reserve` são extensões com novos contratos. Garantir a execução de todos os destrutores durante unwind também é extensão. Soundness e a panic safety básica já descrita pertencem ao núcleo.

## Como participar

Desenvolva a solução em seu próprio repositório. Compartilhe código, ambiente, resultados e justificativa técnica na conversa do clube. Você pode apresentar uma tentativa incompleta; descreva o requisito ainda não atendido e um caso pequeno que permita reproduzir a dúvida.

Organize a memória técnica por contrato, decisões e invariantes, falhas e recursos, verificação, ambiente e limitações. Não há limite de páginas neste pacote.

### Referências orientadas

- **R22.1 — [Rustonomicon: Exception Safety](https://doc.rust-lang.org/nomicon/exception-safety.html).** Identificar o nível mínimo obrigatório para código `unsafe`.
- **R22.2 — [`Layout`](https://doc.rust-lang.org/std/alloc/struct.Layout.html).** Ler `array` e as condições de tamanho/alinhamento.
- **R22.3 — [Miri, documentação oficial](https://github.com/rust-lang/miri).** Consultar instalação, classes de problemas detectadas e limitações.
- **R22.4 — [Código real: `alloc/vec/mod.rs`](https://doc.rust-lang.org/src/alloc/vec/mod.rs.html).** Localizar `push`, `pop` e `Drop for Vec`; observar a atualização de comprimento e a delegação da liberação a `RawVec`, sem copiar recursos fora do escopo.

As referências do caderno foram preservadas. Consulte as revisões fixadas e o status de consulta em [references.md](references.md). A leitura de código real é complementar; a documentação necessária para interpretar o contrato continua indicada nas seções correspondentes.
