---
title: 'Gere uma imagem PPM'
slug: '002-ppm'
area: graphics
summary: 'Crie uma imagem calculando as cores de cada pixel e escrevendo o resultado em um arquivo PPM.'
publishedAt: 2026-10-20
updatedAt: 2026-10-20
draft: false
difficulty: intermediate
categories: [build, investigate]
participation: open
recommendedLanguage: C
acceptedLanguages: [C]
cardTopics: ['Imagens e coordenadas', 'Pixels RGB', 'Escrita binária']
topics: ['Pixels RGB', 'Coordenadas', 'PPM P6', 'Escrita binária', 'Erros de escrita']
github:
  challenge: true
  solutions: [c]
  community: true
featured: true
environment: 'C11 · Unix/Linux · bytes de 8 bits'
---

**Dificuldade:** Intermediário  
**Linguagem recomendada:** C (C11)  
**Linguagens aceitas:** C (C11)  
**Conceitos:** Pixels RGB, coordenadas, PPM P6, escrita binária e erros de escrita.

## O desafio

Uma imagem digital pode ser uma sequência de pixels, cada um com três canais de cor.

Implemente o `oxide-ppm`. Gere uma imagem PPM P6 com as cores calculadas a partir das coordenadas, sem bibliotecas gráficas.

Pré-requisitos: laços, coordenadas e I/O básico. O objetivo é distinguir texto de cabeçalho e bytes de pixels.

## Especificação

Execute `oxide-ppm` sem argumentos. Escreva em `stdout` uma imagem de **256 × 256 pixels**. O programa não precisa ler `stdin`.

Comece com este cabeçalho ASCII exato, com LF após `255`:

```text
P6
256 256
255
```

Depois, escreva os pixels como bytes binários, sem separadores ou bytes finais. Cada pixel ocupa três bytes, na ordem vermelho, verde e azul (RGB).

Percorra a imagem da esquerda para a direita e de cima para baixo. A origem `(0, 0)` fica no canto superior esquerdo. Para cada pixel `(x, y)`, com coordenadas de 0 a 255, use:

- vermelho: `x`;
- verde: `y`;
- azul: `0`.

O cabeçalho ocupa 15 bytes. Os pixels ocupam 196608 bytes. O arquivo completo tem exatamente **196623 bytes**.

## Exemplo

```sh
./oxide-ppm > imagem.ppm
wc -c < imagem.ppm
# 196623
```

Abra `imagem.ppm` em um visualizador compatível com PPM P6. O canto superior esquerdo é preto. O superior direito é vermelho, e o inferior esquerdo é verde. O inferior direito é amarelo: vermelho e verde valem 255, e azul vale zero.

## Requisitos

- Implemente em C11, apenas com a biblioteca padrão, em Unix/Linux com bytes de 8 bits.
- Não use bibliotecas gráficas ou de processamento de imagens.
- Gere a imagem em fluxo, sem guardá-la inteira na memória. Use memória adicional constante.
- Escreva em `stdout` apenas os bytes do arquivo PPM. Não acrescente LF depois dos pixels.
- Retorne status zero somente no sucesso. Em erro de escrita, escreva um diagnóstico em `stderr` e retorne status diferente de zero.
- Esvazie o buffer de saída antes de encerrar e verifique o resultado de `fflush`. Uma falha pode aparecer somente nessa etapa.
- Entregue o código-fonte, as instruções de compilação, os testes e uma explicação da ordem dos pixels.

## Casos de teste

| Propriedade | Valor esperado |
|---|---|
| Cabeçalho | `P6\n256 256\n255\n` — 15 bytes. |
| Dados dos pixels | 196608 bytes. |
| Pixel `(0, 0)` | `00 00 00` |
| Pixel `(255, 0)` | `ff 00 00` |
| Pixel `(0, 255)` | `00 ff 00` |
| Pixel `(255, 255)` | `ff ff 00` |
| Erro de escrita em `/dev/full` | Status diferente de zero e diagnóstico em `stderr`. |

Compare todos os bytes, além de abrir a imagem em um visualizador. Uma imagem que parece correta pode ter cabeçalho, canais ou bytes finais incorretos.

Os vetores públicos ficam em `tests/cases.json`. O [guia de testes](README.md) contém os comandos de compilação e execução. Os [materiais](materials/README.md) fornecem a imagem esperada e seu gerador.

## Extensões opcionais

- Gere tabuleiro, listras ou círculos em um modo separado.
- Aceite largura e altura como argumentos opcionais.
- Implemente PPM P3 em outro modo e compare os arquivos.
- Compare a compressão RLE de imagens com padrões diferentes.

As extensões preservam a imagem e o formato da execução sem argumentos.

## Como participar

Compartilhe sua implementação no fórum de desafios do Discord, com a imagem gerada e uma descoberta. Dúvidas, experimentos e soluções parciais também são bem-vindas.

Consulte as [dicas progressivas no Discord](https://discord.com/channels/1561460326136811570/1561951075441967157) quando precisar de apoio.
