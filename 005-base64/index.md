---
title: 'Base64 de ida e volta'
slug: '005-base64'
area: systems-fundamentals
summary: 'Codifique e decodifique bytes em Base64 com padding obrigatório e forma canônica estrita.'
publishedAt: 2026-10-20
updatedAt: 2026-10-20
draft: false
difficulty: intermediate
categories: [build]
participation: open
recommendedLanguage: C
acceptedLanguages: [C, Rust]
cardTopics: ['Bytes e fluxo', 'RFC 4648', 'Validação estrita']
topics: ['Processamento binário', 'Codificação', 'Base64', 'Padding', 'Operações com bits', 'Streams']
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
**Conceitos:** Codificação, Base64, operações com bits, validação e streams.

## O desafio

Base64 representa dados binários com os caracteres de um alfabeto fixo.

Implemente o `oxide-base64`, com um codificador e um decodificador. O decodificador recupera os bytes originais e rejeita representações inválidas ou não canônicas.

O desafio combina operações com bits, leitura em fluxo e validação. Pré-requisitos: laços, arrays e I/O binário.

## Especificação

Aceite exatamente um dos modos:

```sh
oxide-base64 encode
oxide-base64 decode
```

Leia bytes de `stdin` e escreva o resultado em `stdout`, sem quebra de linha adicional. Entrada vazia é válida e produz saída vazia nos dois modos.

Use o alfabeto padrão da [RFC 4648](https://www.rfc-editor.org/rfc/rfc4648.html):

```text
ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/
```

Em `encode`, represente cada grupo de três bytes por quatro símbolos. Complete o último grupo com `=` quando necessário: dois sinais para um byte restante, um sinal para dois bytes restantes.

Em `decode`, exija comprimento múltiplo de quatro e padding obrigatório nos grupos incompletos. O padding só pode aparecer no último quarteto, nas formas `xx==` ou `xxx=`. Em `xx==`, os quatro bits baixos do segundo sexteto são zero. Em `xxx=`, os dois bits baixos do terceiro sexteto são zero. Essa é a forma canônica exigida neste exercício.

Rejeite espaços, quebras de linha, caracteres fora do alfabeto, padding em posição errada, dados após o padding e bits de preenchimento diferentes de zero. Processe a entrada em fluxo, com tempo O(n) e memória adicional O(1).

## Exemplo

Os vetores `encode1` e `decode1` usam um byte, `f`:

```sh
$ printf f | ./oxide-base64 encode
Zg==
$ printf Zg== | ./oxide-base64 decode
f
```

As quebras de linha após os resultados acima são apenas a apresentação do exemplo. Os programas escrevem exatamente os quatro bytes `5a 67 3d 3d` e o byte `66`.

## Requisitos

- Implemente em C11 ou Rust estável, apenas com a biblioteca padrão. Trate bytes como valores de 8 bits.
- Não delegue o núcleo do exercício a ferramentas ou bibliotecas prontas de Base64.
- Retorne status zero somente no sucesso. Escreva em `stdout` apenas o resultado especificado. Os testes não comparam `stderr` no sucesso.
- Em argumento inválido, formato inválido ou falha de leitura, alocação ou escrita, escreva um diagnóstico em `stderr` e retorne status diferente de zero.
- Esvazie o buffer de saída antes de encerrar (`fflush` em C) e verifique o resultado. Trate pipe fechado com diagnóstico. Não encerre em silêncio por `SIGPIPE`.
- Uma falha pode deixar saída parcial. Não é necessário desfazer essa saída.
- Trate todos os bytes como dados, inclusive `00`. Valide também os bits descartados pelo padding.
- Entregue o código-fonte, as instruções de compilação, os testes e uma explicação das decisões.

## Casos de teste

| Entrada | Modo | Resultado |
|---|---|---|
| Vazia | `encode` ou `decode` | Saída vazia. |
| `f` | `encode` | `Zg==` |
| `fo` | `encode` | `Zm8=` |
| `foo` | `encode` | `Zm9v` |
| `foobar` | `encode` | `Zm9vYmFy` |
| Bytes de `00` a `ff` | Ida e volta nos vetores `encode7` e `decode7` | Recuperação exata dos 256 bytes. |
| `AB==`, `AAB=` | `decode` | Rejeição por bits de preenchimento não canônicos. |
| `AA=A`, `A===`, `AA==AA==` | `decode` | Rejeição de padding inválido. |
| `Zg==` seguido de `\n` | `decode` | Rejeição da quebra de linha. |

Verifique a propriedade `decode(encode(entrada)) == entrada` também com dados de `materials/generate.py`. Os vetores incluem outros caracteres inválidos, comprimentos incompletos, modo desconhecido e falhas de I/O.

Os vetores públicos ficam em `tests/cases.json`. O [guia de testes](README.md) contém os comandos de compilação e execução. Passe todos os vetores e acrescente casos próprios.

## Extensões opcionais

- Gere casos aleatórios determinísticos para verificar a propriedade de ida e volta.
- Meça a expansão de tamanho para entradas de comprimentos diferentes.
- Crie uma variante URL-safe como modo separado. Preserve o alfabeto e a validação estrita dos modos básicos.

As extensões não alteram o contrato original.

## Como participar

Compartilhe sua implementação no fórum de desafios do Discord, com um exemplo válido e uma rejeição explicada. Dúvidas, descobertas e soluções parciais também são bem-vindas.
