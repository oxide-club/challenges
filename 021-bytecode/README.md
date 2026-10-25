# 021-bytecode — executar os testes

Leia primeiro a [definição](index.md) e o [trace do laço](materials/trace.md). Este exercício não depende de outro desafio.

Compile seu programa, por exemplo:

```sh
cc -std=c11 -Wall -Wextra -Wpedantic seu-vm.c -o oxide-bytecode
# Ou, com Rust estável:
rustc --edition=2021 seu-vm.rs -o oxide-bytecode
```

Execute o programa com laço fornecido:

```sh
./oxide-bytecode < materials/sum-loop.bin
```

Com o [runner independente](../README.md#como-testar-seu-programa) instalado:

```sh
oxide-test list 021-bytecode
oxide-test run 021-bytecode /caminho/para/oxide-bytecode
oxide-test run 021-bytecode /caminho/para/oxide-bytecode --case loop --case unreachable-invalid
```

Com Python 3.10 ou superior, na raiz de `challenges`:

```sh
python3 021-bytecode/tests/test.py /caminho/para/oxide-bytecode
```

Os dois runners usam os mesmos 27 vetores de `tests/cases.json`. Nos casos válidos, o runner compara todos os bytes de `stdout`. Nos casos de erro, exige status diferente de zero e diagnóstico em `stderr`.

A suíte cobre:

- soma, laço e DUP;
- valores negativos;
- entrada vazia;
- falta de operandos em cada instrução que retira valores;
- opcode desconhecido e operando truncado;
- salto para o meio de uma instrução, para o fim do arquivo e salto truncado;
- endereço de memória inválido;
- código inalcançável inválido;
- queda fora do código;
- 65º valor e overflow;
- HALT com pilha incorreta;
- orçamento exato e orçamento excedido;
- argumentos e falhas de I/O.

Em Linux, o runner verifica erro de leitura com um diretório em `stdin`, erro de escrita com `/dev/full` e pipe sem leitor. Casos indisponíveis aparecem como ignorados.

Cada caso tem limite de cinco segundos, ajustável com `--timeout 10`. O diretório `materials/` contém o leitor inicial em Python, o programa com laço e o seu trace.

Revise no código a validação prévia de todo o programa e o trace do laço. Os testes verificam a saída, não o trace.

## Orientação e migração

O [roteiro junto ao trace](materials/trace.md#usar-o-trace-como-evidência) orienta previsões e uma intervenção opcional nos saltos, sem alterar a ISA.

Veio do laboratório 009? Consulte o [guia de migração](../docs/labs-migration.md) antes de adaptar seu projeto. Não é necessário refazer uma implementação já concluída; os testes daqui validam apenas o contrato deste desafio.
