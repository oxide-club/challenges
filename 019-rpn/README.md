# 019-rpn — executar os testes

Leia primeiro a [definição](index.md). Este exercício não depende de outro desafio.

Compile seu programa, por exemplo:

```sh
cc -std=c11 -Wall -Wextra -Wpedantic seu-rpn.c -o oxide-rpn
# Ou, com Rust estável:
rustc --edition=2021 seu-rpn.rs -o oxide-rpn
```

Com o [runner independente](../README.md#como-testar-seu-programa) instalado:

```sh
oxide-test list 019-rpn
oxide-test run 019-rpn /caminho/para/oxide-rpn
oxide-test run 019-rpn /caminho/para/oxide-rpn --case overflow
```

Com Python 3.10 ou superior, na raiz de `challenges`:

```sh
python3 019-rpn/tests/test.py /caminho/para/oxide-rpn
```

Os dois runners usam os mesmos 19 vetores de `tests/cases.json`. Nos casos válidos, o runner compara todos os bytes de `stdout`. Nos casos de erro, exige status diferente de zero e diagnóstico em `stderr`.

A suíte cobre:

- o exemplo e a ordem dos operandos;
- o menor int32 e literal fora do intervalo;
- overflow em soma, subtração e multiplicação;
- falta de operandos e valores excedentes;
- entrada vazia;
- a capacidade de 64 valores e o 65º valor;
- byte zero em token e whitespace variado;
- argumentos e falhas de I/O.

Em Linux, o runner verifica erro de leitura com um diretório em `stdin`, erro de escrita com `/dev/full` e pipe sem leitor. Casos indisponíveis aparecem como ignorados.

Cada caso tem limite de cinco segundos, ajustável com `--timeout 10`. O diretório `materials/` contém o trace da pilha para o exemplo.

Revise no código a verificação de overflow antes de cada operação e o limite fixo da pilha. Os testes verificam a saída, não a estrutura do código.
