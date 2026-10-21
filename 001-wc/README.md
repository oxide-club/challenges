# 001-wc — executar os testes

Leia primeiro a [definição](index.md). Este exercício não depende de outro desafio.

Compile seu programa, por exemplo:

```sh
cc -std=c11 -Wall -Wextra -Wpedantic seu-wc.c -o oxide-wc
```

Com o [runner independente](../README.md#como-testar-seu-programa) instalado:

```sh
oxide-test list 001-wc
oxide-test run 001-wc /caminho/para/oxide-wc
oxide-test run 001-wc /caminho/para/oxide-wc --case sem-quebra
```

Com Python 3.10 ou superior, na raiz de `challenges`:

```sh
python3 001-wc/tests/test.py /caminho/para/oxide-wc
```

Os dois runners usam os mesmos 13 vetores de `tests/cases.json`. Nos casos válidos, exigem status zero e comparam todos os bytes de `stdout`.

A suíte cobre:

- entrada vazia e ausência de LF final;
- os seis separadores ASCII;
- separadores consecutivos e nas bordas;
- uma palavra de 128 KiB;
- 32768 linhas.

Os arquivos `materials/*.in` contêm as entradas. Cada `.out` correspondente contém a saída exata. Alguns arquivos são vazios ou têm caracteres de controle. O [guia dos materiais](materials/README.md) explica a regeneração. A manutenção compara as contagens com `LC_ALL=C wc`; a suíte do participante não depende dessa ferramenta.

Cada caso tem limite de cinco segundos, ajustável com `--timeout 10`.

Revise no código a memória constante, o uso de C11 e a ausência de chamadas ao `wc` original. Os testes não provam essas propriedades. Unicode, flags, caminhos de arquivos e falhas de I/O são extensões opcionais.
