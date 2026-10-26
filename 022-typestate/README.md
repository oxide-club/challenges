# 022-typestate — guia local

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

`src/support.rs` fornece `FaultPlan { open, write, finalize }`. Cada `true` permite uma falha; `take_*` consome somente o respectivo gatilho. `TransitionError` tem campos públicos `reason` e `resource`; o motivo é `TransitionReason::Injected`. Não exponha os campos de `Resource`; sua representação privada pode mudar. A suíte não verifica exaustivamente campos e construtores adicionais: a auditoria manual de encapsulamento é obrigatória. A fixture `materials/bytes.bin` contém exatamente os quatro bytes ASCII `abcd`, sem newline.

## Verificar

A suíte consulta a API pública. Valores esperados foram derivados manualmente do enunciado: bytes literais, capacidade de 4.096 bytes e gatilhos de falha. Consulte [materiais](materials/README.md).

A referência reservada passou os checks funcionais e os clientes de compilação aplicáveis. Os cinco mutantes funcionais originais e um mutante adicional da revisão foram rejeitados em cada pacote. Os controles de compilação usam clientes válidos equivalentes; erros de importação ou sintaxe não contam como detecção. Esses registros são históricos. Os resultados abrangem os controles executados; o starter continua incompleto. A revisão de invariantes das soluções dos participantes continua necessária. O piloto não foi executado e foi dispensado pelo responsável.

## Entrega

Complete [report-template.md](report-template.md) e entregue os artefatos da seção Requisitos do enunciado. Não altere os casos para fazer o starter passar. As extensões são opcionais e as estimativas continuam sujeitas ao piloto.

## Licenças e origem

Documentação original: CC BY 4.0. Código original: MIT. Fixtures e valores literais originais: CC0 1.0. Origem: contrato curricular do clube, preparação de 25/10/2026, revisão `rust-libraries-v1`. Não foram copiados trechos de implementações externas. Consulte [references.md](references.md) para fontes, revisões e limites de consulta.
