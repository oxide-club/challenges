---
title: '#21 — Uma VM de bytecode'
slug: '021-bytecode'
summary: 'Execute bytecode de pilha com aritmética, memória e saltos, com validação prévia e orçamento de instruções.'
publishedAt: 2026-10-20
updatedAt: 2026-10-20
draft: false
difficulty: advanced
categories: [build, investigate]
participation: flagship
recommendedLanguage: C
acceptedLanguages: [C, Rust]
cardTopics: ['Máquina virtual', 'Bytecode', 'Fluxo de controle']
topics: ['Máquina virtual', 'Bytecode', 'Ciclo buscar-decodificar-executar', 'Validação', 'Fluxo de controle', 'Overflow de inteiros']
github:
  challenge: true
  solutions: [c]
  community: true
featured: false
environment: 'C11 ou Rust estável · Unix/Linux · inteiros de 32 bits'
---

**Dificuldade:** Difícil  
**Linguagem recomendada:** C (C11)  
**Linguagens aceitas:** C (C11) e Rust (estável)  
**Conceitos:** Máquina virtual, bytecode, ciclo buscar-decodificar-executar, validação e fluxo de controle.

## O desafio

Implemente uma máquina virtual de pilha que executa aritmética, memória e saltos.

Separe a validação do bytecode da execução. Investigue como o PC e a pilha evoluem em um programa com laço.

Pré-requisitos: arrays, inteiros de largura fixa, pilha e fluxo de controle. Os programas e helpers fornecidos permitem começar sem os outros interpretadores.

## Especificação

Execute `oxide-bytecode` sem argumentos. Leia de `stdin` até 65536 bytes de bytecode binário, sem cabeçalho. PC é o offset em bytes da próxima instrução. A pilha comporta 64 valores int32. A memória tem 16 posições int32, inicialmente zeradas.

| Opcode hex | Instrução | Operando após o opcode | Efeito |
|---|---|---|---|
| `00` | HALT | Nenhum | Encerra. Exige exatamente um valor na pilha. |
| `01` | PUSH | 4 bytes: int32 little endian em complemento de dois | Empilha o literal. |
| `02` | ADD | Nenhum | Retira b e a. Empilha a+b. |
| `03` | SUB | Nenhum | Retira b e a. Empilha a-b. |
| `04` | MUL | Nenhum | Retira b e a. Empilha a*b. |
| `05` | DUP | Nenhum | Copia o topo da pilha. |
| `06` | LOAD | 1 byte: endereço de 0 a 15 | Empilha o valor da memória. |
| `07` | STORE | 1 byte: endereço de 0 a 15 | Retira um valor e armazena no endereço. |
| `08` | JMP | 2 bytes: offset absoluto u16 little endian | Salta para o alvo. |
| `09` | JZ | 2 bytes: offset absoluto u16 little endian | Retira a condição. Salta se a condição é zero. |

Quando JZ recebe condição diferente de zero, avança para a instrução seguinte. As demais instruções também avançam conforme o seu tamanho, exceto JMP e HALT. Valores e resultados intermediários cabem em int32, de -2147483648 a 2147483647. Overflow é erro. Não execute aritmética com sinal que transborda.

Antes de executar, decodifique **toda** a entrada. Rejeite opcode desconhecido, operando incompleto, endereço de memória inválido e alvo de salto que não é início de instrução dentro do arquivo. Isso vale inclusive para código inalcançável. Saltar para um operando ou para o fim do arquivo é inválido.

Execute no máximo 1000 instruções. HALT conta nesse orçamento. Rejeite falta de operandos, excesso de pilha, queda fora do código e tentativa de executar a 1001ª instrução. HALT exige exatamente um valor na pilha e escreve esse resultado em decimal com LF em `stdout`.

Há um [leitor inicial](materials/read_le.py), um [programa com laço](materials/sum-loop.bin) e o seu [trace de PC, pilha e memória](materials/trace.md). Não é necessário construir assembler ou compilador.

## Exemplo

Os bytes abaixo empilham 3 e 4, somam e encerram:

```text
01 03 00 00 00 01 04 00 00 00 02 00
```

A execução passa pelos PCs 0, 5, 10 e 11. A pilha evolui para `[3]`, `[3,4]`, `[7]` e permanece `[7]` no HALT. A saída exata é:

```text
7
```

O programa `materials/sum-loop.bin` usa memória e saltos para somar 3+2+1. Ele produz `6` e LF.

## Requisitos

- Implemente em C11 ou Rust estável, apenas com a biblioteca padrão.
- Valide todo o programa antes da execução, inclusive instruções e saltos inalcançáveis.
- Mantenha pilha e memória dentro dos limites. Verifique overflow numérico e o orçamento.
- Retorne status zero somente no sucesso. Escreva em `stdout` apenas o resultado especificado.
- Em argumento, formato, operação ou limite inválido, ou falha de leitura ou escrita, escreva um diagnóstico em `stderr` e retorne status diferente de zero.
- Entregue implementação, regressões e um trace de PC e pilha para o laço. O trace não aparece no `stdout` da interface testada.
- Justifique os limites: validação prévia O(n), mapa de fronteiras O(n) e execução limitada a 1000 instruções. Uma falha pode deixar saída parcial.

## Casos de teste

| Programa ou situação | Resultado esperado |
|---|---|
| PUSH 3; PUSH 4; ADD; HALT | `7` e LF. |
| Programa de soma com laço fornecido | `6` e LF. |
| PUSH 8; DUP; ADD; HALT | `16` e LF. |
| Opcode desconhecido, mesmo inalcançável | Rejeitar. |
| Operando truncado ou endereço 16 | Rejeitar. |
| Salto para operando ou para o fim do arquivo | Rejeitar. |
| Operação sem operandos ou 65º valor | Rejeitar. |
| Overflow int32 | Rejeitar. |
| HALT com quantidade de valores diferente de um | Rejeitar. |
| Laço infinito ou 1001ª instrução | Rejeitar por orçamento. |
| Programa que encerra exatamente na 1000ª instrução | Aceitar. |
| Queda fora do código ou erros de I/O | Falhar com diagnóstico. |

Os vetores públicos ficam em `tests/cases.json`. O [guia de testes](README.md) contém os comandos de compilação e execução. Passe todos os vetores e acrescente casos próprios.

## Extensões opcionais

- Construa um disassembler separado para os opcodes definidos.
- Faça uma visualização interativa do trace sem alterar a execução base.

As extensões não alteram o formato, o orçamento ou a saída exigida pela suíte.

## Como participar

Compartilhe sua implementação e o trace do laço no fórum de desafios do Discord, com um programa inválido que a validação prévia rejeita. Dúvidas, descobertas e soluções parciais também são bem-vindas.
