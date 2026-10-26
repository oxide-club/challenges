# Materiais — no_std

| Arquivo | Responsabilidade |
| --- | --- |
| `starter/start.S` | Stub do clube; alinhamento, direção de strings e chamada não retornante. |
| `starter/memory.S` | Rotinas auxiliares reais do clube. |
| `starter/main.rs` | Wrappers a completar; mensagem, seleção 0/74 e panic handler 101 fornecidos. |
| `starter/policy.rs` | Política de escrita a completar. |
| `../tests/policy.rs` | Retornos simulados de escrita, sem syscall nativa. |
| `../tests/stack.S` | Cliente independente para auditar a ABI do stub. |
| `../tests/memory.c` | Casos independentes para as rotinas auxiliares. |
| `../tests/check.py` | Build, inspeção e testes em subprocessos. |
| `../tests/write_limit.c`, `write_limit_probe.c`, `writev_limit_probe.c` | Tracer e sonda independentes para escrita nativa parcial seguida de sucesso; não exigem interface adicional do candidato. |
| `AUDIT.md` | Referência psABI, inventário, invariantes e limites. |

Siga o [guia local](../README.md). `--prepare` verifica o suporte; não aprova o núcleo incompleto.
A saída esperada foi transcrita literalmente do enunciado e conferida como 19 bytes.
A referência completa e os mutantes permanecem fora do pacote distribuído.
Consulte [origem e licenças](ORIGIN.md).
