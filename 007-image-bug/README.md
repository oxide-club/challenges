# 007-image-bug — executar os testes

Leia primeiro a [definição](index.md). Este exercício não depende de outro desafio.

Compile o starter e reproduza o defeito antes de editar:

```sh
cc -std=c11 -Wall -Wextra -Wpedantic -Werror -I materials materials/buggy.c -o /tmp/buggy
/tmp/buggy < materials/labels-3x2.ppm | cmp - materials/labels-3x2.ppm
```

Compile a versão corrigida com o mesmo helper, por exemplo:

```sh
cc -std=c11 -Wall -Wextra -Wpedantic -Werror -I materials corrigido.c -o oxide-image-bug
# Ou, com Rust estável, reescreva a cópia por coordenadas:
rustc --edition=2021 seu-image-bug.rs -o oxide-image-bug
```

Com o [runner independente](../README.md#como-testar-seu-programa) instalado:

```sh
oxide-test list 007-image-bug
oxide-test run 007-image-bug /tmp/buggy
oxide-test run 007-image-bug /caminho/para/oxide-image-bug
```

Com Python 3.10 ou superior, na raiz de `challenges`:

```sh
python3 007-image-bug/tests/test.py /caminho/para/oxide-image-bug
```

Os dois runners usam os mesmos 15 vetores de `tests/cases.json`. O starter falha nos casos retangulares e passa no caso quadrado. A versão corrigida passa em todos. Nos casos válidos, o runner compara todos os bytes de `stdout` e informa pixel e canal nas diferenças. Nos casos de erro, exige status diferente de zero e diagnóstico em `stderr`.

A suíte cobre imagens 3×2, 2×2, 1×4, 4×1 e 1×1, cabeçalhos inválidos, raster truncado, bytes extras e falhas de I/O. Em Linux, o runner verifica erro de leitura com um diretório em `stdin`, erro de escrita com `/dev/full` e pipe sem leitor. Casos indisponíveis aparecem como ignorados.

Cada caso tem limite de cinco segundos, ajustável com `--timeout 10`. O diretório `materials/` contém o starter, o helper PPM, a imagem rotulada 3×2 e a imagem quadrada 2×2.

Revise no relato o contraexemplo, a hipótese, a causa e a regressão. Os testes não avaliam a explicação.
