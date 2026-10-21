---
title: '#20 — Interpretador de expressões'
slug: '020-expressions'
summary: 'Interprete expressões inteiras com precedência, associatividade e parênteses, e rejeite sintaxe inválida.'
publishedAt: 2026-10-20
updatedAt: 2026-10-20
draft: false
difficulty: intermediate
categories: [build]
participation: open
recommendedLanguage: C
acceptedLanguages: [C, Rust]
cardTopics: ['Parsing', 'Precedência', 'Gramática']
topics: ['Parsing', 'Descida recursiva', 'Gramática', 'Precedência', 'Overflow de inteiros', 'Validação']
github:
  challenge: true
  solutions: [c]
  community: true
featured: false
environment: 'C11 ou Rust estável · Unix/Linux · inteiros de 32 bits'
---

**Dificuldade:** Intermediário  
**Linguagem recomendada:** C (C11)  
**Linguagens aceitas:** C (C11) e Rust (estável)  
**Conceitos:** Parsing, descida recursiva, gramática, precedência, overflow de inteiros e validação.

## O desafio

Implemente um interpretador de expressões inteiras com precedência e parênteses.

O objetivo é reconhecer a estrutura da expressão, calcular o valor e distinguir sintaxe inválida de uma conta válida.

Pré-requisitos: tokens, aritmética, arrays e parsing recursivo ou técnica equivalente. Há um [lexer inicial](materials/tokens.py) em Python. O material não depende de outro desafio.

## Especificação

Execute `oxide-expressions` sem argumentos. Leia até 65536 bytes de `stdin` e reconheça a gramática:

```text
expr = term { ("+" | "-") term }
term = atom { "*" atom }
atom = inteiro | "(" expr ")"
```

Literais são inteiros decimais não negativos, de 0 a 2147483647. Aceite espaços ASCII entre tokens: espaço, tabulação, CR, LF, FF e VT. A multiplicação tem precedência sobre soma e subtração. Operadores do mesmo nível associam à esquerda. Não há operadores unários, variáveis ou funções: `-1` é inválido e `0-1` é válido.

Resultados intermediários e final cabem em int32, de -2147483648 a 2147483647. Overflow é erro, mesmo se uma operação posterior pudesse voltar ao intervalo. Não execute aritmética com sinal que transborda. Aceite até 64 pares de parênteses abertos ao mesmo tempo. Rejeite profundidade maior.

Consuma toda a entrada. Entrada vazia, operando ausente, parênteses desequilibrados, caractere inválido e token excedente são erros. A saída válida é o resultado decimal seguido de LF em `stdout`.

## Exemplo

```sh
printf '2 + 3 * 4' | ./oxide-expressions
```

Saída:

```text
14
```

A expressão `(2 + 3) * 4` produz `20` seguido de LF. Em `9-3-2`, a associatividade à esquerda produz `(9-3)-2`, isto é, `4`.

## Requisitos

- Implemente em C11 ou Rust estável, apenas com a biblioteca padrão.
- Respeite a gramática, a precedência e a associatividade. Não introduza operador unário.
- Verifique os limites dos literais, dos resultados intermediários e da profundidade de parênteses.
- Retorne status zero somente no sucesso. Escreva em `stdout` apenas o resultado especificado.
- Em argumento, sintaxe ou limite inválido, ou falha de leitura ou escrita, escreva um diagnóstico em `stderr` e retorne status diferente de zero.
- Uma falha pode deixar saída parcial. Não é necessário desfazer essa saída.
- Entregue implementação, regressões e uma explicação da estratégia de parsing e dos limites adotados.

## Casos de teste

| Entrada ou situação | Resultado esperado |
|---|---|
| `2 + 3 * 4` | `14` e LF. |
| `(2 + 3) * 4` | `20` e LF. |
| `9-3-2` | `4` e LF. |
| `0-2147483647-1` | `-2147483648` e LF. |
| `2147483648` ou `2147483647+1` | Rejeitar limite numérico. |
| `-1` ou `1++2` | Rejeitar sintaxe. |
| `(2+3` ou `1 2` | Rejeitar entrada incompleta ou excedente. |
| 64 pares abertos ao mesmo tempo | Aceitar se a expressão é válida. |
| 65 pares abertos ao mesmo tempo | Rejeitar. |
| Entrada vazia ou byte zero | Rejeitar. |
| Erros de I/O | Falhar com diagnóstico. |

Os vetores públicos ficam em `tests/cases.json`. O [guia de testes](README.md) contém os comandos de compilação e execução. Passe todos os vetores e acrescente casos próprios.

## Extensões opcionais

- Gere uma árvore sintática para visualização em uma ferramenta separada.
- Acrescente mensagens de erro com a posição do token em `stderr`.

As extensões preservam a gramática, os limites e a saída base.

## Como participar

Compartilhe sua implementação e a estratégia de parsing no fórum de desafios do Discord. Inclua um caso que diferencia `2 + 3 * 4` de `(2 + 3) * 4`. Dúvidas, descobertas e soluções parciais também são bem-vindas.
