# Materiais — 024-mini-refcell

**Situação:** pacote tecnicamente validado; saída de rascunho autorizada pelo responsável, com dispensa do piloto.

O clube fornece `Cargo.toml`, assinaturas em `src/lib.rs`, apoios descritos abaixo, suíte pública `tests/contract.rs`, pares em `tests/ui/`, runner `tests/compile.py`, entrada `tests/check.py`, roteiro de execução e modelo de memória técnica. O participante implementa os corpos identificados por `participant:` e justifica as invariantes; não precisa construir o harness.

As assinaturas estão em `src/lib.rs`. `BorrowError` distingue `WriterActive`, `ReadersActive` e `ReaderLimitReached`. A representação inicial usa `UnsafeCell<T>` e `Cell<i16>`; o participante implementa aquisição, acesso e liberação. Os campos privados não podem ser acessados pelos clientes. Os guards contêm um borrow da célula: preserve seus lifetimes e os auto traits. O limite público continua sendo 255 leitores. O teste libera leitores um a um até o último, verificando que a escrita permanece bloqueada enquanto houver qualquer leitor.

Os testes verificam conflitos exatos, recuperação, limite, unwind, retorno antecipado, guard esquecido e drop único. Os pares de compilação cobrem lifetimes, `Clone`, `DerefMut` e `Send`/`Sync`. `MiniRefCell<T>: Send` continua opcional; a suíte não exige `Send` positivo e rejeita `Send` tanto para `MiniRefCell<Rc<i32>>` quanto para `MiniRefCell<MutexGuard<'static, i32>>`. O segundo conteúdo é `Sync` e `!Send`, distinguindo um bound incorreto `T: Sync`. Os controles positivos usam o mesmo tipo do negativo com um bound válido.

Os testes de compilação rejeitam `Clone` tanto para `MiniRef` quanto para `MiniRefMut`. O par `writer_clone` tem cliente válido que exige `Deref<Target = i32>` do mesmo guard; nenhum cliente inválido é executado.

## Oráculo e controles

Os resultados esperados constam como literais nas fixtures públicas, calculados diretamente pelas regras do enunciado. Não são gerados pela implementação candidata. A validação inicial da referência e dos controles negativos foi executada separadamente. A distribuição não contém referências nem mutantes.

A preparação aprovada significa build e controles de interface disponíveis. O núcleo do starter falha intencionalmente. Após implementar, o participante deve obter aprovação funcional e justificar os limites das observações. Os comandos estão no [guia local](../README.md).

## Origem e licenças

Contrato: atividade 24 do caderno `Oxide_Club_Desafios_e_Laboratorios_Rust_Seguranca_Terminologia_Revisada_2026-10-25.md`; redação conforme PTC 1.1. Materiais originais da preparação `rust-libraries-v1`, 25/10/2026. Documentação CC BY 4.0; código MIT; fixtures/valores esperados CC0 1.0. Fontes externas são links de leitura e conservam suas próprias licenças; nenhum código externo foi incorporado.
