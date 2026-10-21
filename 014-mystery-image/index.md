---
title: 'Que arquivo é este?'
slug: '014-mystery-image'
area: binary-reverse-engineering
summary: 'Infira um formato de imagem desconhecido com experimentos controlados e escreva um leitor que exporta PPM.'
publishedAt: 2026-10-20
updatedAt: 2026-10-20
draft: false
difficulty: intermediate
categories: [investigate, build]
participation: flagship
recommendedLanguage: C
acceptedLanguages: [C, Rust]
cardTopics: ['Engenharia reversa', 'Hipóteses e evidências', 'Formatos binários']
topics: ['Engenharia reversa', 'Formatos binários', 'Método experimental', 'Ordem de bytes', 'PPM']
github:
  challenge: true
  solutions: [c]
  community: true
featured: false
environment: 'C11 ou Rust estável · Unix/Linux · bytes de 8 bits'
---

**Dificuldade:** Intermediário  
**Linguagem recomendada:** C (C11)  
**Linguagens aceitas:** C (C11) e Rust (estável)  
**Conceitos:** Engenharia reversa, formatos binários, método experimental, ordem de bytes e PPM.

## O desafio

Investigue um formato de imagem pequeno e desconhecido. Implemente um leitor que exporta PPM.

A entrega explica como as observações sustentam a especificação inferida.

Pré-requisitos: arrays, bytes, coordenadas e inteiros de largura fixa. O material não depende de outro desafio.

## Especificação

Execute `oxide-mystery-image` sem argumentos. Leia um arquivo `.px` de até 65536 bytes de `stdin`. Escreva uma imagem PPM P6 em `stdout`.

O formato investigado tem cabeçalho curto e pixels sem compressão. As dimensões válidas são positivas, com no máximo 64 pixels por eixo. Infira cabeçalho, dimensões, disposição dos pixels e ordem dos bytes. Rejeite arquivos inválidos ou com bytes finais.

A saída tem o cabeçalho exato `P6\nW H\n255\n`, com W e H em decimal. Depois vêm os bytes RGB, da esquerda para a direita e de cima para baixo, sem bytes finais.

O [corpus inicial](materials/README.md) traz pares `.px` e `.ppm`. Use o oráculo para solicitar novas amostras:

```sh
python3 materials/oracle.py W H RRGGBB... > consulta.px
```

Os pixels da consulta são RGB, em ordem de linhas. Trate o gerador como um instrumento de consulta. Não leia o código do gerador antes de concluir a investigação. O helper [write_ppm.py](materials/write_ppm.py) grava uma visualização com `python3 materials/write_ppm.py W H RGB_HEX saida.ppm`.

Compare pares que alteram uma propriedade por vez: largura, altura, vermelho, verde ou azul. Depois investigue um retângulo com pixels distintos. Registre hipótese, previsão, experimento e conclusão. Reserve cores e dimensões novas para conferir a especificação depois de formulada. Os casos de validação da suíte são separados do corpus inicial.

## Exemplo

O par inicial `red.px` e `red.ppm` representa um pixel vermelho. Execute:

```sh
./oxide-mystery-image < materials/red.px > resultado.ppm
cmp resultado.ppm materials/red.ppm
```

O PPM esperado contém o cabeçalho `P6\n1 1\n255\n` seguido dos três bytes `ff 00 00`. O exemplo documenta a saída pública sem revelar a estrutura do arquivo investigado.

## Requisitos

- Implemente em C11 ou Rust estável, apenas com a biblioteca padrão. Trate bytes como valores de 8 bits.
- Entregue o leitor, a especificação inferida e o registro das hipóteses, com evidências que diferenciem interpretações concorrentes.
- Valide com amostras novas, além do corpus inicial. Inclua regressões.
- Retorne status zero somente no sucesso. Escreva em `stdout` apenas a imagem PPM.
- Em argumento, formato ou limite inválido, ou falha de leitura ou escrita, escreva um diagnóstico em `stderr` e retorne status diferente de zero.
- Preserve bytes arbitrários nos pixels, inclusive `00`. Uma falha pode deixar saída parcial.
- Explique os limites e o mapeamento entre coordenadas e posições no arquivo.

## Casos de teste

| Caso | Resultado esperado |
|---|---|
| Pixel vermelho do corpus | PPM idêntico a `red.ppm`. |
| Imagem retangular do corpus | Dimensões e pixels idênticos ao PPM correspondente. |
| Novas dimensões e cores | Conversão coerente com a especificação inferida. |
| Dimensão zero ou acima de 64 | Rejeitar. |
| Cabeçalho inválido ou payload incompleto | Rejeitar. |
| Bytes finais adicionais | Rejeitar. |
| Erro de leitura, escrita ou pipe fechado | Falhar com diagnóstico. |

Os vetores públicos ficam em `tests/cases.json`. Reserve os vetores novos para a etapa de validação. O [guia de testes](README.md) contém os comandos de compilação e execução.

## Extensões opcionais

- Construa um encoder separado depois de validar a especificação inferida.
- Automatize a geração de pares que diferenciem duas hipóteses de disposição de pixels.

As extensões preservam o leitor e o contrato base da suíte.

## Como participar

Compartilhe a especificação inferida e o registro das hipóteses no fórum de desafios do Discord. Dúvidas, descobertas e soluções parciais também são bem-vindas.
