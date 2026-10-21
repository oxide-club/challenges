---
title: '#15 — O que este executável faz?'
slug: '015-mystery-program'
summary: 'Reconstrua uma transformação determinística de bytes a partir de um executável, com traces, assembly e debugger.'
publishedAt: 2026-10-20
updatedAt: 2026-10-20
draft: false
difficulty: advanced
categories: [investigate, build]
participation: open
recommendedLanguage: C
acceptedLanguages: [C, Rust]
cardTopics: ['Engenharia reversa', 'Assembly x86-64', 'Debugger']
topics: ['Engenharia reversa', 'Assembly x86-64', 'GDB', 'ELF', 'Método experimental', 'Testes diferenciais']
github:
  challenge: true
  solutions: [c]
  community: true
featured: false
environment: 'C11 ou Rust estável · Linux x86-64 para o alvo · bytes de 8 bits'
---

**Dificuldade:** Difícil  
**Linguagem recomendada:** C (C11)  
**Linguagens aceitas:** C (C11) e Rust (estável)  
**Conceitos:** Engenharia reversa, assembly x86-64, GDB, ELF e testes diferenciais.

## O desafio

Reconstrua o comportamento de um executável pequeno do clube.

Investigue como cada byte e sua posição afetam a saída. Produza uma implementação equivalente, com evidências.

Pré-requisitos: bytes, arrays e inteiros. Disassembly e debugger ajudam. Os traces permitem começar em outras plataformas. O material não depende de outro desafio.

## Especificação

Execute `oxide-mystery-program` sem argumentos. A entrada em `stdin` contém de zero a **64 bytes arbitrários**. A saída em `stdout` contém exatamente a mesma quantidade de bytes, transformados, sem cabeçalho nem LF adicional. A transformação é determinística. Não há aleatoriedade nem acesso à rede. Entrada vazia produz saída vazia. Rejeite entradas com mais de 64 bytes.

O alvo é [mystery-linux-x86_64](materials/mystery-linux-x86_64), um executável Linux x86-64. Consulte o alvo como oráculo:

```sh
./materials/mystery-linux-x86_64 < entrada.bin > saida.bin
```

A [listagem de assembly](materials/mystery.asm) e os [traces e comandos de debugger](materials/traces.md) permitem estudar o comportamento sem executar o ELF. O binário distribuído é stripped e PIE. Siga o procedimento por endereços dos materiais, inclusive o cálculo da base para depurar com ASLR.

Formule hipóteses sobre ordem, alteração dos bytes e dependência da posição. Compare zeros, impulsos em posições distintas, uma rampa e entradas de 64 bytes. Depois de escrever o pseudocódigo, valide com entradas novas. A fonte e o procedimento de reconstrução do alvo ficam na referência separada, para preservar a investigação.

## Exemplo

Uma observação inicial disponível nos traces é:

```text
stdin hex:  41 42 43
stdout hex: 1b 19 1b
```

A saída tem três bytes, sem quebra de linha. Use essa observação para confrontar hipóteses. Ela não basta para determinar a transformação inteira.

## Requisitos

- Implemente a versão equivalente em C11 ou Rust estável, apenas com a biblioteca padrão.
- Entregue pseudocódigo explicado, implementação, regressões e o registro das hipóteses, com os experimentos que as diferenciam.
- Confira o resultado com casos novos, além das observações iniciais.
- Aceite qualquer valor de byte, inclusive `00` e `ff`, dentro do limite de 64 bytes.
- Retorne status zero somente no sucesso. Escreva em `stdout` apenas os bytes transformados.
- Em argumento, limite ou operação inválida, ou falha de leitura ou escrita, escreva um diagnóstico em `stderr` e retorne status diferente de zero.
- Uma falha pode deixar saída parcial. Justifique os limites e os acessos aos buffers.

## Casos de teste

| Caso | Resultado esperado |
|---|---|
| Entrada vazia | Saída vazia. |
| Byte `00` | Byte `5a`, conforme o trace inicial. |
| Bytes `41 42 43` | Bytes `1b 19 1b`. |
| Impulsos em posições diferentes | Mesmo resultado do alvo. |
| Dados novos com bytes altos | Mesmo resultado do alvo. |
| 64 bytes | Aceitar e produzir exatamente 64 bytes. |
| 65 bytes | Rejeitar. |
| Argumentos ou falhas de I/O | Falhar com diagnóstico. |

Os vetores públicos ficam em `tests/cases.json`. Use os casos novos para validar a hipótese final. O [guia de testes](README.md) contém os comandos de compilação e execução.

## Extensões opcionais

- Automatize consultas diferenciais entre sua implementação e o alvo.
- Documente quais instruções do assembly sustentam cada parte do pseudocódigo.

As extensões não alteram a transformação, os limites ou a interface base.

## Como participar

Compartilhe o pseudocódigo e o registro das hipóteses no fórum de desafios do Discord. Dúvidas, descobertas e soluções parciais também são bem-vindas.
