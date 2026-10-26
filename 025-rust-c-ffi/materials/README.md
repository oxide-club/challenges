# Materiais — biblioteca Rust com interface C

O clube fornece build, assinaturas, clientes de verificação, fixtures e gancho de panic. O participante completa a biblioteca e o helper.

| Arquivo | Função |
| --- | --- |
| `starter/oxide.h` | Tipos e assinaturas C; documentação de ponteiros a completar. |
| `starter/rotate.c` | Helper C incompleto. |
| `starter/rust/lib.rs` | Biblioteca incompleta, com exports compiláveis. |
| `starter/rust/hooks.rs` | Injeção única de panic por thread, somente em testes. |
| `generate.py`, `fixtures.json` | 512 valores esperados, calculados por rearranjo textual de bits. |
| `../tests/expected.h` | Os mesmos dados CC0 consumidos pelo cliente C. |
| `../tests/client.c` | Integração C → Rust → C e casos de erro. |
| `../tests/destroy.c`, `destroy_poison.c` | Liberação de contextos sem panic e após poison, com LSan. |
| `../tests/lsan_probe.c`, `lsan_probe.rs` | Sonda independente da disponibilidade e da supressão específica do payload. |
| `../tests/helper.rs`, `../tests/layout.rs` | Clientes Rust para helper e layout. |
| `../tests/check.py` | Build e execução em diretório temporário. |

Os valores literais `00 01 80 ff → 00 02 01 ff` e os offsets LP64 foram conferidos manualmente.
O gerador usa strings de oito bits; o helper de referência usa operadores inteiros. A comparação não depende de round-trip.

Execute os comandos do [guia local](../README.md). Status 0 em `--prepare` não aprova o núcleo.
Consulte [origem e licenças](ORIGIN.md).
