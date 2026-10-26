# Referências e revisões

Contrato local: atividade 21 do caderno revisado em 25/10/2026; PTC 1.1. As referências abaixo foram consultadas em 25/10/2026. Não há dependências Cargo externas nem código upstream incorporado à solução inicial.

| Referência | Revisão fixa e leitura | Alcance |
| --- | --- | --- |
| R21.1 | Book, commit `05d114287b7d6f6c9253d5242540f00fbd6172ab`: [introdução a generics](https://github.com/rust-lang/book/blob/05d114287b7d6f6c9253d5242540f00fbd6172ab/src/ch10-00-generics.md) e [métodos](https://github.com/rust-lang/book/blob/05d114287b7d6f6c9253d5242540f00fbd6172ab/src/ch10-01-syntax.md#in-method-definitions). | Comparar `impl<T> Point<T>` com `impl Point<f32>`. Não fornece o protocolo de transições do exercício. |
| R21.2 | Rust, commit `48a229ceaefd4985c50990b14116b6d856af0985`: [documentação de `PhantomData`](https://github.com/rust-lang/rust/blob/48a229ceaefd4985c50990b14116b6d856af0985/library/core/src/marker.rs#L676). | Exemplos de parâmetros não armazenados e ressalvas sobre drop checking; explicar a relação de tipos representada pelo marcador. |
| R21.3 | Mesmo commit Rust: [definição e implementações de traits](https://github.com/rust-lang/rust/blob/48a229ceaefd4985c50990b14116b6d856af0985/library/core/src/marker.rs#L811). | Localizar `PhantomData`, `Copy` e `Clone`; distinguir copiar o marcador de copiar o recurso. |

O commit do Book foi identificado pelo [submódulo de documentação do Rust](https://github.com/rust-lang/rust/blob/48a229ceaefd4985c50990b14116b6d856af0985/src/doc), que aponta para essa revisão. Não foi inferido a partir do número da toolchain. A documentação conceitual de `PhantomData` e sua implementação estão no mesmo arquivo fixado, em trechos distintos.

Fontes primárias: projetos Rust e The Rust Programming Language. Licença MIT conferida nos arquivos [do Book](https://github.com/rust-lang/book/blob/05d114287b7d6f6c9253d5242540f00fbd6172ab/LICENSE-MIT) e [do Rust](https://github.com/rust-lang/rust/blob/48a229ceaefd4985c50990b14116b6d856af0985/LICENSE-MIT); os avisos upstream permanecem aplicáveis. Os fontes completos e as licenças consultadas foram preservados fora do pacote público. URLs, status HTTP, tamanho e SHA-256 constam no manifesto de consulta (registro histórico retirado deste repositório).

Os três links do índice são fixos. A suíte continua derivada do contrato local; esta leitura não altera assinaturas, comportamento exigido nem critérios dos testes.
