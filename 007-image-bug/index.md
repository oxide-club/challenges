---
title: 'Pixels fora do lugar'
slug: '007-image-bug'
area: graphics
summary: 'Reproduza, explique e corrija um erro de mapeamento de pixels que só aparece em imagens retangulares.'
publishedAt: 2026-10-20
updatedAt: 2026-10-20
draft: false
difficulty: beginner
categories: [debug, investigate]
participation: flagship
recommendedLanguage: C
acceptedLanguages: [C, Rust]
cardTopics: ['Imagens e coordenadas', 'Debugging', 'Regressão']
topics: ['Debugging', 'Stride', 'Coordenadas', 'PPM', 'Teste de regressão']
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
**Conceitos:** Debugging, stride, coordenadas, PPM e teste de regressão.

## O desafio

O programa em `materials/buggy.c` copia uma imagem pixel por pixel. Uma imagem retangular sai diferente da original.

Investigue o comportamento, formule uma hipótese e corrija o defeito. Entregue a correção com um teste de regressão.

O starter compila e mantém os acessos dentro do buffer. O objetivo é diagnosticar um erro de resultado, sem comportamento indefinido. Pré-requisitos: arrays, índices e I/O básico.

## Especificação

A interface corrigida é:

```sh
oxide-image-bug < entrada.ppm > saida.ppm
```

Não aceite argumentos. Leia uma imagem de `stdin`. Escreva em `stdout` uma imagem com as mesmas dimensões e exatamente os mesmos bytes RGB, pixel por pixel. A cópia por coordenadas é intencional. Preserve esse trabalho no patch.

O formato de imagem é um subconjunto estrito de [PPM P6](https://netpbm.sourceforge.net/doc/ppm.html). O cabeçalho contém exatamente `P6\nW H\n255\n`. Cada dimensão tem de um a três dígitos decimais, valor entre 1 e 256, e pode ter zeros iniciais. Depois do cabeçalho vêm exatamente W×H×3 bytes, em ordem de linhas, com os canais vermelho, verde e azul de cada pixel. Não há comentários, CRLF, espaços extras no cabeçalho, imagens concatenadas ou bytes finais. O primeiro byte do raster pode ter qualquer valor, inclusive espaço ou quebra de linha. A saída usa o mesmo formato, com dimensões sem zeros iniciais.

O arquivo `materials/ppm.h` fornece o tipo `Image`, a leitura (`ppm_read`) e a gravação (`ppm_write`). Use esses materiais para concentrar a investigação no processamento dos pixels.

A entrega contém o contraexemplo, a hipótese investigada, a causa identificada, o patch e um teste que falha no original e passa na versão corrigida. Compare também um caso quadrado. Explique, depois da investigação, por que o caso quadrado não revela o problema.

## Exemplo

O arquivo `materials/labels-3x2.ppm` contém este arranjo de cores:

```text
vermelho  verde    azul
amarelo   magenta  ciano
```

Após o cabeçalho `P6\n3 2\n255\n`, os bytes esperados são:

```text
ff 00 00  00 ff 00  00 00 ff
ff ff 00  ff 00 ff  00 ff ff
```

Compile e execute o original antes de editar:

```sh
cc -std=c11 -Wall -Wextra -Wpedantic -Werror -I materials materials/buggy.c -o /tmp/buggy
/tmp/buggy < materials/labels-3x2.ppm > /tmp/observada.ppm
cmp materials/labels-3x2.ppm /tmp/observada.ppm
```

A comparação aponta uma diferença. A versão corrigida produz um arquivo idêntico para essa entrada, porque o cabeçalho já é canônico. Registre suas previsões antes de examinar os bytes observados.

## Requisitos

- Implemente em C11 ou Rust estável, apenas com a biblioteca padrão. Trate bytes como valores de 8 bits.
- Execute o original primeiro e registre uma hipótese antes do patch. Rastreie coordenadas e posições dos pixels em um exemplo pequeno.
- Mantenha os acessos válidos. Não introduza comportamento indefinido para reproduzir ou corrigir a falha.
- Retorne status zero somente no sucesso. Escreva em `stdout` apenas o resultado especificado. Os testes não comparam `stderr` no sucesso.
- Em argumento inválido, formato inválido ou falha de leitura, alocação ou escrita, escreva um diagnóstico em `stderr` e retorne status diferente de zero.
- Esvazie o buffer de saída antes de encerrar (`fflush` em C) e verifique o resultado. Trate pipe fechado com diagnóstico. Não encerre em silêncio por `SIGPIPE`.
- Uma falha pode deixar saída parcial. Não é necessário desfazer essa saída.
- Entregue uma regressão retangular que diferencie as duas versões. Apoie a explicação nos resultados, não apenas na aparência da imagem.
- Entregue o código-fonte, as instruções de compilação, os testes e o relato da investigação.

## Casos de teste

| Material ou vetor | O que verificar |
|---|---|
| `materials/labels-3x2.ppm` | Contraexemplo visual rotulado. O original altera pixels. |
| `image3x2` | Regressão retangular com comparação exata dos bytes. |
| `image2x2` | Caso quadrado. O original passa nele. A versão corrigida também. |
| `image1x4`, `image4x1`, `image1x1` | Dimensões estreitas e pixel único. |
| `badppm0` a `badppm6` | Rejeição de cabeçalho inválido, dimensão zero, maxval diferente de 255, raster truncado ou bytes extras. |
| `io-full`, `io-directory`, `io-broken-pipe` | Diagnóstico de falhas de leitura e escrita. |

O arquivo `materials/square-2x2.ppm` permite reproduzir o contraste entre as duas formas de imagem. As duas imagens usam cores próprias. Não confunda uma com a outra.

Execute a suíte primeiro contra `/tmp/buggy` e depois contra o programa corrigido. Preserve a evidência de que a regressão distingue as versões.

Os vetores públicos ficam em `tests/cases.json`. O [guia de testes](README.md) contém os comandos de compilação e execução. Passe todos os vetores e acrescente casos próprios.

## Extensões opcionais

- Automatize comparações para todas as dimensões pequenas, com pixels distinguíveis.
- Registre o percurso dos pixels em um arquivo de diagnóstico separado da saída PPM.
- Acrescente uma visualização das coordenadas ao relato de investigação.

As extensões não substituem o contraexemplo, a explicação da causa e o patch.

## Como participar

Compartilhe a investigação e a regressão no fórum de desafios do Discord. Dúvidas, descobertas e soluções parciais também são bem-vindas.
