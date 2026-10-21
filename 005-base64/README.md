# 005-base64 — executar os testes

Leia primeiro a [definição](index.md). Este exercício não depende de outro desafio.

Compile seu programa, por exemplo:

```sh
cc -std=c11 -Wall -Wextra -Wpedantic seu-base64.c -o oxide-base64
# Ou, com Rust estável:
rustc --edition=2021 seu-base64.rs -o oxide-base64
```

Com o [runner independente](../README.md#como-testar-seu-programa) instalado:

```sh
oxide-test list 005-base64
oxide-test run 005-base64 /caminho/para/oxide-base64
oxide-test run 005-base64 /caminho/para/oxide-base64 --case decode1
```

Com Python 3.10 ou superior, na raiz de `challenges`:

```sh
python3 005-base64/tests/test.py /caminho/para/oxide-base64
```

Os dois runners usam os mesmos 36 vetores de `tests/cases.json`. O runner passa `encode` ou `decode` ao programa. Os bytes dos vetores ficam em hexadecimal para preservar `00` e `ff`. Nos casos válidos, o runner compara todos os bytes de `stdout`. Nos casos de erro, exige status diferente de zero e diagnóstico em `stderr`.

A suíte cobre:

- os vetores da RFC 4648;
- todos os valores de byte em ida e volta;
- bits de preenchimento não canônicos e padding em posição errada;
- quebra de linha e caracteres fora do alfabeto;
- comprimento incompleto e modo desconhecido;
- falhas de I/O.

Em Linux, o runner verifica erro de leitura com um diretório em `stdin`, erro de escrita com `/dev/full` e pipe sem leitor. Casos indisponíveis aparecem como ignorados.

Cada caso tem limite de cinco segundos, ajustável com `--timeout 10`. O diretório `materials/` contém um exemplo de entrada e saída e um gerador de entradas grandes.

Revise no código o processamento em fluxo, a memória constante e o uso exclusivo da biblioteca padrão. Os testes não provam essas propriedades.
