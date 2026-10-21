# 010-fixed-buffer — executar os testes

Leia primeiro a [definição](index.md). Este exercício não depende de outro desafio.

O diretório `materials/` fornece `api.h` e `adapter.c`. Escreva `implementation.c` sem `main` e compile com o adaptador:

```sh
cc -std=c11 -Wall -Wextra -Wpedantic -Werror -I materials implementation.c materials/adapter.c -o oxide-fixed-buffer
```

Compile e execute também o teste direto da API:

```sh
cc -std=c11 -Wall -Wextra -Wpedantic -Werror -I materials tests/api_test.c implementation.c -o /tmp/oxide-api-test
/tmp/oxide-api-test
```

Com o [runner independente](../README.md#como-testar-seu-programa) instalado:

```sh
oxide-test list 010-fixed-buffer
oxide-test run 010-fixed-buffer /caminho/para/oxide-fixed-buffer
```

Com Python 3.10 ou superior, na raiz de `challenges`:

```sh
python3 010-fixed-buffer/tests/test.py /caminho/para/oxide-fixed-buffer
```

Os dois runners usam os mesmos 6 vetores de `tests/cases.json`. Cada vetor envia a capacidade e uma sequência de comandos em `stdin` e compara todos os bytes de `stdout`. Nos casos de erro, o runner exige status diferente de zero e diagnóstico em `stderr`.

A suíte cobre buffer vazio, capacidade exata, excesso com estado preservado, limpeza, capacidade zero e comando inválido. O teste direto da API verifica bytes de guarda fora da região e a preservação do estado nas falhas.

O adaptador é infraestrutura de teste. Não altere os comandos nem o formato de saída. Em Rust, reproduza o mesmo protocolo sobre uma região fixa com offsets.

Cada caso tem limite de cinco segundos, ajustável com `--timeout 10`.

Revise no código a ausência de alocação dinâmica e de coleções prontas. Os testes não provam essas propriedades.
