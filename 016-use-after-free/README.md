# 016-use-after-free — executar os testes

Leia primeiro a [definição](index.md). Este exercício não depende de outro desafio.

Reproduza o defeito do starter com AddressSanitizer antes de editar:

```sh
cc -std=c11 -g -O0 -fsanitize=address -fno-omit-frame-pointer materials/buggy.c -o /tmp/oxide-buggy
ASAN_OPTIONS=detect_leaks=0 /tmp/oxide-buggy
```

Espere status diferente de zero e o diagnóstico `heap-use-after-free`. Endereços e linhas variam conforme a compilação.

O diretório `materials/` fornece `api.h` e `adapter.c`. Escreva `implementation.c` sem `main` e compile com o adaptador:

```sh
cc -std=c11 -Wall -Wextra -Wpedantic -Werror -I materials implementation.c materials/adapter.c -o oxide-use-after-free
```

Compile e execute também o teste direto da API:

```sh
cc -std=c11 -Wall -Wextra -Wpedantic -Werror -I materials tests/api_test.c implementation.c -o /tmp/oxide-api-test
/tmp/oxide-api-test
```

Execute a regressão completa. O script compila o starter e a correção com ASan e UBSan. Ele exige o diagnóstico no starter e a aprovação de todos os vetores na correção:

```sh
python3 tests/sanitizer_regression.py /caminho/para/implementation.c
```

Com o [runner independente](../README.md#como-testar-seu-programa) instalado:

```sh
oxide-test list 016-use-after-free
oxide-test run 016-use-after-free /caminho/para/oxide-use-after-free
```

Com Python 3.10 ou superior, na raiz de `challenges`:

```sh
python3 016-use-after-free/tests/test.py /caminho/para/oxide-use-after-free
```

Os dois runners usam os mesmos 4 vetores de `tests/cases.json`. Cada vetor envia bytes brutos em `stdin` e compara todos os bytes de `stdout`. Nos casos de erro, o runner exige status diferente de zero e diagnóstico em `stderr`.

A suíte cobre entrada vazia, bytes com zero no meio, texto ASCII e entrada acima do limite. O teste direto da API verifica a independência da cópia e a liberação do resultado de comprimento zero.

O adaptador lê bytes brutos, sem comandos. Não altere o formato de saída. Em Rust, reproduza a cópia com propriedade explícita e mantenha a investigação do starter em C.

Cada caso tem limite de cinco segundos, ajustável com `--timeout 10`.

Revise no relato a linha do tempo, o responsável por cada `free` e a regressão. Os testes não avaliam a explicação.
