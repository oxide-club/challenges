# 013-record-inspector — executar os testes

Leia primeiro a [definição](index.md). Este exercício não depende de outro desafio.

Compile seu programa, por exemplo:

```sh
cc -std=c11 -Wall -Wextra -Wpedantic -I materials seu-inspector.c -o oxide-record-inspector
# Ou, com Rust estável:
rustc --edition=2021 seu-inspector.rs -o oxide-record-inspector
```

Com o [runner independente](../README.md#como-testar-seu-programa) instalado:

```sh
oxide-test list 013-record-inspector
oxide-test run 013-record-inspector /caminho/para/oxide-record-inspector
oxide-test run 013-record-inspector /caminho/para/oxide-record-inspector --case length-overrun
```

Com Python 3.10 ou superior, na raiz de `challenges`:

```sh
python3 013-record-inspector/tests/test.py /caminho/para/oxide-record-inspector
```

Os dois runners usam os mesmos 13 vetores de `tests/cases.json`. Nos casos válidos, o runner compara todos os bytes de `stdout`. Nos casos de erro, exige status diferente de zero e diagnóstico em `stderr`.

A suíte cobre:

- contagem zero;
- os registros do exemplo;
- comprimento zero;
- cabeçalho truncado e assinatura inválida;
- contagem maior que os registros;
- comprimento maior que os bytes restantes;
- bytes extras;
- argumentos e falhas de I/O.

Em Linux, o runner verifica erro de leitura com um diretório em `stdin`, erro de escrita com `/dev/full` e pipe sem leitor. Casos indisponíveis aparecem como ignorados.

Cada caso tem limite de cinco segundos, ajustável com `--timeout 10`. O diretório `materials/` contém o arquivo de exemplo e o helper de leitura little endian.

Revise no código a verificação de limites antes de cada leitura. Os testes verificam a saída, não a estrutura do código.
