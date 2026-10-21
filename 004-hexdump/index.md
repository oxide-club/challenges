---
title: 'Hexdump'
slug: '004-hexdump'
area: systems-fundamentals
summary: 'Mostre offsets, bytes em hexadecimal e uma coluna ASCII, com 16 bytes por linha e saída exata.'
publishedAt: 2026-10-20
updatedAt: 2026-10-20
draft: false
difficulty: beginner
categories: [build]
participation: flagship
recommendedLanguage: C
acceptedLanguages: [C, Rust]
cardTopics: ['Bytes e fluxo', 'Formatação exata', 'Testes de fronteira']
topics: ['Processamento binário', 'Offsets', 'Hexadecimal', 'ASCII', 'Streams']
github:
  challenge: true
  solutions: [c]
  community: true
featured: false
environment: 'C11 ou Rust estável · Unix/Linux · bytes de 8 bits'
---

**Dificuldade:** Fácil  
**Linguagem recomendada:** C (C11)  
**Linguagens aceitas:** C (C11) e Rust (estável)  
**Conceitos:** Processamento binário, offsets, hexadecimal, ASCII e streams.

## O desafio

Um hexdump mostra todos os bytes de um arquivo, inclusive os bytes que um terminal não mostra como texto.

Implemente o `oxide-hexdump`. A ferramenta mostra o offset, os valores em hexadecimal e uma coluna ASCII alinhada.

O foco é ler dados binários em fluxo e formatar a última linha incompleta. Pré-requisitos: laços, arrays e I/O básico.

## Especificação

Aceite zero ou um argumento:

```sh
oxide-hexdump
oxide-hexdump arquivo
```

Sem argumento, leia `stdin`. Com um argumento, abra o caminho em modo binário. O nome `-` é um nome de arquivo comum. Rejeite dois ou mais argumentos.

Divida a entrada em linhas de até 16 bytes. Cada linha contém, nesta ordem:

1. O offset do primeiro byte em hexadecimal minúsculo, com no mínimo oito dígitos e zeros à esquerda.
2. Dois espaços e dezesseis campos de três caracteres. Um byte presente ocupa dois dígitos hexadecimais minúsculos e um espaço. Uma posição ausente ocupa três espaços.
3. Um espaço, `|`, a representação ASCII dos bytes presentes, `|` e uma quebra de linha `\n`.

Na coluna ASCII, mostre os bytes de `0x20` a `0x7e` como caracteres. Substitua os demais bytes por `.`. Não complete a coluna ASCII com espaços.

Os offsets começam em zero e contam bytes. Entrada vazia produz saída vazia. Não escreva uma linha final com o tamanho. Não compacte linhas repetidas.

Aceite comprimentos representáveis em `uint64_t` e rejeite overflow. Processe a entrada em fluxo, com tempo O(n) e memória adicional O(1).

## Exemplo

O vetor `bytes-17` contém os bytes de `00` a `10`. A saída exata é:

```text
00000000  00 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d 0e 0f  |................|
00000010  10                                               |.|
```

A segunda linha contém quinze campos vazios. Os espaços fazem parte do resultado. A quebra de linha após cada `|` final também.

## Requisitos

- Implemente em C11 ou Rust estável, apenas com a biblioteca padrão. Trate bytes como valores de 8 bits.
- Não delegue o núcleo do exercício a ferramentas prontas, como `xxd` ou `od`.
- Retorne status zero somente no sucesso. Escreva em `stdout` apenas o resultado especificado. Os testes não comparam `stderr` no sucesso.
- Em argumento inválido ou falha de leitura, alocação ou escrita, escreva um diagnóstico em `stderr` e retorne status diferente de zero.
- Esvazie o buffer de saída antes de encerrar (`fflush` em C) e verifique o resultado. Trate pipe fechado com diagnóstico. Não encerre em silêncio por `SIGPIPE`.
- Uma falha pode deixar saída parcial. Não é necessário desfazer essa saída.
- Mantenha a saída independente do locale. Preserve a diferença entre o byte `0xff` e o fim do arquivo.
- Entregue o código-fonte, as instruções de compilação, os testes e uma explicação das decisões.

## Casos de teste

| Vetor público | Comportamento esperado |
|---|---|
| `bytes-0` | Entrada vazia produz nenhuma linha. |
| `bytes-1`, `bytes-15` | A última linha recebe campos vazios na coluna hexadecimal. |
| `bytes-16`, `bytes-17` | Linha completa e transição para o offset `00000010`. |
| `bytes-256` | Todos os valores de byte, inclusive `00` e `ff`. |
| `file` | Os bytes vêm do caminho passado como argumento. |
| `missing`, `args` | Rejeição de arquivo inexistente e de excesso de argumentos. |
| `io-full`, `io-directory`, `io-broken-pipe` | Falha de I/O produz erro com diagnóstico. |

O gerador `materials/generate.py TAMANHO` escreve bytes cíclicos de 0 a 255, até 16777216 bytes, sem carregar tudo na memória.

Os vetores públicos ficam em `tests/cases.json`. O [guia de testes](README.md) contém os comandos de compilação e execução. Passe todos os vetores e acrescente casos próprios.

## Extensões opcionais

- Acrescente opções de largura ou agrupamento em um modo separado. Mantenha a saída padrão intacta.
- Destaque bytes imprimíveis com cores somente com uma opção explícita.
- Compare a representação hexadecimal com a representação Base64 dos mesmos dados.

As extensões não fazem parte dos critérios básicos.

## Como participar

Compartilhe sua implementação no fórum de desafios do Discord, com um caso de fronteira que você testou. Dúvidas, descobertas e soluções parciais também são bem-vindas.
