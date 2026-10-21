# 017-arena — executar os testes

Leia primeiro a [definição](index.md). Este exercício não depende de outro desafio.

O diretório `materials/` fornece `api.h` e `adapter.c`. Escreva `implementation.c` sem `main` e compile com o adaptador:

```sh
cc -std=c11 -Wall -Wextra -Wpedantic -Werror -I materials implementation.c materials/adapter.c -o oxide-arena
```

Compile e execute também o teste direto da API:

```sh
cc -std=c11 -Wall -Wextra -Wpedantic -Werror -I materials tests/api_test.c implementation.c -o /tmp/oxide-api-test
/tmp/oxide-api-test
```

Com o [runner independente](../README.md#como-testar-seu-programa) instalado:

```sh
oxide-test list 017-arena
oxide-test run 017-arena /caminho/para/oxide-arena
```

Com Python 3.10 ou superior, na raiz de `challenges`:

```sh
python3 017-arena/tests/test.py /caminho/para/oxide-arena
```

Os dois runners usam os mesmos 4 vetores de `tests/cases.json`. Cada vetor envia a capacidade e uma sequência de comandos em `stdin` e compara todos os bytes de `stdout`. Nos casos de erro, o runner exige status diferente de zero e diagnóstico em `stderr`.

A suíte cobre preenchimento por alinhamento, falha sem consumo de capacidade, reset com reutilização, alinhamentos inválidos, tamanho zero, overflow e capacidade zero. O teste direto da API verifica os endereços reais, o alinhamento e a ausência de sobreposição.

O adaptador é infraestrutura de teste. Não altere os comandos nem o formato de saída. Em Rust, reproduza o mesmo protocolo com offsets sobre uma região fixa.

Cada caso tem limite de cinco segundos, ajustável com `--timeout 10`.

Revise no código a verificação de overflow por subtração e a ausência de alocação dinâmica. Os testes não provam essas propriedades.
