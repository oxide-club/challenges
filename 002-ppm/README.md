# 002-ppm — executar os testes

Leia primeiro a [definição](index.md). Compile seu programa C11, por exemplo:

```sh
cc -std=c11 -Wall -Wextra -Wpedantic seu-ppm.c -o oxide-ppm
```

Na raiz do repositório `challenges`, execute:

```sh
python3 002-ppm/tests/test.py /caminho/para/oxide-ppm
```

Os testes verificam o cabeçalho exato, os 196623 bytes do arquivo, todos os
65536 pixels e o status de saída. Nenhum byte adicional é permitido.

Em Linux, a saída também é direcionada a `/dev/full`: o programa deve
diagnosticar o erro em `stderr` e terminar com status diferente de zero.
Lembre-se de que erros podem aparecer somente ao descarregar o buffer de saída.
Esse caso aparece como ignorado quando o dispositivo não existe.

Os testes não verificam a linguagem utilizada, a ausência de bibliotecas
gráficas ou o uso constante de memória. Revise essas exigências no código.
Padrões, dimensões configuráveis e PPM P3 são extensões opcionais.

Cada caso tem limite de cinco segundos, ajustável com `--timeout 10`.
O executor interrompe programas que ultrapassem 196623 bytes em `stdout` ou
64 KiB em `stderr` por caso. A saída correta cabe nesses limites.
