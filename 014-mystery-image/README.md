# 014-mystery-image — executar os testes

Leia primeiro a [definição](index.md) e o [corpus inicial](materials/README.md). Este exercício não depende de outro desafio.

Compile seu programa, por exemplo:

```sh
cc -std=c11 -Wall -Wextra -Wpedantic seu-leitor.c -o oxide-mystery-image
# Ou, com Rust estável:
rustc --edition=2021 seu-leitor.rs -o oxide-mystery-image
```

Com o [runner independente](../README.md#como-testar-seu-programa) instalado:

```sh
oxide-test list 014-mystery-image
oxide-test run 014-mystery-image /caminho/para/oxide-mystery-image
oxide-test run 014-mystery-image /caminho/para/oxide-mystery-image --case red --case rect
```

Com Python 3.10 ou superior, na raiz de `challenges`:

```sh
python3 014-mystery-image/tests/test.py /caminho/para/oxide-mystery-image
```

Os dois runners usam os mesmos 11 vetores de `tests/cases.json`. Nos casos válidos, o runner compara todos os bytes de `stdout` e informa pixel e canal nas diferenças. Nos casos de erro, exige status diferente de zero e diagnóstico em `stderr`.

A suíte cobre:

- o pixel vermelho e o retângulo do corpus;
- uma amostra nova com cores e dimensões fora do corpus;
- payload truncado e dimensão zero;
- cabeçalho inválido e bytes extras;
- argumentos e falhas de I/O.

Use a amostra nova somente na etapa de validação. Em Linux, o runner verifica erro de leitura com um diretório em `stdin`, erro de escrita com `/dev/full` e pipe sem leitor. Casos indisponíveis aparecem como ignorados.

Cada caso tem limite de cinco segundos, ajustável com `--timeout 10`. O diretório `materials/` contém os pares `.px` e `.ppm`, o oráculo e o helper de visualização PPM.

Revise no relato as hipóteses, as evidências e a validação com amostras novas. Os testes verificam a saída, não a investigação.
