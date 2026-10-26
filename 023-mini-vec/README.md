# 023-mini-vec — guia local

Leia a [definição](index.md). O pacote inicial compila; o núcleo em `src/lib.rs` contém `todo!` intencionais. **Pacote tecnicamente validado; saída de rascunho autorizada pelo responsável.** Não há solução distribuída.

## Ambiente e linguagens

Validado em Linux x86_64, target `x86_64-unknown-linux-gnu`, Rust/Cargo 1.98.1, edição 2021, Python 3. Sem crates externas. Build padrão debug, panic por unwind, sem flags adicionais. Registre `rustc -Vv`, `cargo -V` e `python3 --version`. A validação usou Python 3.14.8 e a toolchain selecionada diretamente em `PATH`; consulte a nota sobre o proxy rustup nas evidências.

## Preparar e executar

Copie este diretório para seu repositório e execute os comandos a partir da cópia:

```sh
cargo check --offline
python3 tests/check.py --prepare
cargo test --offline
python3 tests/compile.py
python3 tests/check.py
```

Os dois primeiros comandos devem terminar com status 0 antes da implementação. `--prepare` compila biblioteca e testes e verifica pares de clientes, mas **não aceita o núcleo**. `cargo test` e o check completo falham intencionalmente por `participant:` até completar `src/lib.rs`. Nenhum teste funcional está ignorado. `tests/compile.py` compila o controle válido antes do inválido e confere códigos de diagnóstico; ele não executa clientes inválidos. Bibliotecas não precisam de uma CLI artificial para o runner de programas.

Implemente o núcleo, preserve as assinaturas públicas e execute novamente os checks. O wrapper retorna 0 para aprovação, 1 para falha e 77 para ferramenta ausente. `cargo test` direto retorna 101 quando um teste falha.

## Interface auxiliar

`src/support.rs` fornece `Allocator`, compartilhável por `clone`. `fail_next()` recusa a próxima tentativa de alocação. `stats()` devolve `(tentativas, alocações bem-sucedidas, liberações)`. `with_allocator` permite injetá-lo; `new` usa o padrão. O adaptador aloca memória real. Use `allocate(Layout)` somente com tamanho não zero; `deallocate` exige ponteiro vivo e o layout original. Não substitua o adaptador.

Implemente também `layout_for::<T>(capacity)`, cálculo puro que retorna `Layout` ou `CapacityOverflow`. A suíte passa `usize::MAX` sem forjar estado nem ponteiros. `PushError` devolve `reason` e o próprio `value`. Os spies em `tests/support/mod.rs` mantêm um borrow do log externo; `DropBomb` não possui alocações. Por isso, um double drop pode não produzir diagnóstico de UB no Miri; o teste também limita a contagem de cada id a uma ocorrência. A observação aceita a omissão de drops pendentes após panic, mas exige liberação do buffer. A suíte varia a bomba pelas quatro posições de um vetor e confere também a liberação após remover todos os elementos por `pop`.

## Verificar

A suíte consulta a API pública. Valores esperados foram derivados manualmente do enunciado: capacidades 0/1/2/4/8, layouts, erros de alocação e sequências de drops. Consulte [materiais](materials/README.md).

A referência reservada passou os checks funcionais e os clientes de compilação aplicáveis. Os cinco mutantes funcionais originais e um mutante adicional da revisão foram rejeitados em cada pacote. Os controles de compilação usam clientes válidos equivalentes; erros de importação ou sintaxe não contam como detecção. Esses registros são históricos. Os resultados abrangem os controles executados; o starter continua incompleto. A revisão de invariantes das soluções dos participantes continua necessária. O piloto não foi executado e foi dispensado pelo responsável.

Miri foi executado na referência com o canal instalado `nightly` de 24/10/2026 (o canal datado `nightly-2026-10-25` não foi validado), rustc `1.101.0-nightly`, commit `12433c307b5a497388ffe2f4e49dbf1ab8c71fa0`. Para repetir após implementar:

```sh
rustup toolchain install nightly --component miri,rust-src
cargo +nightly miri setup
MIRI_TOOLCHAIN=nightly sh tests/miri.sh
```

`MIRI_TOOLCHAIN` seleciona o canal. Para usar os binários diretamente, coloque a pasta `bin` da toolchain no `PATH` e defina `RUSTUP_TOOLCHAIN=nightly MIRI_DIRECT=1`. Registre as versões: o canal móvel pode mudar.

O script retorna 77 se Miri não estiver disponível; isso não equivale a aprovação. O recorte é `--test contract --test zst_allocation`, com detecção padrão de leaks habilitada. `support_contract` não passa pelo Miri. Miri não executa o harness Python/rustc nem os pares de compilação. Nenhuma variável `MIRIFLAGS` foi usada na validação. Testes de unwind e de liberação do buffer pertencem ao núcleo. Miri examina estas execuções, sem substituir a auditoria de soundness. O adaptador conta liberações, mas não registra o layout de cada alocação. A detecção dinâmica de liberação com layout incorreto depende do Miri; um check nativo aprovado não demonstra essa propriedade.

## Entrega

Complete [report-template.md](report-template.md) e entregue os artefatos da seção Requisitos do enunciado. Não altere os casos para fazer o starter passar. As extensões são opcionais e as estimativas continuam sujeitas ao piloto.

## Licenças e origem

Documentação original: CC BY 4.0. Código original: MIT. Fixtures e valores literais originais: CC0 1.0. Origem: contrato curricular do clube, preparação de 25/10/2026, revisão `rust-libraries-v1`. Não foram copiados trechos de implementações externas. Consulte [references.md](references.md) para fontes, revisões e limites de consulta.
