# Materiais — 022-typestate

**Situação:** pacote tecnicamente validado; saída de rascunho autorizada pelo responsável, com dispensa do piloto.

O clube fornece `Cargo.toml`, assinaturas em `src/lib.rs`, apoios descritos abaixo, suíte pública `tests/contract.rs`, pares em `tests/ui/`, runner `tests/compile.py`, entrada `tests/check.py`, roteiro de execução e modelo de memória técnica. O participante implementa os corpos identificados por `participant:` e justifica as invariantes; não precisa construir o harness.

`src/support.rs` fornece `FaultPlan { open, write, finalize }`. Cada `true` permite uma falha; `take_*` consome somente o respectivo gatilho. `TransitionError` tem campos públicos `reason` e `resource`; o motivo é `TransitionReason::Injected`. Não exponha os campos de `Resource`. A fixture `materials/bytes.bin` contém exatamente os quatro bytes ASCII `abcd`, sem newline.

Os campos privados podem mudar de nome ou usar tuple struct. O par `private_representation` tenta reconstruir o mesmo estado por struct update, sem nomear campos; detecta a exposição de todos os campos tanto em struct nomeada quanto em tuple struct. Ele não detecta toda exposição parcial. O par `closed_as_open` verifica a distinção estática entre os estados, sem depender de campos privados. A suíte não inspeciona todos os campos e construtores possíveis: revise manualmente que nenhum campo de `Resource` nem construtor de estado intermediário está público. O relatório deve registrar essa auditoria. Os pares de clonagem cobrem `Closed`, `Open` e `Finalized`; `finalized_open` cobre a ausência de reabertura.

## Oráculo e controles

Os resultados esperados constam como literais nas fixtures públicas, calculados diretamente pelas regras do enunciado. Não são gerados pela implementação candidata. A validação inicial da referência e dos controles negativos foi executada separadamente. A distribuição não contém referências nem mutantes.

A preparação aprovada significa build e controles de interface disponíveis. O núcleo do starter falha intencionalmente. Após implementar, o participante deve obter aprovação funcional e justificar os limites das observações. Os comandos estão no [guia local](../README.md).

## Origem e licenças

Contrato: atividade 21 do caderno `Oxide_Club_Desafios_e_Laboratorios_Rust_Seguranca_Terminologia_Revisada_2026-10-25.md`; redação conforme PTC 1.1. Materiais originais da preparação `rust-libraries-v1`, 25/10/2026. Documentação CC BY 4.0; código MIT; fixtures/valores esperados CC0 1.0. Fontes externas são links de leitura e conservam suas próprias licenças; nenhum código externo foi incorporado.
