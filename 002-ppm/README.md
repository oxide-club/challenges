# 002-ppm — executar os testes

Leia primeiro a [definição](index.md). Este exercício não depende de outro desafio.

Compile seu programa, por exemplo:

```sh
cc -std=c11 -Wall -Wextra -Wpedantic seu-ppm.c -o oxide-ppm
```

Com o [runner independente](../README.md#como-testar-seu-programa) instalado:

```sh
oxide-test list 002-ppm
oxide-test run 002-ppm /caminho/para/oxide-ppm
oxide-test run 002-ppm /caminho/para/oxide-ppm --case image
```

Com Python 3.10 ou superior, na raiz de `challenges`:

```sh
python3 002-ppm/tests/test.py /caminho/para/oxide-ppm
```

Os dois runners usam os mesmos 2 vetores de `tests/cases.json`. O caso `image` exige status zero e compara o cabeçalho, os 65536 pixels e o tamanho total de 196623 bytes. Nenhum byte adicional é permitido. Diferenças nos pixels recebem diagnóstico de posição e canal.

O caso `write-error` direciona a saída a `/dev/full`. Exige status diferente de zero e diagnóstico em `stderr`. Esse caso aparece como ignorado quando o dispositivo não existe. Verifique também o resultado de `fflush`: o erro pode aparecer somente ao esvaziar o buffer.

Cada caso tem limite de cinco segundos, ajustável com `--timeout 10`. O diretório `materials/` contém a imagem esperada e seu gerador. Consulte o [guia dos materiais](materials/README.md).

Revise no código a memória constante, o uso de C11 e a ausência de bibliotecas gráficas. Os testes não provam essas propriedades. Padrões, dimensões configuráveis e PPM P3 são extensões opcionais.
