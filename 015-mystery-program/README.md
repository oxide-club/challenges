# 015-mystery-program — executar os testes

Leia primeiro a [definição](index.md) e os [traces](materials/traces.md). Este exercício não depende de outro desafio.

O alvo `materials/mystery-linux-x86_64` executa somente em Linux x86-64. O clube distribui um único alvo para manter os offsets dos traces e o procedimento de debugger iguais para todos. Em outra plataforma, execute o alvo no ambiente [Docker](../docs/runner.md#docker) ou no [WSL 2](../docs/runner.md#windows-com-wsl-2-recomendado) descritos no guia do runner. Sem esses ambientes, use a listagem `materials/mystery.asm` e os traces. Consulte o alvo como oráculo:

```sh
printf 'ABC' | ./materials/mystery-linux-x86_64 | od -An -tx1
```

Compile sua implementação equivalente, por exemplo:

```sh
cc -std=c11 -Wall -Wextra -Wpedantic seu-programa.c -o oxide-mystery-program
# Ou, com Rust estável:
rustc --edition=2021 seu-programa.rs -o oxide-mystery-program
```

Com o [runner independente](../README.md#como-testar-seu-programa) instalado:

```sh
oxide-test list 015-mystery-program
oxide-test run 015-mystery-program /caminho/para/oxide-mystery-program
oxide-test run 015-mystery-program /caminho/para/oxide-mystery-program --case fresh
```

Com Python 3.10 ou superior, na raiz de `challenges`:

```sh
python3 015-mystery-program/tests/test.py /caminho/para/oxide-mystery-program
```

Os dois runners usam os mesmos 10 vetores de `tests/cases.json`. Nos casos válidos, o runner compara todos os bytes de `stdout`. Nos casos de erro, exige status diferente de zero e diagnóstico em `stderr`.

A suíte cobre entrada vazia, o byte zero, `ABC`, uma amostra nova com bytes altos, 64 bytes, 65 bytes, argumentos e falhas de I/O. Use a amostra nova somente na etapa de validação. Em Linux, o runner verifica erro de leitura com um diretório em `stdin`, erro de escrita com `/dev/full` e pipe sem leitor. Casos indisponíveis aparecem como ignorados.

Cada caso tem limite de cinco segundos, ajustável com `--timeout 10`.

Revise no relato o pseudocódigo, os experimentos e a validação com casos novos. Os testes verificam a saída, não a investigação.
