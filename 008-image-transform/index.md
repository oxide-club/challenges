---
title: 'Recorte e gire uma imagem'
slug: '008-image-transform'
area: graphics
summary: 'Implemente recorte retangular e rotação de 90 graus com mapeamento exato de coordenadas.'
publishedAt: 2026-10-20
updatedAt: 2026-10-20
draft: false
difficulty: intermediate
categories: [build]
participation: open
recommendedLanguage: C
acceptedLanguages: [C, Rust]
cardTopics: ['Imagens e coordenadas', 'Rotação', 'Recorte']
topics: ['Coordenadas', 'Recorte', 'Rotação', 'Mapeamento inverso', 'PPM', 'Validação']
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
**Conceitos:** Coordenadas, recorte, rotação, mapeamento inverso e PPM.

## O desafio

Recortar e girar imagens exige transformar coordenadas sem perder a ordem dos pixels.

Implemente o `oxide-image-transform`, com duas operações independentes: recorte retangular e rotação de 90 graus no sentido horário.

A leitura e a gravação PPM são fornecidas. O trabalho se concentra no mapeamento dos pixels. Pré-requisitos: arrays, índices e I/O básico.

## Especificação

Aceite uma das duas formas. Leia a imagem de `stdin` e escreva o resultado em `stdout`:

```sh
oxide-image-transform crop X Y W H
oxide-image-transform rotate
```

A origem (0,0) fica no canto superior esquerdo. O eixo x cresce para a direita e o eixo y cresce para baixo.

Em `crop`, os quatro argumentos são inteiros decimais sem sinal, com valor até 256. W e H são positivos. O retângulo inclui x em [X,X+W) e y em [Y,Y+H). Rejeite qualquer recorte que ultrapasse a imagem. A saída tem dimensões W×H. O pixel (x,y) da saída recebe o pixel (X+x,Y+y) da entrada.

Em `rotate`, gire exatamente 90 graus no sentido horário. Para uma entrada de largura w e altura h, a saída tem largura h e altura w. O pixel (x,y) da saída recebe o pixel (y,h−1−x) da entrada. Não recorte nessa operação. Não combine as duas operações em uma invocação. Não há interpolação: copie cada pixel inteiro.

O formato de imagem é um subconjunto estrito de [PPM P6](https://netpbm.sourceforge.net/doc/ppm.html). O cabeçalho contém exatamente `P6\nW H\n255\n`. Cada dimensão tem de um a três dígitos decimais, valor entre 1 e 256, e pode ter zeros iniciais. Depois do cabeçalho vêm exatamente W×H×3 bytes, em ordem de linhas, com os canais vermelho, verde e azul de cada pixel. Não há comentários, CRLF, espaços extras no cabeçalho, imagens concatenadas ou bytes finais. O primeiro byte do raster pode ter qualquer valor, inclusive espaço ou quebra de linha. A saída usa o mesmo formato, com dimensões sem zeros iniciais.

O arquivo `materials/ppm.h` fornece `Image`, `ppm_read` e `ppm_write`. Use esse apoio. O tempo é proporcional ao número de pixels processados. A memória pode ocupar O(w×h).

## Exemplo

A imagem `materials/labels-3x2.ppm`, usada pelos vetores `rotate` e `crop`, tem esta disposição:

```text
vermelho  verde    azul
amarelo   magenta  ciano
```

O comando abaixo produz uma imagem 2×3:

```sh
./oxide-image-transform rotate < materials/labels-3x2.ppm > /tmp/girada.ppm
```

Os pixels esperados, por linha, são:

```text
amarelo  vermelho
magenta  verde
ciano    azul
```

O comando `crop 1 0 2 2` produz uma imagem 2×2 com verde e azul na primeira linha e magenta e ciano na segunda.

## Requisitos

- Implemente em C11 ou Rust estável, apenas com a biblioteca padrão. Trate bytes como valores de 8 bits.
- Não delegue o núcleo do exercício a bibliotecas prontas de imagem.
- Implemente as duas operações separadamente. Rejeite nome de operação, quantidade de argumentos e números inválidos.
- Preserve os três canais de cada pixel. Verifique os limites do recorte antes de acessar a imagem.
- Retorne status zero somente no sucesso. Escreva em `stdout` apenas o resultado especificado. Os testes não comparam `stderr` no sucesso.
- Em argumento inválido, formato inválido ou falha de leitura, alocação ou escrita, escreva um diagnóstico em `stderr` e retorne status diferente de zero.
- Esvazie o buffer de saída antes de encerrar (`fflush` em C) e verifique o resultado. Trate pipe fechado com diagnóstico. Não encerre em silêncio por `SIGPIPE`.
- Uma falha pode deixar saída parcial. Não é necessário desfazer essa saída.
- Explique o mapeamento de coordenadas, inclusive a troca de dimensões na rotação.
- Entregue o código-fonte, as instruções de compilação, os testes e uma explicação das decisões.

## Casos de teste

| Vetor público | Operação | Resultado esperado |
|---|---|---|
| `rotate` | Rotação da imagem rotulada 3×2 | Imagem 2×3 conforme o exemplo. |
| `crop` | `crop 1 0 2 2` | Verde e azul, magenta e ciano, em uma imagem 2×2. |
| `identity` | Recorte da imagem inteira | Pixels e dimensões preservados. |
| `last` | `crop 2 1 1 1` | Um único pixel ciano. |
| `rotate-1x3`, `rotate-3x1`, `rotate-1x1` | Imagens estreitas e pixel único | Dimensões trocadas. Bytes de pixel iguais a whitespace preservados. |
| `invalid0` a `invalid5` | Recorte fora da imagem, tamanho zero, número negativo ou malformado, argumentos incorretos | Rejeição com diagnóstico. |
| `badppm0` a `badppm6` | PPM malformado ou incompleto | Rejeição. |

Os vetores também cobrem falhas de I/O. Compare os arquivos byte a byte, além de abrir as imagens em um visualizador.

Os vetores públicos ficam em `tests/cases.json`. O [guia de testes](README.md) contém os comandos de compilação e execução. Passe todos os vetores e acrescente casos próprios.

## Extensões opcionais

- Verifique que quatro rotações de 90 graus recuperam a imagem original.
- Acrescente espelhamento ou rotações de 180 e 270 graus como operações novas. Preserve as duas interfaces básicas.
- Projete uma transformação com menos memória e documente as restrições de acesso à entrada.

As extensões não fazem parte dos critérios básicos.

## Como participar

Compartilhe sua implementação no fórum de desafios do Discord, com um exemplo não quadrado e uma rejeição de recorte. Dúvidas, descobertas e soluções parciais também são bem-vindas.
