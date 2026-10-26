---
title: "Célula com borrows verificados em runtime"
slug: "024-mini-refcell"
area: memory
summary: "Implemente uma célula com guards RAII, controle de borrows e auditoria da interface segura."
publishedAt: "2026-10-25"
updatedAt: "2026-10-25"
draft: false
difficulty: "advanced"
categories: ["build"]
participation: "open"
recommendedLanguage: "Rust"
acceptedLanguages: ["Rust"]
cardTopics: ["Interior mutability", "Lifetimes", "Unsafe Rust"]
topics: ["Interior mutability", "Lifetimes", "Unsafe Rust"]
featured: false
environment: "Linux x86_64; Rust/Cargo 1.98.1; Miri pelo canal nightly instalado; versão observada no guia"
---

**Dificuldade:** Avançado\
**Linguagem recomendada:** Rust\
**Linguagens aceitas:** Rust\
**Conceitos:** Interior mutability, Lifetimes e Unsafe Rust\
**Ambiente:** Linux x86_64; Rust/Cargo 1.98.1; Miri pelo canal nightly instalado; versão observada no guia

Os materiais estão disponíveis no [guia local](README.md). O núcleo do starter permanece incompleto para implementação pelo participante. Consulte os requisitos e as limitações de ambiente antes de começar.

## O desafio

Implemente `MiniRefCell<T>` sobre `UnsafeCell<T>` e um estado de borrow privado. A célula deve oferecer acesso compartilhado ou exclusivo por guards RAII, rejeitar conflitos por erros recuperáveis e impedir que referências escapem dos lifetimes que as autorizam.

A solução será aceita quando cumprir a máquina de estados e todos os requisitos do contrato, incluindo o limite de leitores, os auto traits, a liberação em saídas normais e unwind e a política para guards esquecidos. Construa primeiro a máquina de estados; só depois introduza a criação das referências e seus guards. A justificativa das invariantes que tornam segura cada conversão do ponteiro interno em referência é parte obrigatória da solução.

### Por que construir esta solução

`UnsafeCell<T>` permite que o conteúdo de uma shared reference seja mutado sob um protocolo adequado. Ele não dispensa a exclusividade de mutable references nem resolve data races. A abstração construída aqui deve transformar essa permissão de baixo nível em uma API que autoriza leitores ou um escritor. [R24.1](https://doc.rust-lang.org/std/cell/struct.UnsafeCell.html).

Esse mecanismo tem duas camadas: estado dinâmico decide quando criar referências; lifetimes limitam por quanto tempo o chamador pode utilizá-las. A solução só estará correta quando as duas camadas concordarem, incluindo conflitos, overflow e abandono de guards.

### Antes de começar

Ownership, referências, lifetimes, `Drop`, generics, traits `Deref`/`DerefMut` e contratos de `unsafe`; conhecer a diferença entre compartilhar uma referência e mover ownership para outra thread. Os desafios `022-typestate` e `023-mini-vec` são preparações recomendadas. Nenhuma estrutura concorrente precisa ser implementada.

### Objetivos de aprendizagem

- Definir estados de borrow e aplicar suas transições sem produzir acessos incompatíveis.
- Implementar guards cujo `Deref` e `DerefMut` preservem o lifetime do borrow.
- Devolver erros recuperáveis em conflitos, sem panic como caminho normal da API.
- Tratar explicitamente o limite do contador de leitores.
- Explicar `!Sync`, a possibilidade condicionada de `Send` e o efeito de `mem::forget`.

### Conceitos trabalhados

Interior mutability; permissões dinâmicas; RAII; contadores limitados; borrows vinculados a guards; leak safety; auto traits; segurança durante unwinding; revisão de invariantes.

## Especificação

`new(value: T) -> Self` começa sem borrows. `try_borrow(&self) -> Result<MiniRef<'_, T>, BorrowError>` adquire leitura; `try_borrow_mut(&self) -> Result<MiniRefMut<'_, T>, BorrowError>` adquire escrita. Não haverá métodos chamados `borrow` que silenciosamente adotem semântica de `Result` diferente da convenção documentada de `RefCell`.

O estado distingue livre, leitores ativos e escritor ativo. O limite pedagógico é **255 leitores simultâneos**, para tornar a borda alcançável pela API pública. O 256º pedido retorna `ReaderLimitReached`, preservando o contador. Com escritor ativo, qualquer pedido retorna `WriterActive`; com leitores ativos, pedido exclusivo retorna `ReadersActive`. Falhas não criam guard nem alteram estado. Aritmética não pode fazer wraparound para um estado livre.

`MiniRef` implementa somente `Deref<Target = T>`; `MiniRefMut`, `Deref` e `DerefMut`. Uma referência obtida do guard não pode sobreviver ao borrow desse guard. O lifetime do próprio guard também está vinculado ao `MiniRefCell`. Não há conversão pública que extraia `&T` ou `&mut T` com lifetime independente, nem `Clone` de guards. Descartar um leitor reduz o contador; descartar o escritor libera a célula. Esses destrutores não podem panicar.

O container permanece `!Sync`; não haverá `unsafe impl Sync`. Isso não implica `!Send`: transferir ownership da célula, sem borrows vivos, pode ser permitido quando `T: Send`. Não acrescente `unsafe impl Send` para superar erros do compilador; justifique os auto traits obtidos pelos campos. Guards do núcleo não podem ser transferidos ou compartilhados entre threads.

Esquecer um guard com `mem::forget` **não pode causar UB**. A política escolhida conserva a autorização ocupada: um leitor esquecido impede futuros escritores; um escritor esquecido impede qualquer novo borrow. O container continua descartável quando não existem referências utilizáveis. A linguagem não garante execução de todos os destrutores, e código `unsafe` precisa respeitar essa possibilidade. [R24.3](https://doc.rust-lang.org/std/mem/fn.forget.html).

A representação privada do starter pode mudar, desde que preserve as assinaturas, os lifetimes, os auto traits exigidos e o comportamento observável. A célula pode ser `Send` pelos auto traits dos campos; se for, `T: Send` deve ser condição necessária.

## Exemplo

Com uma célula livre, dois pedidos de leitura devem ter sucesso. Enquanto os dois guards existirem, `try_borrow_mut()` deve retornar `ReadersActive`. Depois do drop dos dois guards, um pedido exclusivo deve ter sucesso. Enquanto esse escritor existir, `try_borrow()` deve retornar `WriterActive`.

## Requisitos

- **Artefato obrigatório:** biblioteca, guards, testes funcionais e de compilação e evidências de Miri.
- **Justificativa técnica obrigatória:** máquina de estados, comentários `SAFETY` e auditoria da fronteira segura que identifique qual invariante autoriza cada conversão do ponteiro interno em referência. Explique os lifetimes, os auto traits, o limite do contador, a segurança durante unwind e a política para guards esquecidos.
- **Explorações opcionais:** comparações com `RefCell`, seus guards e `Mutex`, conforme a seção Extensões opcionais, se realizadas.

### Roteiro de desenvolvimento

1. Modele cada transição e seu erro antes de manipular `UnsafeCell`.
2. Implemente a aquisição de permissões e os guards, vinculando a emissão de cada referência à aquisição bem-sucedida da permissão.
3. Escreva clientes que tentem guardar uma referência além do guard; confirme a rejeição estática.
4. Exercite o limite de leitores, os conflitos, as saídas normais, as saídas antecipadas, panic durante uso e guards esquecidos.
5. Revise lifetimes, auto traits e comentários `SAFETY`; execute os testes funcionais e de compilação e reúna as evidências de Miri, verificando as invariantes de cada acesso e descarte.

### Materiais fornecidos

Consulte a [preparação dos materiais](materials/README.md). O clube fornece os apoios e o harness descritos; o participante implementa o núcleo e justifica suas invariantes.

## Casos de teste

Dois leitores devem coexistir e observar o mesmo valor; escritor deve modificar o valor e liberar a célula ao sair de escopo. Teste leitor → escritor, escritor → leitor e escritor → escritor, conferindo os erros exatos e posterior recuperação. Mantenha 255 leitores vivos, confirme a recusa seguinte, descarte um e confirme uma nova aquisição.

Uma saída antecipada e um unwind controlado durante o uso devem liberar o borrow quando o guard é destruído. Esquecer um leitor deve manter a escrita bloqueada; esquecer um escritor deve bloquear ambos os métodos, sem fabricar referências inválidas. Casos `compile_fail` devem cobrir referência sobrevivendo ao guard e tentativa de compartilhar a célula entre threads. O drop normal de `T` deve ocorrer uma vez.

Estes casos especificam a verificação exigida. A suíte pública está em `tests/`; consulte os comandos no guia local. Nos testes de compilação, confirme que cada cliente inválido falha pelo motivo esperado; um erro de sintaxe ou importação não comprova a propriedade. Essa regra se aplica quando houver testes de compilação no núcleo.

## Extensões opcionais

As atividades desta seção são opcionais e não compõem os critérios de correção.

- Compare sua interface com as variantes falíveis de `RefCell` e com as variantes que fazem panic. [R24.2](https://doc.rust-lang.org/std/cell/struct.RefCell.html).
- Leia os guards reais em `core/cell.rs` e identifique como estado e lifetime se complementam; examine os testes do contador e o descarte de `BorrowRef` e `BorrowRefMut`. [R24.4](https://doc.rust-lang.org/src/core/cell.rs.html).
- Compare conceitualmente a função de `Mutex` com a da célula, sem acrescentar sincronização entre threads ao núcleo.

Lifetimes corretos, overflow, leak safety, auto traits e a análise das invariantes da própria solução permanecem obrigatórios.

Wrappers que fazem panic, projeção de guards e recuperação de borrows esquecidos são extensões opcionais e exigem novos contratos. Overflow, lifetimes corretos e leak safety pertencem ao núcleo; sincronização entre threads fica fora dele.

## Como participar

Desenvolva a solução em seu próprio repositório. Compartilhe código, ambiente, resultados e justificativa técnica na conversa do clube. Você pode apresentar uma tentativa incompleta; descreva o requisito ainda não atendido e um caso pequeno que permita reproduzir a dúvida.

Organize a memória técnica por contrato, decisões e invariantes, falhas e recursos, verificação, ambiente e limitações. Não há limite de páginas neste pacote.

### Referências orientadas

- **R24.1 — [`UnsafeCell`](https://doc.rust-lang.org/std/cell/struct.UnsafeCell.html).** Ler regras de aliasing e a distinção entre interior mutability e exclusividade.
- **R24.2 — [`RefCell`](https://doc.rust-lang.org/std/cell/struct.RefCell.html).** Comparar `try_borrow`, `try_borrow_mut` e as variantes que fazem panic.
- **R24.3 — [`mem::forget`](https://doc.rust-lang.org/std/mem/fn.forget.html).** Ler a seção Safety e explicar por que `Drop` não pode ser pressuposto.
- **R24.4 — [Código real: `core/cell.rs`](https://doc.rust-lang.org/src/core/cell.rs.html).** Localizar `BorrowRef::new`, seus testes de contador e `Drop`, depois `BorrowRefMut`; a standard library tem recursos e representação além do núcleo proposto.

As referências do caderno foram preservadas. Consulte as revisões fixadas e o status de consulta em [references.md](references.md). A leitura de código real é complementar; a documentação necessária para interpretar o contrato continua indicada nas seções correspondentes.
