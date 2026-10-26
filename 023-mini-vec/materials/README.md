# Materiais — 023-mini-vec

**Situação:** pacote tecnicamente validado; saída de rascunho autorizada pelo responsável, com dispensa do piloto.

O clube fornece `Cargo.toml`, assinaturas em `src/lib.rs`, apoios descritos abaixo, suíte pública `tests/contract.rs`, pares em `tests/ui/`, runner `tests/compile.py`, entrada `tests/check.py`, roteiro de execução e modelo de memória técnica. O participante implementa os corpos identificados por `participant:` e justifica as invariantes; não precisa construir o harness.

`src/support.rs` fornece `Allocator`, compartilhável por `clone`. `fail_next()` recusa a próxima tentativa de alocação. `stats()` devolve `(tentativas, alocações bem-sucedidas, liberações)`. `with_allocator` permite injetá-lo; `new` usa o padrão. O adaptador aloca memória real. Use `allocate(Layout)` somente com tamanho não zero; `deallocate` exige ponteiro vivo e o layout original. Não substitua o adaptador.

Implemente também `layout_for::<T>(capacity)`, cálculo puro que retorna `Layout` ou `CapacityOverflow`. A suíte passa `usize::MAX` sem forjar estado nem ponteiros. `PushError` devolve `reason` e o próprio `value`. Os spies em `tests/support/mod.rs` mantêm um borrow do log externo; `DropBomb` não possui alocações. Por isso, um double drop pode não produzir diagnóstico de UB no Miri; o teste também limita a contagem de cada id a uma ocorrência. A observação aceita a omissão de drops pendentes após panic, mas exige liberação do buffer. O teste inclui as quatro posições da bomba num vetor de quatro elementos e observa `stats()` após esvaziamento completo por `pop`. A conferência dinâmica do layout de liberação depende do Miri; o adaptador registra contagens, não os layouts.

`tests/zst_allocation.rs` observa o allocator global numa integração isolada. A rejeição de ZST deve ocorrer antes de qualquer alocação, inclusive a criação do adaptador baseado em `Rc`. Revise também a delegação inicial de `new`; ela não constitui uma implementação concluída. O script Miri executa esse teste além de `contract`.

## Oráculo e controles

Os resultados esperados constam como literais nas fixtures públicas, calculados diretamente pelas regras do enunciado. Não são gerados pela implementação candidata. A validação inicial da referência e dos controles negativos foi executada separadamente. A distribuição não contém referências nem mutantes.

A preparação aprovada significa build e controles de interface disponíveis. O núcleo do starter falha intencionalmente. Após implementar, o participante deve obter aprovação funcional e justificar os limites das observações. Os comandos estão no [guia local](../README.md).

## Origem e licenças

Contrato: atividade 22 do caderno `Oxide_Club_Desafios_e_Laboratorios_Rust_Seguranca_Terminologia_Revisada_2026-10-25.md`; redação conforme PTC 1.1. Materiais originais da preparação `rust-libraries-v1`, 25/10/2026. Documentação CC BY 4.0; código MIT; fixtures/valores esperados CC0 1.0. Fontes externas são links de leitura e conservam suas próprias licenças; nenhum código externo foi incorporado.
