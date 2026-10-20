# 003-rle — executar os testes

Com o [runner independente](../README.md#como-testar-seu-programa) instalado:

```sh
oxide-test run 003-rle /caminho/para/oxide-rle
oxide-test list 003-rle
oxide-test run 003-rle /caminho/para/oxide-rle --case encode-run-256
```

O runner Rust dispensa Python em tempo de execução e apresenta cada vetor como
caso independente. As idas e voltas usam xorshift com estado inicial 3 e os mesmos
tamanhos do executor Python; os bytes gerados diferem entre os dois executores.
O fluxo Python abaixo continua disponível por compatibilidade.

Leia primeiro a [definição](index.md). Compile seu programa, por exemplo:

```sh
cc -std=c11 -Wall -Wextra -Wpedantic seu-rle.c -o oxide-rle
# Ou, com Rust estável:
rustc --edition=2021 seu-rle.rs -o oxide-rle
```

Na raiz de `challenges`, execute com Python 3.10 ou superior em Unix/Linux:

```sh
python3 003-rle/tests/test.py /caminho/para/oxide-rle
```

O executor passa `encode` ou `decode` ao programa e compara bytes exatos.
Cobre entrada vazia, todos os valores de byte, sequências de 255, 256, 510,
511 e 65536 bytes, pares adjacentes iguais e todas as contagens válidas.
Também rejeita argumentos inválidos, contagens zero e pares incompletos,
inclusive após um prefixo válido.

As idas e voltas usam dados pseudoaleatórios com semente fixa, incluindo
tamanhos próximos de 8192 bytes. Um oráculo independente verifica os pares
emitidos, para que erros complementares nos dois modos não passem despercebidos.

Em Linux, o executor verifica erros de leitura com um diretório em `stdin`.
Quando `/dev/full` existe, verifica erros de escrita com saídas pequenas
(falha no flush) e grandes. Verifica também pipes sem leitor.
Casos indisponíveis aparecem como ignorados.
Erros devem produzir status diferente de zero e diagnóstico em `stderr`;
o teste não exige desfazer uma saída parcial já escrita.

Cada caso tem limite de cinco segundos, ajustável com `--timeout 10`.
O executor limita `stderr` a 64 KiB e `stdout` ao tamanho esperado, ao dobro
da entrada no encode aleatório, ou a 256 KiB nos testes de erro.

Revise no código o processamento incremental, o uso de memória e o uso
exclusivo da biblioteca padrão em C11 ou Rust estável. Os testes não provam
essas propriedades. Extensões opcionais devem preservar a interface e o
formato base usados pela suíte.
