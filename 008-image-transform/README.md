# 008-image-transform — executar os testes

Leia primeiro a [definição](index.md). Este exercício não depende de outro desafio.

Compile seu programa com o helper PPM fornecido, por exemplo:

```sh
cc -std=c11 -Wall -Wextra -Wpedantic -I materials seu-transform.c -o oxide-image-transform
# Ou, com Rust estável:
rustc --edition=2021 seu-transform.rs -o oxide-image-transform
```

Com o [runner independente](../README.md#como-testar-seu-programa) instalado:

```sh
oxide-test list 008-image-transform
oxide-test run 008-image-transform /caminho/para/oxide-image-transform
oxide-test run 008-image-transform /caminho/para/oxide-image-transform --case rotate
```

Com Python 3.10 ou superior, na raiz de `challenges`:

```sh
python3 008-image-transform/tests/test.py /caminho/para/oxide-image-transform
```

Os dois runners usam os mesmos 23 vetores de `tests/cases.json`. O runner passa `rotate` ou `crop X Y W H` ao programa. Nos casos válidos, o runner compara todos os bytes de `stdout` e informa pixel e canal nas diferenças. Nos casos de erro, exige status diferente de zero e diagnóstico em `stderr`.

A suíte cobre:

- rotação e recorte da imagem rotulada 3×2;
- recorte da imagem inteira e recorte de um pixel;
- imagens 1×3, 3×1 e 1×1;
- recortes fora da imagem e argumentos malformados;
- PPM inválido;
- falhas de I/O.

Em Linux, o runner verifica erro de leitura com um diretório em `stdin`, erro de escrita com `/dev/full` e pipe sem leitor. Casos indisponíveis aparecem como ignorados.

Cada caso tem limite de cinco segundos, ajustável com `--timeout 10`. O diretório `materials/` contém o helper PPM, a imagem rotulada 3×2 e um exemplo de entrada e saída.

Revise no código a verificação dos limites antes do acesso à imagem e a explicação do mapeamento de coordenadas. Os testes não avaliam a explicação.
