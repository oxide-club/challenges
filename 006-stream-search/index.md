---
title: '#6 — Busca de sequência em stream'
slug: '006-stream-search'
summary: 'Encontre todas as ocorrências de um padrão binário em fluxo, inclusive sobrepostas, em tempo linear.'
publishedAt: 2026-10-20
updatedAt: 2026-10-20
draft: false
difficulty: advanced
categories: [build]
participation: open
recommendedLanguage: C
acceptedLanguages: [C, Rust]
cardTopics: ['Bytes e fluxo', 'KMP', 'Complexidade linear']
topics: ['Processamento binário', 'Busca de padrões', 'KMP', 'Tabela de prefixos', 'Análise de algoritmos', 'Streams']
github:
  challenge: true
  solutions: [c]
  community: true
featured: false
environment: 'C11 ou Rust estável · Unix/Linux · bytes de 8 bits'
---

**Dificuldade:** Difícil  
**Linguagem recomendada:** C (C11)  
**Linguagens aceitas:** C (C11) e Rust (estável)  
**Conceitos:** Busca de padrões, KMP, tabela de prefixos, análise de algoritmos e streams.

## O desafio

Uma sequência pode começar no fim de um bloco de leitura e terminar no bloco seguinte.

Implemente o `oxide-stream-search`. A ferramenta encontra todas as ocorrências de um padrão binário sem carregar a entrada inteira na memória.

O objetivo é preservar o estado entre blocos e justificar o tempo linear, inclusive para padrões repetitivos. Pré-requisitos: arrays, ponteiros e análise de algoritmos.

## Especificação

Aceite exatamente um argumento:

```sh
oxide-stream-search PADRAO_HEX
```

O padrão é uma sequência hexadecimal não vazia, com quantidade par de dígitos de `0` a `9`, `a` a `f` ou `A` a `F`. Não aceite separadores nem o prefixo `0x`. Depois da decodificação, o padrão pode ocupar até 1 MiB (1048576 bytes).

Leia a entrada binária de `stdin`. Para cada ocorrência, escreva o offset em decimal seguido de `\n`. Os offsets começam em zero e aparecem em ordem crescente, inclusive nas ocorrências sobrepostas. Sem ocorrências, a saída é vazia. Todos os bytes são dados válidos, inclusive `00`. Aceite comprimentos de entrada representáveis em `uint64_t` e rejeite overflow.

Use KMP com uma tabela de prefixos e estado preservado entre blocos. Um algoritmo equivalente é aceito com uma demonstração de tempo O(n+m), com n bytes de entrada e m bytes de padrão. A memória adicional é O(m+B), com tamanho de bloco B fixo. Não carregue toda a entrada. Não reposicione o arquivo para reler bytes.

## Exemplo

No vetor `search1`, o padrão hexadecimal `616261` representa `aba`:

```sh
$ printf abababa | ./oxide-stream-search 616261
0
2
4
```

As ocorrências nas posições 0, 2 e 4 se sobrepõem. Todas fazem parte da resposta.

## Requisitos

- Implemente em C11 ou Rust estável, apenas com a biblioteca padrão. Trate bytes como valores de 8 bits.
- Não delegue o núcleo do exercício a funções ou ferramentas prontas de busca.
- Retorne status zero somente no sucesso. Escreva em `stdout` apenas o resultado especificado. Os testes não comparam `stderr` no sucesso.
- Em argumento inválido, padrão inválido ou falha de leitura, alocação ou escrita, escreva um diagnóstico em `stderr` e retorne status diferente de zero.
- Esvazie o buffer de saída antes de encerrar (`fflush` em C) e verifique o resultado. Trate pipe fechado com diagnóstico. Não encerre em silêncio por `SIGPIPE`.
- Uma falha pode deixar saída parcial. Não é necessário desfazer essa saída.
- Mantenha o estado da busca entre leituras e depois de cada ocorrência, inclusive nas sobrepostas.
- Explique por que o algoritmo não reexamina toda a entrada a cada recuo e como obtém o limite O(n+m). Os testes verificam os resultados. A revisão do código verifica a complexidade.
- Entregue o código-fonte, as instruções de compilação, os testes e a justificativa da complexidade.

## Casos de teste

| Vetor público | Entrada ou situação | Resultado |
|---|---|---|
| `search0` | Entrada vazia, padrão `61` | Saída vazia. |
| `search1` | `abababa`, padrão `616261` | Offsets 0, 2 e 4. |
| `search2` | `aaaaa`, padrão `616161` | Offsets 0, 1 e 2. |
| `search3` | Bytes `00 ff 00 ff`, padrão `00ff` | Offsets 0 e 2. |
| `search4` | 4095 bytes `x` seguidos de `abcdab`, padrão `61626364` | Offset 4095. A ocorrência atravessa o bloco de 4096 bytes. |
| `search5` | Prefixos repetidos, padrão `616261626163` | Offset 23996. |
| `search6` | Padrão maior que a entrada | Saída vazia. |
| `invalid0` a `invalid4` | Argumento ausente, padrão vazio, hexadecimal ímpar ou inválido, argumentos extras | Rejeição com diagnóstico. |

Os vetores também cobrem falhas de I/O. Use `materials/generate.py` para criar entradas maiores. Acrescente casos com fronteiras diferentes das fornecidas.

Os vetores públicos ficam em `tests/cases.json`. O [guia de testes](README.md) contém os comandos de compilação e execução. Passe todos os vetores e acrescente casos próprios.

## Extensões opcionais

- Compare a quantidade de comparações com uma busca ingênua em entradas repetitivas.
- Teste o mesmo fluxo com tamanhos internos de bloco diferentes.
- Projete uma interface separada para vários padrões. Não altere a interface básica.

As extensões não fazem parte dos critérios básicos.

## Como participar

Compartilhe sua implementação e a justificativa de complexidade no fórum de desafios do Discord, com uma ocorrência dividida entre duas leituras. Dúvidas, descobertas e soluções parciais também são bem-vindas.
