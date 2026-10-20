---
title: '#3 — Construa um compressor RLE'
slug: '003-rle'
summary: 'Comprima e descomprima bytes com RLE, processando streams e preservando exatamente os dados originais.'
publishedAt: 2026-10-20
updatedAt: 2026-10-20
draft: false
difficulty: advanced
categories: [build, investigate]
participation: open
recommendedLanguage: C
topics: ['Processamento binário', 'Codificação', 'Streams', 'Gerenciamento de estado']
github:
  challenge: true
  solutions: [c, rust]
  community: true
featured: false
environment: 'C11 ou Rust estável · Exemplos para terminais Unix/Linux'
---

**Dificuldade:** Avançado (primeiro mês)  
**Linguagem recomendada:** C (C11)  
**Linguagens aceitas:** C (C11) e Rust (estável)  
**Conceitos:** Processamento binário, codificação, streams e gerenciamento de estado.

## O desafio

O *Run-Length Encoding* (RLE) representa sequências de bytes repetidos por pares de **contagem e valor**.

Implemente o `oxide-rle`, capaz de comprimir e descomprimir sequências arbitrárias de bytes, preservando exatamente os dados originais.

## Especificação

O programa deve aceitar exatamente um argumento:

```bash
./oxide-rle encode
./oxide-rle decode
```

Nos dois modos, leia bytes de `stdin` e escreva bytes em `stdout`.

O formato comprimido consiste em pares consecutivos de **dois bytes**, sem cabeçalho:

- **Contagem:** um byte entre `1` e `255`.
- **Valor:** um byte entre `0x00` e `0xff`.

No modo `encode`, represente cada sequência máxima de bytes iguais por um par. Divida sequências com mais de 255 repetições em pares consecutivos. No modo `decode`, aceite qualquer sequência de pares válidos, inclusive pares adjacentes com o mesmo valor.

Um arquivo vazio produz uma saída vazia em ambos os modos.

### Exemplo

A entrada `AAAAABBBCC` deve gerar os bytes `05 41 03 42 02 43`:

```bash
$ printf 'AAAAABBBCC' | ./oxide-rle encode | od -An -tx1
 05 41 03 42 02 43
```

A descompressão deve reproduzir os bytes originais, sem acrescentar uma quebra de linha.

## Requisitos

- Implemente em C11 ou Rust estável, utilizando apenas a biblioteca padrão da linguagem e considerando bytes de 8 bits.
- Processe os dados incrementalmente, sem carregá-los integralmente na memória.
- Trate qualquer valor de byte como dado válido, inclusive `0x00`.
- Rejeite argumentos inválidos, contagem zero e pares incompletos.
- Em erros de formato, leitura ou escrita, informe o problema em `stderr` e retorne um status diferente de zero.
- Não utilize bibliotecas de compressão externas nem ferramentas prontas na implementação.

## Casos de teste

| Entrada original | Bytes comprimidos (hexadecimal) |
|---|---|
| Vazia | Vazia |
| `A` | `01 41` |
| `AAA` | `03 41` |
| `ABAB` | `01 41 01 42 01 41 01 42` |
| 255 bytes `A` | `ff 41` |
| 256 bytes `A` | `ff 41 01 41` |
| Bytes `00 00 ff` | `02 00 01 ff` |

No modo `decode`, rejeite `00 41` (contagem zero) e `03` (par incompleto).

Verifique também a propriedade:

```text
decode(encode(entrada)) == entrada
```

Ela deve valer para qualquer sequência de bytes, não apenas texto.

## Extensões opcionais

- Medir a razão de compressão.
- Aceitar caminhos de entrada e saída.
- Automatizar testes de ida e volta com dados aleatórios.
- Projetar um cabeçalho versionado e limitar o tamanho da descompressão.

## Como participar

Compartilhe sua implementação no fórum de desafios do Discord, com um teste de ida e volta e um caso de erro tratado corretamente. Dúvidas, descobertas e soluções parciais também são bem-vindas.
