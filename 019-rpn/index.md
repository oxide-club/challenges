---
title: 'Calculadora RPN'
slug: '019-rpn'
area: languages-interpreters
summary: 'Avalie expressões em notação polonesa reversa (RPN) com uma pilha fixa e detecte tokens inválidos, falta de operandos e overflow.'
publishedAt: 2026-10-20
updatedAt: 2026-10-20
draft: false
difficulty: beginner
categories: [build]
participation: open
recommendedLanguage: C
acceptedLanguages: [C, Rust]
cardTopics: ['Pilha', 'Notação pós-fixa', 'Overflow']
topics: ['Pilha', 'Notação pós-fixa', 'Tokenização', 'Overflow de inteiros', 'Validação']
github:
  challenge: true
  solutions: [c]
  community: true
featured: false
environment: 'C11 ou Rust estável · Unix/Linux · inteiros de 32 bits'
---

**Dificuldade:** Fácil  
**Linguagem recomendada:** C (C11)  
**Linguagens aceitas:** C (C11) e Rust (estável)  
**Conceitos:** Pilha, notação pós-fixa, tokenização, overflow de inteiros e validação.

## O desafio

Implemente uma calculadora RPN com pilha fixa. RPN é a sigla de *Reverse Polish Notation*, a notação polonesa reversa. Nessa notação, o operador vem depois dos operandos: `3 4 +` calcula 3 + 4.

Além de calcular, detecte tokens inválidos, falta de operandos e operações fora do intervalo numérico.

Pré-requisitos: arrays, pilha, aritmética e I/O. O [trace inicial](materials/trace.md) mostra a evolução da pilha em um exemplo. O material não depende de outro desafio.

## Especificação

Execute `oxide-rpn` sem argumentos. Leia até 65536 bytes de `stdin`. Separe os tokens com um ou mais espaços ASCII: espaço, tabulação, CR, LF, FF ou VT. Aceite espaços antes e depois da expressão.

Um token inteiro contém um sinal `-` opcional seguido de um ou mais dígitos decimais. Não há `+` unário. Literais e resultados cabem em int32, de -2147483648 a 2147483647. Os operadores binários são `+`, `-` e `*`. Cada operador retira primeiro o operando direito b e depois o esquerdo a. Depois calcula a+b, a-b ou a*b.

Use uma pilha fixa de 64 valores. Rejeite:

- token inválido;
- literal fora do intervalo;
- menos de dois operandos para um operador;
- tentativa de empilhar o 65º valor;
- término com quantidade de valores diferente de um.

Entrada vazia é inválida. Qualquer resultado intermediário fora de int32 é erro. Não execute aritmética com sinal que transborda.

Uma expressão válida produz o resultado decimal seguido de um único LF em `stdout`. O processamento dos tokens custa O(n). A pilha usa O(64) de memória.

## Exemplo

```sh
printf '3 4 + 2 *' | ./oxide-rpn
```

Saída:

```text
14
```

A pilha evolui assim: `[3]`, `[3,4]`, `[7]`, `[7,2]`, `[14]`. Para conferir a ordem dos operandos, `3 7 -` produz `-4` seguido de LF.

## Requisitos

- Implemente em C11 ou Rust estável, apenas com a biblioteca padrão.
- Mantenha a pilha dentro da capacidade fixa de 64 valores.
- Verifique overflow dos literais e de cada operação antes de converter ou armazenar o resultado em int32.
- Retorne status zero somente no sucesso. Escreva em `stdout` apenas o resultado especificado.
- Em argumento, sintaxe ou limite inválido, ou falha de leitura ou escrita, escreva um diagnóstico em `stderr` e retorne status diferente de zero.
- Uma falha pode deixar saída parcial. Não é necessário desfazer essa saída.
- Entregue implementação, regressões e uma explicação das invariantes e dos limites.

## Casos de teste

| Entrada ou situação | Resultado esperado |
|---|---|
| `3 4 + 2 *` | `14` e LF. |
| `3 7 -` | `-4` e LF. |
| `-2147483648` | Aceitar o menor int32. |
| `2147483648` | Rejeitar literal fora do intervalo. |
| `2147483647 1 +` | Rejeitar overflow. |
| `1 +` | Rejeitar falta de operandos. |
| `1 2` ou entrada vazia | Rejeitar estado final inválido. |
| 64 valores e 63 somas | Aceitar sem ultrapassar a pilha. |
| 65 valores sem operadores | Rejeitar excesso de capacidade. |
| Token com byte zero ou letra | Rejeitar. |
| Erros de I/O | Falhar com diagnóstico. |

Os vetores públicos ficam em `tests/cases.json`. O [guia de testes](README.md) contém os comandos de compilação e execução. Passe todos os vetores e acrescente casos próprios.

## Extensões opcionais

- Faça uma ferramenta separada que mostra a pilha após cada token.
- Gere expressões válidas aleatórias e compare com um modelo independente.

As extensões preservam os operadores, os limites e a saída da interface base.

## Como participar

Compartilhe sua implementação no fórum de desafios do Discord, com um caso de overflow que ela rejeita. Dúvidas, descobertas e soluções parciais também são bem-vindas.
