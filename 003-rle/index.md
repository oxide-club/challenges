---
title: 'Construa um compressor RLE'
slug: '003-rle'
area: algorithms-data-structures
summary: 'Implemente a compressão e a descompressão de sequências de bytes, recuperando exatamente os dados originais.'
publishedAt: 2026-10-20
updatedAt: 2026-10-20
draft: false
difficulty: advanced
categories: [build, investigate]
participation: open
recommendedLanguage: C
acceptedLanguages: [C, Rust]
cardTopics: ['Bytes e fluxo', 'Compressão sem perda', 'Validação']
topics: ['Compressão sem perda', 'RLE', 'Pares contagem/valor', 'Streams', 'Validação de formato']
github:
  challenge: true
  solutions: [c, rust]
  community: true
featured: true
environment: 'C11 ou Rust estável · Unix/Linux · bytes de 8 bits'
---

**Dificuldade:** Difícil  
**Linguagem recomendada:** C (C11)  
**Linguagens aceitas:** C (C11) e Rust (estável)  
**Conceitos:** Compressão sem perda, RLE, pares contagem/valor, streams e validação.

## O desafio

O *Run-Length Encoding* (RLE) representa sequências de bytes iguais por pares de contagem e valor.

Implemente o `oxide-rle`, com um compressor e um descompressor. A descompressão recupera exatamente os bytes originais, inclusive zeros e valores altos.

Pré-requisitos: laços, bytes, estado e I/O binário. O desafio combina processamento em fluxo e rejeição de entradas inválidas.

## Especificação

Aceite exatamente um dos modos:

```sh
oxide-rle encode
oxide-rle decode
```

Leia bytes de `stdin` e escreva o resultado em `stdout`, sem quebra de linha adicional. Entrada vazia produz saída vazia nos dois modos.

O formato comprimido contém pares consecutivos de dois bytes, sem cabeçalho:

- **Contagem:** um byte de 1 a 255.
- **Valor:** um byte de `00` a `ff`.

Em `encode`, represente cada sequência máxima de bytes iguais por um par. Se a sequência excede 255 bytes, emita pares de contagem 255 e um último par para o restante, se houver.

Em `decode`, aceite qualquer sequência de pares válidos, inclusive pares adjacentes com o mesmo valor. Repita o valor pela contagem indicada. Rejeite contagem zero e par incompleto.

Todos os valores de byte são dados válidos. O byte `00` não é terminador de texto. Processe a entrada em fluxo, sem carregar todos os dados na memória.

## Exemplo

A entrada `AAAAABBBCC` gera os bytes `05 41 03 42 02 43`:

```sh
printf 'AAAAABBBCC' | ./oxide-rle encode | od -An -tx1
# 05 41 03 42 02 43
```

O primeiro par representa cinco bytes `A`. Os outros pares representam três bytes `B` e dois bytes `C`. A descompressão produz `AAAAABBBCC`, sem LF final.

## Requisitos

- Implemente em C11 ou Rust estável, apenas com a biblioteca padrão e bytes de 8 bits.
- Mantenha o estado entre leituras. Use memória adicional constante.
- Não delegue a compressão a bibliotecas externas ou ferramentas prontas.
- Rejeite modo ausente, modo desconhecido, argumentos extras, contagem zero e pares incompletos.
- Retorne status zero somente no sucesso. Escreva em `stdout` apenas o resultado especificado.
- Em erro de formato, leitura ou escrita, escreva um diagnóstico em `stderr` e retorne status diferente de zero.
- Esvazie o buffer de saída antes de encerrar e verifique o resultado. Trate pipe fechado com diagnóstico.
- Uma falha pode deixar saída parcial. Não é necessário desfazer essa saída.
- Entregue o código-fonte, as instruções de compilação, os testes e uma explicação do estado usado nos dois modos.

## Casos de teste

| Entrada original | Bytes comprimidos em hexadecimal |
|---|---|
| Vazia | Saída vazia. |
| `A` | `01 41` |
| `AAA` | `03 41` |
| `ABAB` | `01 41 01 42 01 41 01 42` |
| 255 bytes `A` | `ff 41` |
| 256 bytes `A` | `ff 41 01 41` |
| Bytes `00 00 ff` | `02 00 01 ff` |

Em `decode`, rejeite `00 41` e `03`. Aceite `01 41 02 41` e produza `AAA`, apesar dos pares adjacentes com o mesmo valor.

Verifique também `decode(encode(entrada)) == entrada` com bytes arbitrários. Compare a codificação com a saída esperada antes da ida e volta. Erros complementares nos dois modos podem esconder uma codificação incorreta.

Os vetores públicos ficam em `tests/cases.json` e incluem limites de contagem, argumentos inválidos e falhas de I/O. O [guia de testes](README.md) contém os comandos. Os [materiais](materials/README.md) fornecem exemplos binários e seu gerador. Acrescente casos próprios.

## Extensões opcionais

- Meça a razão de compressão para padrões diferentes.
- Aceite caminhos de entrada e saída em uma interface separada.
- Gere testes de ida e volta com dados aleatórios determinísticos.
- Projete um cabeçalho versionado e um limite para o tamanho descomprimido em outro formato.

As extensões preservam os modos e o formato binário básicos.

## Como participar

Compartilhe sua implementação no fórum de desafios do Discord, com uma ida e volta e uma rejeição explicada. Dúvidas, descobertas e soluções parciais também são bem-vindas.
