---
title: "Biblioteca Rust com interface C"
slug: "025-rust-c-ffi"
area: systems-fundamentals
summary: "Integre C e Rust com ABI, buffers, ownership e política de panic explicitamente definidos."
publishedAt: "2026-10-25"
updatedAt: "2026-10-25"
draft: false
difficulty: "advanced"
categories: ["build"]
participation: "open"
recommendedLanguage: "Rust"
acceptedLanguages: ["Rust", "C"]
cardTopics: ["FFI", "ABI", "Ownership"]
topics: ["FFI", "ABI", "Ownership"]
featured: false
environment: "Linux x86-64; Rust e C obrigatórios; compilador C e ferramentas ELF"
---

**Dificuldade:** Avançado
**Linguagem recomendada:** Rust
**Linguagens aceitas:** Rust, C
**Conceitos:** FFI, ABI, ownership
**Ambiente:** Linux x86-64; Rust e C obrigatórios; compilador C e ferramentas ELF

Os materiais estão disponíveis no [guia local](README.md). O núcleo do starter permanece incompleto para implementação pelo participante. Consulte os requisitos e as limitações de ambiente antes de começar.

## O desafio

Crie uma biblioteca que mantém uma chave de um byte em um contexto Rust. Um cliente C cria o contexto, envia bytes, recebe bytes transformados e o destrói. A transformação de cada byte é `rotate_left(src[i] ^ key, 1)`, sendo a rotação implementada por um helper C e invocada pelo lado Rust. A operação é didática e não deve ser descrita como criptografia.

A solução será aceita quando integrar cliente C → Rust → helper C e cumprir o contrato de ABI, layout, ownership, validade de buffers e falhas abaixo. O cabeçalho e a documentação devem tornar explícitas as pré-condições que a implementação não pode verificar; os testes e a inspeção de layout e símbolos devem sustentar a correção dessa interface.

### Por que construir esta solução

Tipos parecidos não garantem uma fronteira binária correta. Além da calling convention, uma interface precisa dizer quais ponteiros continuam válidos, quem libera cada alocação e como um erro atravessa a fronteira. Declarações `extern` não verificam essas obrigações pelo programador. [R25.1](https://doc.rust-lang.org/1.98.1/nomicon/ffi.html).

Uma transformação simples de bytes permite observar essas decisões sem acrescentar um algoritmo difícil. O contexto será opaco para C; o resultado terá layout público. Essa diferença separa representação privada de um objeto e representação contratada de uma mensagem.

### Antes de começar

C com structs, ponteiros, arrays e cabeçalhos; Rust com ownership, slices, `Result` e `unsafe`; compilação separada, bibliotecas estáticas e linking. Conhecimento introdutório de ABI, alinhamento e símbolos ELF é necessário. Os laboratórios [de ABI](https://oxideclub.dev/labs/012-abi-lab/) e [de linking](https://oxideclub.dev/labs/014-dynamic-linking-lab/), além do desafio [023-mini-vec](../023-mini-vec/index.md), são preparações recomendadas.

### Objetivos de aprendizagem

- Exportar funções Rust com ABI C e chamá-las de um cliente C.
- Declarar e invocar corretamente uma função C a partir de Rust.
- Conferir tamanho, alinhamento e offsets de uma estrutura compartilhada.
- Especificar validade, lifetime, aliasing e responsabilidade por liberação em cada parâmetro.
- Traduzir erros recuperáveis e delimitar o tratamento de panic sem prometer validação de ponteiros arbitrários.

### Conceitos trabalhados

FFI; ABI C; `repr(C)`; tipos opacos; ownership através da fronteira; contratos de buffers; símbolos exportados; erros por status; unwind safety; limites da validação dinâmica.

## Especificação

A interface pública será:

- `int32_t oc_create(uint8_t key, OcContext **out);`
- `void oc_destroy(OcContext *ctx);`
- `OcResult oc_transform(OcContext *ctx, const uint8_t *src, size_t src_len, uint8_t *dst, size_t dst_cap);`

`OcContext` é incompleto no cabeçalho C. `OcResult` contém, nesta ordem, `int32_t status`, `size_t written` e `size_t required`; sua contraparte Rust usa `#[repr(C)]`. Status são `0 = Ok`, `1 = InvalidArgument`, `2 = BufferTooSmall`, `3 = InternalPanic` e `4 = Poisoned`. Não passe `Vec`, referências Rust, `String`, enums sem representação contratada ou trait objects pela ABI. `repr(C)` define regras de layout, sem validar ponteiros ou estabelecer ownership. [R25.2](https://doc.rust-lang.org/1.98.1/reference/type-layout.html).

As funções Rust expostas com essas pré-condições de ponteiro devem ser `unsafe extern "C"`; uma API Rust pública segura não pode exigir que o chamador adivinhe obrigações de memória não verificadas.

`oc_create` retorna `InvalidArgument` para `out == NULL`. Para `out` não nulo, o chamador garante um slot válido, alinhado e gravável; a função começa deixando-o nulo e só publica o handle no sucesso. Um unwind interno capturado em criação retorna `InternalPanic`, mantém `*out == NULL` e não deixa contexto publicado para envenenar. O contexto é alocado e liberado pelo lado Rust, exclusivamente por `oc_destroy`, que não panica com argumentos válidos. `oc_destroy(NULL)` não faz nada. Handle falso, expirado ou destruído duas vezes viola a pré-condição; não se promete detectar esses casos.

Em `oc_transform`, `ctx == NULL` retorna `InvalidArgument` antes de consultar o estado do contexto. Um contexto não nulo deve estar vivo e as chamadas sobre ele, serializadas. `src == NULL` só é permitido quando `src_len == 0`; `dst == NULL`, quando `dst_cap == 0`. Comprimentos acima de `isize::MAX` são rejeitados. As pré-condições de extensão das regiões aplicam-se somente aos comprimentos dentro dos limites escalares. Para argumentos escalares rejeitados, a função não acessa `src`/`dst` nem forma slices. O contexto não nulo ainda deve estar vivo. Regiões não vazias precisam pertencer a alocações vivas: origem legível com bytes inicializados, destino gravável, sem sobreposição entre si ou com o contexto. Nenhuma referência será retida depois do retorno. Essas condições são responsabilidade do chamador; checar nulidade não demonstra validade de memória.

**Esclarecimento aprovado em 25/10/2026:** a regra anterior não explicitava a relação entre limites escalares e extensão das regiões. O responsável aprovou a redação acima no registro público da aprovação 07 (registro histórico retirado deste repositório). Ela permite testar `PTRDIFF_MAX + 1` sem exigir uma alocação impossível; não permite handles falsos ou expirados.

A validação de nulidade e limites escalares precede a consulta ao estado envenenado; a capacidade vem depois. Se `dst_cap < src_len`, retorna `BufferTooSmall`, com `written = 0`, `required = src_len` e destino intacto. No sucesso, `written = required = src_len`; o restante do destino fica intacto. Entrada vazia produz sucesso com comprimentos zero. Em outros erros, ambos os comprimentos retornam zero. `InvalidArgument` e `Poisoned` não escrevem bytes; após `InternalPanic`, os bytes do destino podem ter sido parcialmente alterados e não devem ser interpretados como resultado.

A ABI é `extern "C"`, sem unwind atravessando a fronteira. O perfil de integração usa `panic=unwind`. O gancho de injeção existe somente em `oc_transform`: seu panic é capturado como `InternalPanic`, e esse contexto fica envenenado, admitindo apenas destruição. `catch_unwind` não captura abort, OOM que aborta, sinais, UB ou toda exceção estrangeira; descartar seu payload também merece cuidado. O helper C não lança exceções nem usa `longjmp`. [R25.3](https://doc.rust-lang.org/1.98.1/std/panic/fn.catch_unwind.html).

## Exemplo

Com contexto válido, chave zero e capacidade de destino igual a quatro:

```text
entrada: 00 01 80 ff
saída:  00 02 01 ff
status:  0
written: 4
required: 4
```

Os valores são bytes em hexadecimal. Com capacidade três, o resultado deve ser `BufferTooSmall`, `written = 0` e `required = 4`, sem alterar o destino.

## Requisitos

- **Artefato obrigatório:** biblioteca, helper e cabeçalho contratual completos; comandos e resultados dos clientes C/Rust fornecidos, testes de integração e inspeção `nm`/`readelf`.
- **Justificativa técnica obrigatória:** tabela de ownership e erros, documentação de validade, lifetime, aliasing e liberação em cada parâmetro e explicação da política de panic e envenenamento. Diferencie erro de entrada reconhecido de violação de pré-condição da ABI; justifique as conversões e chamadas `unsafe` necessárias à fronteira.
- **Explorações opcionais:** comparação com a construção de uma visão vinculada ao lifetime dos dados de origem em `CStr::from_ptr`, conforme a seção Extensões opcionais, se realizada.

### Roteiro de desenvolvimento

1. Anote ownership, validade, lifetime, aliasing e responsabilidade por liberação de cada ponteiro no cabeçalho.
2. Defina as representações compartilhadas e confira `sizeof`, alinhamento e offsets de `OcResult` nos dois lados.
3. Complete a biblioteca e o helper; execute os clientes fornecidos para integrar C → Rust → C; examine os símbolos presentes após o linking.
4. Exercite erros detectáveis, precedência das validações, limites de buffers e a política de contexto envenenado.
5. Revise todos os caminhos de criação, transformação e destruição, o tratamento de panic e a documentação das pré-condições; confira se nenhum unwind atravessa a fronteira e se a suíte respeita os limites de validade dos argumentos.

### Materiais fornecidos

Consulte os [materiais fornecidos](materials/README.md). O guia distingue os apoios do clube das implementações do participante.

## Casos de teste

Com chave zero, `[0x00, 0x01, 0x80, 0xFF]` deve resultar em `[0x00, 0x02, 0x01, 0xFF]`. Teste chave não zero, bytes NUL internos, entrada vazia com buffers nulos e contexto válido, capacidade exata e capacidade insuficiente com sentinelas preservadas. Contexto nulo e buffer nulo com comprimento positivo devem retornar `InvalidArgument` sem dereference. Teste criação, destruição única, `destroy(NULL)`, panic controlado e recusa posterior por `Poisoned`.

A suíte não deve fabricar dangling pointers ou aleatórios e esperar um status seguro. Inspeção de layout e símbolos deve concordar com o cabeçalho; endereços absolutos não são critérios de aprovação.

Estes casos especificam a verificação exigida. A suíte pública está descrita no guia local; ela não substitui a revisão das invariantes.

## Extensões opcionais

A atividade desta seção é opcional e não compõe os critérios de correção.

Leia a passagem de raw pointer para referência em `CStr::from_ptr`, identificando exigências que a implementação não consegue comprovar sozinha. Compare os requisitos de uma string terminada em NUL com os de buffers de comprimento explícito. [R25.4](https://doc.rust-lang.org/1.98.1/src/core/ffi/c_str.rs.html).

A documentação das pré-condições da própria ABI e os argumentos de validade, lifetime, ownership e segurança das operações `unsafe` continuam obrigatórios.

Strings UTF-8/C, callbacks, bibliotecas compartilhadas e handles generacionais são extensões. Uma API realmente tolerante a handles arbitrários exige outro desenho. `catch_unwind` não transforma FFI insegura em sandbox.

## Como participar

Desenvolva a solução em seu próprio repositório. Compartilhe código, ambiente, resultados e justificativa técnica na conversa do clube. Você pode apresentar uma tentativa incompleta; descreva o requisito ainda não atendido e um caso pequeno que permita reproduzir a dúvida.

Organize a memória técnica por contrato, decisões e invariantes, falhas e recursos, verificação, ambiente e limitações. Não há limite de páginas definido para esta atividade.

### Referências orientadas

- **R25.1 — [Rustonomicon: FFI](https://doc.rust-lang.org/1.98.1/nomicon/ffi.html).** Ler ponteiros, tipos opacos e fronteiras de unwind.
- **R25.2 — [Rust Reference: Type layout](https://doc.rust-lang.org/1.98.1/reference/type-layout.html).** Consultar representação C, padding e alinhamento.
- **R25.3 — [`catch_unwind`](https://doc.rust-lang.org/1.98.1/std/panic/fn.catch_unwind.html).** Ler Notes e distinguir retorno de erro de término do processo.
- **R25.4 — [Código real: `core/ffi/c_str.rs`](https://doc.rust-lang.org/1.98.1/src/core/ffi/c_str.rs.html).** Localizar `CStr::from_ptr`, seu bloco Safety e a construção da visão vinculada ao lifetime dos dados de origem; comparar os requisitos de uma string terminada em NUL com buffers de comprimento explícito.

As referências Rust abaixo usam a edição 1.98.1. O estado da proveniência externa está no guia local. A leitura de código real é complementar; a documentação necessária para interpretar o contrato continua indicada nas seções correspondentes.
