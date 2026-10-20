# 001-wc — executar os testes

Leia primeiro a [definição](index.md). Compile seu programa C11, por exemplo:

```sh
cc -std=c11 -Wall -Wextra -Wpedantic seu-wc.c -o oxide-wc
```

Na raiz do repositório `challenges`, execute:

```sh
python3 001-wc/tests/test.py /caminho/para/oxide-wc
```

Os casos cobrem os exemplos publicados, todos os seis separadores ASCII,
espaços consecutivos e nas bordas, entrada vazia, ausência de quebra final,
uma palavra longa e muitas linhas. São exigidos status zero e exatamente
três contagens separadas por um espaço, com uma quebra de linha final.

`fixtures/*.in` são entradas em bytes; o arquivo `.out` correspondente
contém a saída exata. Alguns arquivos são vazios ou contêm caracteres de
controle. A verificação de manutenção compara as contagens com `LC_ALL=C wc`;
o teste do participante não depende do `wc` original.

O teste não verifica se o programa usa memória constante, foi escrito em C11
ou invoca outra ferramenta. Revise essas exigências no código. Unicode,
flags, caminhos de arquivos e falhas de I/O são extensões opcionais neste desafio.
