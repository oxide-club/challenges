# Trace completo do laço

Estado após executar cada instrução; memória inicial zerada.

| PC antes | instrução | pilha depois | mem[0], mem[1] |
|---|---|---|---|
| 0 | PUSH | [3] | 0, 0 |
| 5 | STORE | [] | 3, 0 |
| 7 | LOAD | [3] | 3, 0 |
| 9 | PUSH | [3, 0] | 3, 0 |
| 14 | SUB | [3] | 3, 0 |
| 15 | JZ | [] | 3, 0 |
| 18 | LOAD | [0] | 3, 0 |
| 20 | LOAD | [0, 3] | 3, 0 |
| 22 | ADD | [3] | 3, 0 |
| 23 | STORE | [] | 3, 3 |
| 25 | LOAD | [3] | 3, 3 |
| 27 | PUSH | [3, 1] | 3, 3 |
| 32 | SUB | [2] | 3, 3 |
| 33 | STORE | [] | 2, 3 |
| 35 | JMP | [] | 2, 3 |
| 7 | LOAD | [2] | 2, 3 |
| 9 | PUSH | [2, 0] | 2, 3 |
| 14 | SUB | [2] | 2, 3 |
| 15 | JZ | [] | 2, 3 |
| 18 | LOAD | [3] | 2, 3 |
| 20 | LOAD | [3, 2] | 2, 3 |
| 22 | ADD | [5] | 2, 3 |
| 23 | STORE | [] | 2, 5 |
| 25 | LOAD | [2] | 2, 5 |
| 27 | PUSH | [2, 1] | 2, 5 |
| 32 | SUB | [1] | 2, 5 |
| 33 | STORE | [] | 1, 5 |
| 35 | JMP | [] | 1, 5 |
| 7 | LOAD | [1] | 1, 5 |
| 9 | PUSH | [1, 0] | 1, 5 |
| 14 | SUB | [1] | 1, 5 |
| 15 | JZ | [] | 1, 5 |
| 18 | LOAD | [5] | 1, 5 |
| 20 | LOAD | [5, 1] | 1, 5 |
| 22 | ADD | [6] | 1, 5 |
| 23 | STORE | [] | 1, 6 |
| 25 | LOAD | [1] | 1, 6 |
| 27 | PUSH | [1, 1] | 1, 6 |
| 32 | SUB | [0] | 1, 6 |
| 33 | STORE | [] | 0, 6 |
| 35 | JMP | [] | 0, 6 |
| 7 | LOAD | [0] | 0, 6 |
| 9 | PUSH | [0, 0] | 0, 6 |
| 14 | SUB | [0] | 0, 6 |
| 15 | JZ | [] | 0, 6 |
| 38 | LOAD | [6] | 0, 6 |
| 40 | HALT | [6] | 0, 6 |

## Usar o trace como evidência

A tabela registra o estado **depois** da instrução no PC indicado. Antes de
consultá-la, preveja as visitas ao PC 15: quais condições JZ retira e qual será
o próximo PC? Compare as três visitas com condição não nula e a última com
zero. JZ consome a condição nos dois caminhos; no último, salta para 38.
No PC 35, JMP retorna a 7. Explique a relação entre a redução de `mem[0]`,
o crescimento de `mem[1]` e a chegada ao HALT com exatamente um valor.

Se instrumentar sua VM, registre separadamente passo, PC antes, opcode,
pilha antes/depois, memória e próximo PC. Use um arquivo de diagnóstico ou
`stderr`, mantendo apenas o resultado em `stdout`. Identifique o primeiro
estado divergente; comparar apenas o resultado 6 pode esconder um erro de
salto ou de consumo de pilha. Não é exigida uma API de trace.

## Variar um salto sem trocar a ISA

Como investigação opcional, faça duas cópias do programa fornecido. Partindo
do diretório `021-bytecode`, o trecho abaixo modifica somente o operando do
JMP no offset 35; preserva o original e grava as cópias em `/tmp`:

```sh
python3 - <<'PYCODE'
from pathlib import Path
code = Path("materials/sum-loop.bin").read_bytes()
assert code[35:38] == bytes([0x08, 7, 0])
for name, target in [("self-loop", 35), ("operand-jump", 36)]:
    variant = bytearray(code)
    variant[36:38] = target.to_bytes(2, "little")
    Path(f"/tmp/oxide-{name}.bin").write_bytes(variant)
PYCODE
./oxide-bytecode < /tmp/oxide-self-loop.bin
./oxide-bytecode < /tmp/oxide-operand-jump.bin
```

Preveja antes de executar: 35 é uma fronteira válida, enquanto 36 é um byte
do operando. A primeira cópia passa na validação e, depois da primeira volta,
repete JMP 35 sem mudar pilha nem memória. Ela deve falhar ao tentar executar
a 1001ª instrução. A segunda deve ser rejeitada antes de executar qualquer
instrução, mesmo que o destino contenha um byte que isoladamente pareça opcode.
Em ambos os casos, confira status diferente de zero e diagnóstico em `stderr`.

Use a comparação para explicar o que o mapa de fronteiras garante e o que
não garante: um salto estruturalmente válido pode não terminar. O orçamento
limita trabalho; não é prova de término nem substitui a validação integral.
O limite continua sendo 1000 e inclui HALT; estas cópias não acrescentam
requisitos à suíte ou ao protocolo.

O [guia de migração](../../docs/labs-migration.md) distingue este trace da
variante textual do antigo laboratório 009.
