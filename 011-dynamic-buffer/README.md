# 011-dynamic-buffer — executar os testes

Leia primeiro a [definição](index.md). Este exercício não depende de outro desafio.

O diretório `materials/` fornece `api.h` e `adapter.c`. Escreva `implementation.c` sem `main` e compile com o adaptador:

```sh
cc -std=c11 -Wall -Wextra -Wpedantic -Werror -I materials implementation.c materials/adapter.c -o oxide-dynamic-buffer
```

Compile e execute também o teste direto da API:

```sh
cc -std=c11 -Wall -Wextra -Wpedantic -Werror -I materials tests/api_test.c implementation.c -o /tmp/oxide-api-test
/tmp/oxide-api-test
```

Com o [runner independente](../README.md#como-testar-seu-programa) instalado:

```sh
oxide-test list 011-dynamic-buffer
oxide-test run 011-dynamic-buffer /caminho/para/oxide-dynamic-buffer
```

Com Python 3.10 ou superior, na raiz de `challenges`:

```sh
python3 011-dynamic-buffer/tests/test.py /caminho/para/oxide-dynamic-buffer
```

Os dois runners usam os mesmos 5 vetores de `tests/cases.json`. Cada vetor envia uma sequência de comandos em `stdin` e compara todos os bytes de `stdout`. Nos casos de erro, o runner exige status diferente de zero e diagnóstico em `stderr`.

A suíte cobre buffer vazio, crescimento de 8 para 16 e 32 bytes, falha simulada do alocador com estado preservado, overflow sem chamada ao alocador e destruição. O teste direto da API verifica cem appends e a preservação do ponteiro na falha.

O adaptador é infraestrutura de teste. O comando `f` injeta a falha pelo callback `Resize`. Não altere os comandos nem o formato de saída. Em Rust, reproduza o mesmo protocolo com uma reserva própria e um gancho de falha equivalente.

Cada caso tem limite de cinco segundos, ajustável com `--timeout 10`.

Revise no código o cálculo da nova capacidade, a verificação de overflow antes do alocador e a ausência de coleções prontas. Os testes não provam essas propriedades.
