# 004-hexdump — executar os testes

Leia primeiro a [definição](index.md). Este exercício não depende de outro desafio.

Compile seu programa, por exemplo:

```sh
cc -std=c11 -Wall -Wextra -Wpedantic seu-hexdump.c -o oxide-hexdump
# Ou, com Rust estável:
rustc --edition=2021 seu-hexdump.rs -o oxide-hexdump
```

Com o [runner independente](../README.md#como-testar-seu-programa) instalado:

```sh
oxide-test list 004-hexdump
oxide-test run 004-hexdump /caminho/para/oxide-hexdump
oxide-test run 004-hexdump /caminho/para/oxide-hexdump --case bytes-17
```

Com Python 3.10 ou superior, na raiz de `challenges`:

```sh
python3 004-hexdump/tests/test.py /caminho/para/oxide-hexdump
```

Os dois runners usam os mesmos 12 vetores de `tests/cases.json`. Os bytes dos vetores ficam em hexadecimal para preservar `00` e `ff`. Nos casos válidos, o runner compara todos os bytes de `stdout`. Nos casos de erro, exige status diferente de zero e diagnóstico em `stderr`.

A suíte cobre entrada vazia, 1, 15, 16, 17 e 256 bytes, leitura por argumento, arquivo inexistente, excesso de argumentos e falhas de I/O. Em Linux, o runner verifica erro de leitura com um diretório em `stdin`, erro de escrita com `/dev/full` e pipe sem leitor. Casos indisponíveis aparecem como ignorados.

Cada caso tem limite de cinco segundos, ajustável com `--timeout 10`. O diretório `materials/` contém um exemplo de entrada e saída e um gerador de entradas grandes.

Revise no código o processamento em fluxo, a memória constante e o uso exclusivo da biblioteca padrão. Os testes não provam essas propriedades.
