# 006-stream-search — executar os testes

Leia primeiro a [definição](index.md). Este exercício não depende de outro desafio.

Compile seu programa, por exemplo:

```sh
cc -std=c11 -Wall -Wextra -Wpedantic seu-stream-search.c -o oxide-stream-search
# Ou, com Rust estável:
rustc --edition=2021 seu-stream-search.rs -o oxide-stream-search
```

Com o [runner independente](../README.md#como-testar-seu-programa) instalado:

```sh
oxide-test list 006-stream-search
oxide-test run 006-stream-search /caminho/para/oxide-stream-search
oxide-test run 006-stream-search /caminho/para/oxide-stream-search --case search4
```

Com Python 3.10 ou superior, na raiz de `challenges`:

```sh
python3 006-stream-search/tests/test.py /caminho/para/oxide-stream-search
```

Os dois runners usam os mesmos 15 vetores de `tests/cases.json`. O runner passa o padrão hexadecimal como argumento. Os bytes dos vetores ficam em hexadecimal para preservar `00` e `ff`. Nos casos válidos, o runner compara todos os bytes de `stdout`. Nos casos de erro, exige status diferente de zero e diagnóstico em `stderr`.

A suíte cobre:

- entrada vazia;
- ocorrências sobrepostas;
- bytes `00` e `ff`;
- uma ocorrência que atravessa a fronteira de um bloco de 4096 bytes;
- prefixos repetidos;
- padrão maior que a entrada;
- argumentos inválidos;
- falhas de I/O.

Em Linux, o runner verifica erro de leitura com um diretório em `stdin`, erro de escrita com `/dev/full` e pipe sem leitor. Casos indisponíveis aparecem como ignorados.

Cada caso tem limite de cinco segundos, ajustável com `--timeout 10`. O diretório `materials/` contém um exemplo de entrada e saída e um gerador de entradas grandes.

Revise no código a tabela de prefixos, o estado preservado entre blocos, a memória O(m+B) e o uso exclusivo da biblioteca padrão. Os testes verificam resultados, não a complexidade.
