---
title: '#2 — Gere uma imagem PPM'
slug: '002-ppm'
summary: 'Gere uma imagem PPM em C, calculando pixels RGB e escrevendo dados binários sem bibliotecas gráficas.'
publishedAt: 2026-10-20
updatedAt: 2026-10-20
draft: false
difficulty: intermediate
categories: [build, investigate]
participation: open
recommendedLanguage: C
topics: ['Representação binária', 'Pixels RGB', 'Coordenadas', 'Entrada e saída']
github:
  challenge: true
  solutions: [c]
  community: true
featured: false
environment: 'C11 · Exemplos para terminais Unix/Linux'
---

**Dificuldade:** Intermediário  
**Linguagem:** C (C11)  
**Conceitos:** Representação binária, pixels RGB, coordenadas e entrada e saída.

## O desafio

Uma imagem digital pode ser representada por uma sequência de pixels. Seu objetivo é construir o `oxide-ppm`, um programa que gera uma imagem no formato **PPM P6**, sem utilizar bibliotecas gráficas.

## Especificação

Ao ser executado sem argumentos, seu programa deve escrever em `stdout` uma imagem de **256 × 256 pixels**.

O arquivo deve começar com este cabeçalho ASCII, incluindo a quebra de linha após `255`:

```text
P6
256 256
255
```

Após o cabeçalho, escreva os pixels como bytes binários, sem separadores nem dados adicionais. Cada pixel ocupa **3 bytes**, na ordem vermelho, verde e azul (**RGB**).

Percorra a imagem da esquerda para a direita, de cima para baixo. Para cada pixel `(x, y)`, com coordenadas de `0` a `255`, utilize:

- **Vermelho:** `x`
- **Verde:** `y`
- **Azul:** `0`

## Requisitos

- Utilize C11 e sua biblioteca padrão.
- Não utilize bibliotecas gráficas ou de processamento de imagens.
- Gere a imagem sem armazená-la integralmente na memória.
- Escreva apenas os bytes do arquivo PPM em `stdout`.
- Em caso de erro de escrita, emita um diagnóstico em `stderr` e retorne um status diferente de zero.

Considere um ambiente Unix/Linux com bytes de 8 bits.

## Casos de teste

```bash
./oxide-ppm > imagem.ppm
wc -c < imagem.ppm
# 196623
```

| Propriedade | Valor esperado |
|---|---|
| Cabeçalho | `P6\n256 256\n255\n` (15 bytes) |
| Dados dos pixels | `196608` bytes |
| Pixel `(0, 0)` | `00 00 00` |
| Pixel `(255, 0)` | `ff 00 00` |
| Pixel `(0, 255)` | `00 ff 00` |
| Pixel `(255, 255)` | `ff ff 00` |

O arquivo deve ser aberto corretamente por um visualizador compatível com PPM P6.

## Extensões opcionais

1. **Padrões:** gere um tabuleiro, listras, círculos ou outras figuras.
2. **Dimensões:** aceite largura e altura como argumentos.
3. **Formatos:** implemente também PPM P3 e compare os arquivos.
4. **Investigação:** experimente comprimir imagens produzidas pelo seu programa utilizando RLE.

## Como participar

Compartilhe sua implementação no fórum de desafios do Discord, acompanhada de uma imagem gerada e de uma descoberta ou dificuldade encontrada.

**Não é necessário concluir o desafio para participar.** Experimentos, dúvidas e soluções parciais também são contribuições válidas.

## Precisa de uma dica?

Está com dificuldades ou não sabe por onde começar?

Preparamos **três dicas progressivas**, ocultas como spoilers no tópico oficial do desafio.

[Acesse as dicas no Discord](https://discord.com/channels/1561460326136811570/1561951075441967157)

Você também pode compartilhar suas imagens, dúvidas e descobertas na mesma discussão.
