# 003-rle — executar os testes

Leia primeiro a [definição](index.md). Este exercício não depende de outro desafio.

Compile seu programa, por exemplo:

```sh
cc -std=c11 -Wall -Wextra -Wpedantic seu-rle.c -o oxide-rle
# Ou, com Rust estável:
rustc --edition=2021 seu-rle.rs -o oxide-rle
```

Com o [runner independente](../README.md#como-testar-seu-programa) instalado:

```sh
oxide-test list 003-rle
oxide-test run 003-rle /caminho/para/oxide-rle
oxide-test run 003-rle /caminho/para/oxide-rle --case encode-run-256
```

Com Python 3.10 ou superior, na raiz de `challenges`:

```sh
python3 003-rle/tests/test.py /caminho/para/oxide-rle
```

Os dois runners usam os mesmos 54 vetores de `tests/cases.json`. O runner passa `encode` ou `decode` ao programa. Nos casos válidos, exige status zero e compara todos os bytes de `stdout`. Nos casos de erro, exige status diferente de zero e diagnóstico em `stderr`.

A suíte cobre:

- entrada vazia e todos os valores de byte;
- sequências de 255, 256, 510, 511 e 65536 bytes;
- todas as contagens válidas e pares adjacentes com o mesmo valor;
- argumentos inválidos, contagem zero e par incompleto, inclusive após um prefixo válido;
- ida e volta com dados determinísticos, inclusive tamanhos próximos de 8192 bytes;
- falhas de I/O.

Cada ida e volta compara primeiro a codificação com o resultado de um oráculo independente. Depois, envia a saída real de `encode` a `decode` e exige a recuperação exata da entrada.

Em Linux, o runner verifica erro de leitura com um diretório em `stdin`. Também verifica escrita em `/dev/full`, com saídas pequenas e grandes, e pipe sem leitor. Casos indisponíveis aparecem como ignorados. Uma falha pode deixar saída parcial.

Cada invocação tem limite de cinco segundos, ajustável com `--timeout 10`. Uma ida e volta usa duas invocações. O diretório `materials/` contém exemplos binários e seu gerador. Consulte o [guia dos materiais](materials/README.md).

Revise no código o processamento em fluxo, a memória constante e o uso exclusivo da biblioteca padrão. Os testes não provam essas propriedades. As extensões preservam a interface e o formato básicos.
