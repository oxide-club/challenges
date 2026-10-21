# 012-hash-table — executar os testes

Leia primeiro a [definição](index.md). Este exercício não depende de outro desafio.

O diretório `materials/` fornece `api.h` e `adapter.c`. Escreva `implementation.c` sem `main` e compile com o adaptador:

```sh
cc -std=c11 -Wall -Wextra -Wpedantic -Werror -I materials implementation.c materials/adapter.c -o oxide-hash-table
```

Compile e execute também o teste direto da API:

```sh
cc -std=c11 -Wall -Wextra -Wpedantic -Werror -I materials tests/api_test.c implementation.c -o /tmp/oxide-api-test
/tmp/oxide-api-test
```

Com o [runner independente](../README.md#como-testar-seu-programa) instalado:

```sh
oxide-test list 012-hash-table
oxide-test run 012-hash-table /caminho/para/oxide-hash-table
oxide-test run 012-hash-table /caminho/para/oxide-hash-table --case model-sequence
```

Com Python 3.10 ou superior, na raiz de `challenges`:

```sh
python3 012-hash-table/tests/test.py /caminho/para/oxide-hash-table
```

Os dois runners usam os mesmos 5 vetores de `tests/cases.json`. Cada vetor envia uma sequência de comandos em `stdin` e compara todos os bytes de `stdout`. Nos casos de erro, o runner exige status diferente de zero e diagnóstico em `stderr`.

A suíte cobre:

- colisões das chaves 0, 8, 16 e 24;
- atualização sem crescimento;
- crescimento de 8 para 16 slots;
- falha de alocação com estado preservado;
- valores nos limites de `int32_t`;
- uma sequência longa gerada por um modelo independente.

O teste direto da API compara pelo menos cem inserções e atualizações com um modelo simples.

O adaptador é infraestrutura de teste. O comando `f` injeta a falha pelo callback `Allocate`. Não altere os comandos nem o formato de saída. Em Rust, reproduza o mesmo protocolo com uma reserva própria e um gancho de falha equivalente.

Cada caso tem limite de cinco segundos, ajustável com `--timeout 10`.

Revise no código a reconstrução das posições no crescimento e a ausência de mapas prontos. Os testes não provam essas propriedades.
