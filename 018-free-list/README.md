# 018-free-list — executar os testes

Leia primeiro a [definição](index.md). Este exercício não depende de outro desafio.

O diretório `materials/` fornece `api.h` e `adapter.c`. Escreva `implementation.c` sem `main` e compile com o adaptador:

```sh
cc -std=c11 -Wall -Wextra -Wpedantic -Werror -I materials implementation.c materials/adapter.c -o oxide-free-list
```

Compile e execute também o teste direto da API:

```sh
cc -std=c11 -Wall -Wextra -Wpedantic -Werror -I materials tests/api_test.c implementation.c -o /tmp/oxide-api-test
/tmp/oxide-api-test
```

Com o [runner independente](../README.md#como-testar-seu-programa) instalado:

```sh
oxide-test list 018-free-list
oxide-test run 018-free-list /caminho/para/oxide-free-list
oxide-test run 018-free-list /caminho/para/oxide-free-list --case model-sequence
```

Com Python 3.10 ou superior, na raiz de `challenges`:

```sh
python3 018-free-list/tests/test.py /caminho/para/oxide-free-list
```

Os dois runners usam os mesmos 5 vetores de `tests/cases.json`. Cada vetor envia a capacidade e uma sequência de comandos em `stdin` e compara todos os bytes de `stdout`. Nos casos de erro, o runner exige status diferente de zero e diagnóstico em `stderr`.

A suíte cobre:

- divisão de blocos;
- falha por fragmentação e coalescência;
- liberação de todos os blocos;
- capacidade abaixo de oito;
- tamanho zero e overflow;
- esgotamento dos 1024 descritores;
- uma sequência longa comparada com um modelo independente.

O teste direto da API usa sentinelas nos blocos vivos para detectar sobreposição.

O adaptador é infraestrutura de teste. Não altere os comandos nem o formato de saída. Em Rust, reproduza o mesmo protocolo com offsets sobre uma região fixa.

Cada caso tem limite de cinco segundos, ajustável com `--timeout 10`.

Revise no código a ausência de `malloc`, a ordem dos descritores e a união de vizinhos. Os testes não provam essas propriedades.
