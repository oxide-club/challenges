---
title: '#9 — Rasterizador de triângulos 2D'
slug: '009-triangle'
summary: 'Desenhe triângulos com cores por vértice, amostragem no centro do pixel e regra fixa de bordas.'
publishedAt: 2026-10-20
updatedAt: 2026-10-20
draft: false
difficulty: advanced
categories: [build]
participation: open
recommendedLanguage: C
acceptedLanguages: [C, Rust]
cardTopics: ['Imagens e coordenadas', 'Baricêntricas', 'Cobertura de bordas']
topics: ['Rasterização', 'Coordenadas baricêntricas', 'Função de aresta', 'Interpolação RGB', 'Arredondamento', 'PPM']
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
**Conceitos:** Rasterização, coordenadas baricêntricas, função de aresta, interpolação RGB e PPM.

## O desafio

Um rasterizador decide quais pixels pertencem a uma figura e qual cor cada pixel recebe.

Implemente o `oxide-triangle`. A ferramenta desenha triângulos 2D com cores RGB por vértice em uma imagem limitada.

O desafio está na cobertura das bordas, na interpolação e nos casos fora da tela. Pré-requisitos: arrays, determinantes e coordenadas baricêntricas. Não há câmera nem pipeline 3D.

## Especificação

Execute sem argumentos. A entrada em `stdin` é texto ASCII: `W H N`, seguido de N triângulos. Cada triângulo contém três vértices `x y r g b`, em um total de quinze inteiros.

Separe tokens com whitespace ASCII: espaço, tab, CR, LF, VT ou FF. Cada inteiro contém um sinal `-` opcional seguido de um ou mais dígitos. O sinal `+` não é aceito. Não há comentários. Rejeite tokens extras, ausentes ou inválidos. Os limites são:

| Campo | Intervalo |
|---|---|
| W e H | 1 a 256 |
| N | 0 a 1000 |
| x e y de cada vértice | −1024 a 1024 |
| r, g e b | 0 a 255 |

A saída é uma imagem P6 W×H, inicialmente preta. A origem fica no canto superior esquerdo. O eixo x cresce para a direita e o eixo y cresce para baixo. Processe os triângulos na ordem recebida. Onde houver cobertura, o triângulo mais recente substitui a cor anterior.

Para fixar a cobertura sem ambiguidade, defina a função de aresta:

```text
E(a,b,p) = (bx−ax)(py−ay) − (by−ay)(px−ax)
```

Calcule A=E(a,b,c). Se A=0, ignore o triângulo degenerado. Se A<0, troque b e c, com as respectivas cores, para que a área usada seja positiva.

Amostre o pixel (x,y) no centro p=(x+0.5,y+0.5). Uma aresta dirigida u→v aceita p quando E(u,v,p)>0. Quando E=0, a aresta aceita p somente se **`vy<uy` ou (`vy=uy` e `vx>ux`)**. O pixel é coberto somente se as três arestas o aceitam. Assim, uma borda compartilhada pertence a apenas uma face, inclusive quando passa pelo centro de um pixel.

Os pesos dos vértices a, b e c são, respectivamente, E(b,c,p)/A, E(c,a,p)/A e E(a,b,p)/A. Interpole cada canal RGB com esses pesos. Arredonde ao inteiro mais próximo, com empates para cima: `floor(valor+0.5)`. Dobre as coordenadas das amostras para calcular com inteiros. Use produtos de 64 bits para respeitar todos os limites.

Escreva apenas dentro do canvas. Partes externas de um triângulo não geram pixels fora dele. Não implemente perspectiva, câmera, mistura de cores entre faces, antialiasing nem profundidade.

O formato de imagem é um subconjunto estrito de [PPM P6](https://netpbm.sourceforge.net/doc/ppm.html). O cabeçalho contém exatamente `P6\nW H\n255\n`, com dimensões sem zeros iniciais. Depois do cabeçalho vêm exatamente W×H×3 bytes, em ordem de linhas, com os canais vermelho, verde e azul de cada pixel. Não há comentários, CRLF, espaços extras no cabeçalho ou bytes finais.

O arquivo `materials/ppm.h` fornece `Image` e `ppm_write`. A entrada é o texto descrito acima, não uma imagem PPM.

## Exemplo

O arquivo `materials/triangle.txt` e o vetor `triangle1` descrevem uma imagem 3×3 com um triângulo:

```text
3 3 1
0 0 255 0 0
3 0 0 255 0
0 3 0 0 255
```

Execute:

```sh
./oxide-triangle < materials/triangle.txt > /tmp/triangulo.ppm
cmp /tmp/triangulo.ppm materials/triangle.ppm
```

Após o cabeçalho `P6\n3 3\n255\n`, os pixels esperados, em hexadecimal RGB, são:

```text
aa 2b 2b  55 80 2b  00 00 00
55 2b 80  00 00 00  00 00 00
00 00 00  00 00 00  00 00 00
```

O primeiro pixel resulta em RGB (170,43,43). Esse valor também ilustra o arredondamento.

## Requisitos

- Implemente em C11 ou Rust estável, apenas com a biblioteca padrão. Trate bytes como valores de 8 bits.
- Não delegue o núcleo do exercício a bibliotecas prontas de gráficos.
- Aplique exatamente a amostragem no centro, a regra de empate das arestas e o arredondamento definidos. Explique por que duas faces adjacentes não disputam a mesma borda.
- Respeite os limites de coordenadas sem overflow nos produtos. Preserve as cores ao normalizar a orientação. Ignore faces degeneradas.
- Retorne status zero somente no sucesso. Escreva em `stdout` apenas o resultado especificado. Os testes não comparam `stderr` no sucesso.
- Em entrada inválida ou falha de leitura, alocação ou escrita, escreva um diagnóstico em `stderr` e retorne status diferente de zero.
- Esvazie o buffer de saída antes de encerrar (`fflush` em C) e verifique o resultado. Trate pipe fechado com diagnóstico. Não encerre em silêncio por `SIGPIPE`.
- Uma falha pode deixar saída parcial. Não é necessário desfazer essa saída.
- Entregue testes para interpolação, orientação invertida, clipping e bordas compartilhadas. Comparação visual sozinha não basta.
- Entregue o código-fonte, as instruções de compilação, os testes e uma explicação das decisões.

## Casos de teste

| Vetor público | O que verifica |
|---|---|
| `triangle0` | Canvas preto com zero triângulos. |
| `triangle1` | Interpolação e arredondamento do exemplo. |
| `triangle2` | Mesma imagem com orientação dos vértices invertida. |
| `triangle3` | Triângulo degenerado não altera o canvas. |
| `triangle4` | Triângulo parcialmente fora da imagem. |
| `triangle5`, `triangle6` | Faces adjacentes em ordens opostas produzem a mesma imagem, inclusive na diagonal compartilhada. |
| `rational-corpus` | Vinte faces com clipping e cores, conferidas com frações exatas. |
| `coordinate-limits-overflow` | Canvas 1×1 e vértices nos limites ±1024. O único pixel é branco (`ff ff ff`). |
| `invalid0` a `invalid7` | Entrada incompleta, limites inválidos e tokens extras. |

O caso nos limites detecta produtos com largura insuficiente. Os vetores incluem falhas de I/O. O arquivo `materials/oracle.py` é um oráculo lento com frações exatas para entradas válidas pequenas. Ele não valida texto malformado.

Os vetores públicos ficam em `tests/cases.json`. O [guia de testes](README.md) contém os comandos de compilação e execução. Passe todos os vetores e acrescente casos próprios.

## Extensões opcionais

- Restrinja a iteração ao retângulo delimitador do triângulo. Compare com a versão que examina todo o canvas.
- Gere pares de faces adjacentes em orientações diferentes para ampliar a regressão de bordas.
- Acrescente um modo de visualização dos pesos baricêntricos. Preserve a saída básica.

As extensões não alteram a cobertura nem o arredondamento exigidos.

## Como participar

Compartilhe sua implementação e a explicação de um caso de borda no fórum de desafios do Discord. Dúvidas, descobertas e soluções parciais também são bem-vindas.
