# 009-triangle — executar os testes

Leia primeiro a [definição](index.md). Este exercício não depende de outro desafio.

Compile seu programa com o helper PPM fornecido, por exemplo:

```sh
cc -std=c11 -Wall -Wextra -Wpedantic -I materials seu-triangle.c -o oxide-triangle
# Ou, com Rust estável:
rustc --edition=2021 seu-triangle.rs -o oxide-triangle
```

Com o [runner independente](../README.md#como-testar-seu-programa) instalado:

```sh
oxide-test list 009-triangle
oxide-test run 009-triangle /caminho/para/oxide-triangle
oxide-test run 009-triangle /caminho/para/oxide-triangle --case triangle5 --case triangle6
```

Com Python 3.10 ou superior, na raiz de `challenges`:

```sh
python3 009-triangle/tests/test.py /caminho/para/oxide-triangle
```

Os dois runners usam os mesmos 20 vetores de `tests/cases.json`. Nos casos válidos, o runner compara todos os bytes de `stdout` e informa pixel e canal nas diferenças. Nos casos de erro, exige status diferente de zero e diagnóstico em `stderr`.

A suíte cobre:

- canvas vazio;
- interpolação e orientação invertida;
- triângulo degenerado;
- clipping e bordas compartilhadas;
- um corpus de vinte faces;
- vértices nos limites de coordenadas;
- entradas inválidas;
- falhas de I/O.

Em Linux, o runner verifica erro de leitura com um diretório em `stdin`, erro de escrita com `/dev/full` e pipe sem leitor. Casos indisponíveis aparecem como ignorados.

Cada caso tem limite de cinco segundos, ajustável com `--timeout 10`. O diretório `materials/` contém o helper PPM, o exemplo com um triângulo, sua imagem esperada e um oráculo em Python com frações exatas:

```sh
python3 materials/oracle.py < materials/triangle.txt > /tmp/reference.ppm
cmp /tmp/reference.ppm materials/triangle.ppm
```

Revise no código a largura dos produtos, a regra de empate das arestas e o arredondamento. Os testes verificam a imagem final, não a explicação.
