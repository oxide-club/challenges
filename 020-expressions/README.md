# 020-expressions — executar os testes

Leia primeiro a [definição](index.md). Este exercício não depende de outro desafio.

Compile seu programa, por exemplo:

```sh
cc -std=c11 -Wall -Wextra -Wpedantic seu-expressions.c -o oxide-expressions
# Ou, com Rust estável:
rustc --edition=2021 seu-expressions.rs -o oxide-expressions
```

Com o [runner independente](../README.md#como-testar-seu-programa) instalado:

```sh
oxide-test list 020-expressions
oxide-test run 020-expressions /caminho/para/oxide-expressions
oxide-test run 020-expressions /caminho/para/oxide-expressions --case precedence --case parens
```

Com Python 3.10 ou superior, na raiz de `challenges`:

```sh
python3 020-expressions/tests/test.py /caminho/para/oxide-expressions
```

Os dois runners usam os mesmos 19 vetores de `tests/cases.json`. Nos casos válidos, o runner compara todos os bytes de `stdout`. Nos casos de erro, exige status diferente de zero e diagnóstico em `stderr`.

A suíte cobre:

- precedência, parênteses e associatividade à esquerda;
- o menor int32 por subtração;
- overflow em soma e produto;
- literal fora do intervalo;
- operador unário e operador duplo;
- operando ausente e token excedente;
- entrada vazia e byte zero;
- profundidade de 64 e 65 parênteses;
- argumentos e falhas de I/O.

Em Linux, o runner verifica erro de leitura com um diretório em `stdin`, erro de escrita com `/dev/full` e pipe sem leitor. Casos indisponíveis aparecem como ignorados.

Cada caso tem limite de cinco segundos, ajustável com `--timeout 10`. O diretório `materials/` contém um lexer inicial em Python para estudo da tokenização.

Revise no código a verificação de overflow em cada operação e o limite de profundidade. Os testes verificam a saída, não a estratégia de parsing.
