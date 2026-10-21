---
title: '#13 — Inspetor de um formato documentado'
slug: '013-record-inspector'
summary: 'Leia um formato binário de registros documentado, mostre campos e offsets e rejeite arquivos inconsistentes.'
publishedAt: 2026-10-20
updatedAt: 2026-10-20
draft: false
difficulty: beginner
categories: [build]
participation: open
recommendedLanguage: C
acceptedLanguages: [C, Rust]
cardTopics: ['Formatos binários', 'Validação', 'Little endian']
topics: ['Formatos binários', 'Little endian', 'Validação de limites', 'Offsets', 'Inteiros de largura fixa']
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
**Conceitos:** Formatos binários, little endian, validação de limites, offsets e inteiros de largura fixa.

## O desafio

Construa um inspetor para o formato didático REC1.

A ferramenta mostra os campos e seus offsets. Ela reconhece arquivos truncados ou inconsistentes e não interpreta bytes ausentes como dados.

Pré-requisitos: arrays, leitura binária, ponteiros e inteiros de largura fixa. O material não depende de outro desafio.

## Especificação

Execute `oxide-record-inspector` sem argumentos. Leia até 65536 bytes de `stdin`. Escreva o relatório ASCII em `stdout`.

O cabeçalho contém quatro bytes ASCII `REC1`, seguidos da contagem de registros: um inteiro sem sinal de 16 bits em little endian. Cada registro contém:

| Campo | Tamanho | Interpretação |
|---|---|---|
| Tipo | 1 byte | Inteiro sem sinal. Qualquer valor é permitido. |
| Comprimento | 2 bytes | Inteiro sem sinal em little endian. |
| Dados | Comprimento bytes | Bytes arbitrários, inclusive `00`. |

Contagem zero e comprimento zero são válidos. Não há padding, separadores ou bytes finais. A contagem corresponde exatamente aos registros presentes. Cada campo e cada payload está completo.

A primeira linha da saída é `count=N\n`. Para cada registro, escreva `offset=O type=T length=L data=HEX\n`. N, O, T e L são decimais sem sinal. O offset parte de zero e aponta para o byte do tipo. HEX usa dois dígitos minúsculos por byte, sem separador. Dados vazios deixam o campo vazio.

O helper [read_le.h](materials/read_le.h) lê inteiros little endian. Verifique os limites antes de chamar o helper.

## Exemplo

O arquivo [example.rec](materials/example.rec) contém:

```text
52 45 43 31 02 00 07 02 00 41 00 02 01 00 ff
```

Execute:

```sh
./oxide-record-inspector < materials/example.rec
```

Saída exata:

```text
count=2
offset=6 type=7 length=2 data=4100
offset=11 type=2 length=1 data=ff
```

## Requisitos

- Implemente em C11 ou Rust estável, apenas com a biblioteca padrão. Trate bytes como valores de 8 bits.
- Valide cabeçalho, contagem, comprimentos e fim exato do arquivo antes de aceitar a entrada.
- Retorne status zero somente no sucesso. Escreva em `stdout` apenas o relatório especificado.
- Em argumento, formato ou limite inválido, ou falha de leitura ou escrita, escreva um diagnóstico em `stderr` e retorne status diferente de zero.
- Uma falha pode deixar saída parcial. Não é necessário desfazer essa saída.
- Entregue implementação, regressões e a justificativa dos limites e dos acessos ao buffer.

## Casos de teste

| Caso | Resultado esperado |
|---|---|
| `REC1` seguido de contagem zero | `count=0` e LF. |
| Dois registros do exemplo | Campos, dados e offsets exatos. |
| Registro com comprimento zero | Aceitar e escrever `data=` vazio. |
| Cabeçalho ou payload truncado | Rejeitar. |
| Contagem maior que os registros presentes | Rejeitar. |
| Comprimento maior que os bytes restantes | Rejeitar. |
| Bytes após o último registro | Rejeitar. |
| Erro de leitura, escrita ou pipe fechado | Falhar com diagnóstico. |

Os vetores públicos ficam em `tests/cases.json`. O [guia de testes](README.md) contém os comandos de compilação e execução. Passe todos os vetores e acrescente casos próprios.

## Extensões opcionais

- Acrescente uma visualização de offsets para estudo, em uma ferramenta separada.
- Gere arquivos REC1 aleatórios e teste truncamentos em cada posição.

As extensões preservam a interface e a saída do inspetor base.

## Como participar

Compartilhe sua implementação no fórum de desafios do Discord, com um arquivo malformado que ela rejeita. Dúvidas, descobertas e soluções parciais também são bem-vindas.
