# Desafios do Oxide Club

Definições e testes públicos dos desafios do [Oxide Club](https://oxideclub.dev).
Nosso método é **Explorar → Experimentar → Explicar**. Dúvidas, experimentos
e implementações parciais também fazem parte da participação.

| ID estável | Desafio | Guia dos testes |
| --- | --- | --- |
| `001-wc` | [Construa seu wc](001-wc/index.md) | [Executar os testes](001-wc/README.md) |
| `002-ppm` | [Gere uma imagem PPM](002-ppm/index.md) | [Executar os testes](002-ppm/README.md) |

## Como participar

1. Leia o `index.md` do desafio.
2. Desenvolva sua implementação em seu próprio repositório.
3. Execute os testes públicos contra seu programa.
4. Compartilhe descobertas, dúvidas e resultados no tópico do Discord indicado na definição.

Você não precisa consultar uma solução para usar os testes. As implementações
mantidas pelo clube ficam no repositório separado `solutions`, em
`<id>/reference/`. O arquivo `COMMUNITY.md` daquele repositório reúne links
para implementações dos participantes. Não envie sua solução como parte da definição.

## Testar seu programa

Requisitos: Python 3.10 ou superior e Unix/Linux. Os testes usam somente a
biblioteca padrão do Python, sem instalação de pacotes.

Na raiz deste repositório:

```sh
python3 001-wc/tests/test.py /caminho/para/oxide-wc
python3 002-ppm/tests/test.py /caminho/para/oxide-ppm
```

Caminhos relativos são interpretados a partir do diretório de onde você executa
o comando. Use aspas quando houver espaços. Os programas são executados sem
argumentos. Cada caso tem limite de cinco segundos, ajustável com
`--timeout 10`. Falhas retornam status diferente de zero; cada resultado aparece
no terminal. Em outros sistemas Unix, o teste PPM de erro de escrita é
explicitamente ignorado se `/dev/full` não existir.

O executor interrompe programas que excedam 1024 bytes de saída no WC,
196623 bytes no PPM ou 64 KiB de diagnósticos em `stderr` por caso.
Esses limites evitam que uma impressão acidentalmente repetida esgote o
armazenamento; a saída válida de cada desafio cabe nesses limites.

Os testes verificam comportamento observável, não a linguagem utilizada,
complexidade de memória ou todas as restrições de implementação. Leia a
especificação e revise seu código; passar nos testes não substitui essa revisão.

## Contribuir com definições ou testes

Veja [CONTRIBUTING.md](CONTRIBUTING.md). Um desafio ocupa um diretório
`NNN-name`, com número sequencial de três dígitos e um nome curto em minúsculas.
O diretório e o `slug` da definição devem ser iguais. Números publicados
nunca são reutilizados e IDs não mudam com o título.

O `index.md` é a especificação canônica. README, testes e fixtures são arquivos
de apoio. O site poderá consumir apenas os arquivos `<id>/index.md`.

Para verificar o repositório, instale também Make e o utilitário Unix `wc`:

```sh
make check
```

Esse comando valida os IDs, confere fixtures com `LC_ALL=C wc` e testa os
próprios executores usando respostas de fixtures e programas deliberadamente
incorretos. Não publica soluções. O CI executa o mesmo comando em Linux.

As soluções mantidas pelo clube executam estes mesmos testes, fixando uma
revisão deste repositório. Ao alterar um contrato ou teste, indique o impacto
na revisão e atualize a referência em `solutions` quando a alteração for adotada.

## Licenciamento

Testes, ferramentas e documentação técnica original usam [MIT](LICENSE).
As definições editoriais dos desafios têm escopo separado: consulte
[LICENSING.md](LICENSING.md).
