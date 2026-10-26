---
title: "Recurso com estados verificados por tipos"
slug: "022-typestate"
area: memory
summary: "Construa uma API com typestate, transições recuperáveis e rejeição estática de operações inválidas."
publishedAt: "2026-10-25"
updatedAt: "2026-10-25"
draft: false
difficulty: "intermediate"
categories: ["build"]
participation: "open"
recommendedLanguage: "Rust"
acceptedLanguages: ["Rust"]
cardTopics: ["Typestate", "Ownership", "APIs"]
topics: ["Typestate", "Ownership", "APIs"]
featured: false
environment: "Rust estável, Cargo e rustdoc; execução local sem serviços externos"
---

**Dificuldade:** Intermediário\
**Linguagem recomendada:** Rust\
**Linguagens aceitas:** Rust\
**Conceitos:** Typestate, Ownership e APIs\
**Ambiente:** Rust estável, Cargo e rustdoc; execução local sem serviços externos

Os materiais estão disponíveis no [guia local](README.md). O núcleo do starter permanece incompleto para implementação pelo participante. Consulte os requisitos e as limitações de ambiente antes de começar.

## O desafio

Construa `Resource<State>` para acumular bytes e permitir sua leitura somente depois da finalização. A solução deve expressar na interface quais operações são válidas em cada estado e devolver ao chamador um recurso utilizável quando uma transição falhar. Implemente o núcleo sem `unsafe` e sem substituir a restrição de tipos por uma flag consultada em todos os métodos.

A solução será aceita quando cumprir o contrato abaixo, incluindo conteúdo, capacidade, precedência de erros, recuperação após falhas e rejeição estática dos clientes inválidos. Uma tentativa malsucedida não pode destruir silenciosamente os dados nem retirar a possibilidade de tentar novamente. A tabela de transições e a justificativa do encapsulamento integram a demonstração de correção.

### Por que construir esta solução

Abrir, escrever e finalizar parecem ações simples, mas formam um protocolo: algumas sequências são válidas e outras precisam ser impedidas. Neste desafio, estados deixam de ser apenas valores consultados em runtime e passam a limitar os métodos disponíveis. Generics e ownership permitem expressar parte desse protocolo na interface; `PhantomData` representa uma relação de tipos sem armazenar uma instância do marcador. Ele também participa de propriedades de segurança, portanto sua escolha precisa ser explicada. [R21.1](https://github.com/rust-lang/book/blob/05d114287b7d6f6c9253d5242540f00fbd6172ab/src/ch10-00-generics.md), [R21.2](https://github.com/rust-lang/rust/blob/48a229ceaefd4985c50990b14116b6d856af0985/library/core/src/marker.rs#L676).

O interesse está em separar duas perguntas: “esta operação faz sentido neste estado?” e “esta operação válida conseguiu terminar?”. A primeira será respondida por tipos; a segunda, por erros recuperáveis. O recurso é um buffer em memória com I/O simulado, para concentrar o problema no protocolo.

### Antes de começar

É preciso ler e escrever `struct`, `enum`, `impl`, generics, `Result`, métodos com `self`, `&self` e `&mut self`; compreender moves e privacidade de módulos; e executar testes Cargo. Conhecer arquivos reais, `unsafe`, lifetimes explícitos ou async não é necessário. Atividades anteriores de segurança de memória ajudam, mas nenhuma atividade numerada é requisito de ingresso.

### Objetivos de aprendizagem

- Representar os estados `Closed`, `Open` e `Finalized` e identificar os métodos admitidos em cada um.
- Projetar transições que consomem ownership e devolvem um recurso utilizável quando falham.
- Demonstrar rejeições estáticas por indisponibilidade de método ou uso de valor movido.
- Verificar separadamente conteúdo, falhas de operação e limites de capacidade.
- Explicar quais garantias desaparecem se campos, construtores ou operações de clonagem forem expostos inadequadamente.

### Conceitos trabalhados

Typestate; invariantes de representação; encapsulamento; consumo e recuperação de ownership; distinção entre erro estático e dinâmico; documentação de APIs; testes de compilação e correspondência entre estado lógico e representação.

## Especificação

`Resource<Closed>::new(plan)` cria um recurso vazio. `open(self)` retorna `Result<Resource<Open>, TransitionError<Closed>>`; `finalize(self)` só existe em `Resource<Open>` e retorna `Result<Resource<Finalized>, TransitionError<Open>>`. `TransitionError<S>` contém o motivo e o próprio `Resource<S>`, recuperável pelo chamador. Uma falha consome apenas o gatilho de injeção daquela tentativa, preservando os bytes; a próxima tentativa poderá avançar.

`write(&mut self, bytes: &[u8]) -> Result<(), WriteError>` só existe em `Open`. A capacidade lógica máxima é 4.096 bytes. Uma escrita acrescenta todos os bytes em ordem ou nenhum; ultrapassar o limite retorna `CapacityExceeded`. A verificação do limite precede a falha `Injected`, sem consumir seu gatilho. Escrita vazia retorna sucesso e não consome falha. O cálculo de tamanho precisa evitar overflow.

`bytes(&self) -> &[u8]` só existe em `Finalized`. Finalizar vazio é válido; finalizar não acrescenta bytes. Não há reabertura, `Clone` ou `Copy` de recursos. Campos e construtores de estados intermediários permanecem privados. O drop de um recurso aberto abandona os bytes: não existe promessa de persistência nem finalização automática. A API deve impossibilitar escrita antes da abertura, escrita após finalização e segunda finalização da mesma instância.

O starter fornece marcadores de estado, `PhantomData` e blocos `impl`. O participante completa os corpos e justifica essa organização; pode alterar a representação privada preservando as assinaturas e o contrato. A revisão humana deve conferir privacidade de campos e ausência de construtores públicos para estados intermediários, pois os clientes distribuídos não enumeram todas as formas de quebrar o encapsulamento.

## Exemplo

O fluxo abaixo descreve um resultado exigido pelo contrato, sem pressupor uma sintaxe para `FaultPlan`:

```text
novo → abrir → escrever ab → escrever cd → finalizar → consultar bytes
resultado: abcd
```

Se a finalização injetar uma falha, recupere o recurso aberto no erro e repita a tentativa. Os bytes devem continuar sendo `abcd`.

## Requisitos

- **Artefato obrigatório:** biblioteca documentada, clientes mínimos e testes funcionais e de compilação, com toolchain e comandos utilizados.
- **Justificativa técnica obrigatória:** tabela de transições e relatório curto que relacione cada rejeição à garantia pretendida, explique a escolha dos marcadores de estado e mostre como encapsulamento, ownership e recuperação de erros preservam o contrato.
- **Explorações opcionais:** registros das comparações propostas na seção Extensões opcionais, se realizadas.

Uma implementação alternativa baseada exclusivamente em checagens dinâmicas não satisfaz o núcleo.

### Roteiro de desenvolvimento

1. Faça uma tabela de estado, método, tipo de retorno e efeito de falha. Marque quais propriedades dependem do compilador.
2. Examine os clientes válidos e inválidos fornecidos antes de implementar as transições; registre a propriedade verificada por cada par e acrescente casos para decisões próprias da interface.
3. Projete e implemente a recuperação do recurso em `Err`; verifique se o chamador consegue repetir a operação sem duplicar dados.
4. Teste capacidade e injeção combinadas, explicando a precedência contratada.
5. Revise privacidade, marcadores de estado e consumo de ownership; confira se a interface impede as sequências inválidas e documente as garantias e os limites do recurso.

### Materiais fornecidos

Consulte a [preparação dos materiais](materials/README.md). O clube fornece os apoios e o harness descritos; o participante implementa o núcleo e justifica suas invariantes.

## Casos de teste

O fluxo abrir → escrever `ab` → escrever `cd` → finalizar deve produzir `abcd`; finalizar sem escrever deve produzir vazio. Uma falha injetada em cada operação deve permitir recuperar ou reutilizar o recurso e repetir a tentativa sem bytes duplicados. Escrever 4.096 bytes deve funcionar; acrescentar outro byte deve falhar preservando o conteúdo. Escrita vazia não deve acionar a falha pendente.

Os clientes negativos devem tentar escrever em `Closed`, escrever em `Finalized`, finalizar duas vezes e reutilizar o valor consumido por `open`. A falha precisa ocorrer pelo contrato de tipos, sem depender de panic. Não se exige a mesma redação de diagnóstico entre versões do compilador.

Estes casos especificam a verificação exigida. A suíte pública está em `tests/`; consulte os comandos no guia local. Nos testes de compilação, confirme que cada cliente inválido falha pelo motivo esperado; um erro de sintaxe ou importação não comprova a propriedade. Essa regra se aplica quando houver testes de compilação no núcleo.

## Extensões opcionais

As atividades desta seção são opcionais e não compõem os critérios de correção.

- Leia a definição real de `PhantomData` e compare o papel do marcador com o conteúdo efetivamente armazenado. Localize suas implementações de traits e investigue como um marcador sem armazenamento pode afetar a análise do compilador. [R21.3](https://github.com/rust-lang/rust/blob/48a229ceaefd4985c50990b14116b6d856af0985/library/core/src/marker.rs#L811).
- Compare a interface com `enum` e validação dinâmica, identificando quais erros cada alternativa permite detectar antes da execução.

A justificativa dos marcadores e das invariantes usados na própria solução permanece obrigatória; a comparação com a implementação real é um aprofundamento.

Modelar um builder e acrescentar cancelamento explícito são extensões opcionais. Recursos reais, concorrência e garantias de persistência ficam fora do núcleo. Typestate não transforma falhas de I/O em impossibilidades estáticas.

## Como participar

Desenvolva a solução em seu próprio repositório. Compartilhe código, ambiente, resultados e justificativa técnica na conversa do clube. Você pode apresentar uma tentativa incompleta; descreva o requisito ainda não atendido e um caso pequeno que permita reproduzir a dúvida.

Organize a memória técnica por contrato, decisões e invariantes, falhas e recursos, verificação, ambiente e limitações. Não há limite de páginas neste pacote.

### Referências orientadas

- **R21.1 — [The Rust Programming Language: generics, traits e lifetimes](https://github.com/rust-lang/book/blob/05d114287b7d6f6c9253d5242540f00fbd6172ab/src/ch10-00-generics.md).** Revisar parâmetros de tipo; depois ler [métodos genéricos e específicos](https://github.com/rust-lang/book/blob/05d114287b7d6f6c9253d5242540f00fbd6172ab/src/ch10-01-syntax.md#in-method-definitions). Pergunta: por que um método de `impl Point<f32>` não existe para `Point<i32>`?
- **R21.2 — [`PhantomData`](https://github.com/rust-lang/rust/blob/48a229ceaefd4985c50990b14116b6d856af0985/library/core/src/marker.rs#L676).** Ler a documentação no fonte: parâmetros não armazenados, ownership e drop checking. Pergunta: que relação de tipos o marcador expressa sem armazenar um valor?
- **R21.3 — [Código real: `core/marker.rs`](https://github.com/rust-lang/rust/blob/48a229ceaefd4985c50990b14116b6d856af0985/library/core/src/marker.rs#L811).** Localizar `pub struct PhantomData` e suas implementações de traits; explicar por que um marcador sem armazenamento ainda pode afetar a análise do compilador. A biblioteca padrão não fornece a solução deste protocolo.

As referências do caderno foram preservadas. Consulte as revisões fixadas e o status de consulta em [references.md](references.md). A leitura de código real é complementar; a documentação necessária para interpretar o contrato continua indicada nas seções correspondentes.
