---
title: '#10 — Array fixo'
slug: '010-fixed-buffer'
summary: 'Acrescente bytes a uma região emprestada e rejeite excessos sem alterar o estado anterior.'
publishedAt: 2026-10-20
updatedAt: 2026-10-20
draft: false
difficulty: beginner
categories: [build, investigate]
participation: open
recommendedLanguage: C
acceptedLanguages: [C, Rust]
cardTopics: ['Memória', 'Tamanho e capacidade', 'Invariantes']
topics: ['Ponteiros', 'Capacidade', 'Invariantes', 'Structs', 'Testes de API']
github:
  challenge: true
  solutions: [c]
  community: true
featured: false
environment: 'C11 ou Rust estável · Unix/Linux'
---

**Dificuldade:** Fácil  
**Linguagem recomendada:** C (C11)  
**Linguagens aceitas:** C (C11) e Rust (estável)  
**Conceitos:** Ponteiros, capacidade, invariantes, structs e testes de API.

## O desafio

Um buffer tem duas medidas diferentes: o espaço disponível e a quantidade de bytes já usada.

Implemente um buffer que recebe uma região de memória do chamador e acrescenta dados enquanto há capacidade. Uma tentativa que não cabe deixa o estado anterior intacto.

Pré-requisitos: arrays, ponteiros, structs e aritmética de `size_t`.

## Especificação

Implemente a API de [materials/api.h](materials/api.h). Preserve o adaptador [materials/adapter.c](materials/adapter.c).

- `buffer_init` recebe a região e sua capacidade. O tamanho inicial é zero.
- `buffer_append` acrescenta `n` bytes e retorna `1` no sucesso. Se `n > capacity - size`, retorna `0` sem alterar tamanho, capacidade ou bytes anteriores.
- A origem fica fora do buffer e contém `n` bytes válidos. Rejeite uma solicitação impossível antes de acessar a origem. Com `n = 0`, aceite origem `NULL`.
- `buffer_clear` zera somente o tamanho lógico.

A região continua do chamador. A API nunca aloca nem libera essa região.

O executável `oxide-fixed-buffer` não recebe argumentos. O adaptador lê de `stdin` primeiro a capacidade, entre `0` e `65536`, e depois os comandos abaixo, separados por espaços ou quebras de linha.

| Comando | Comportamento e saída |
|---|---|
| `a HEX` | Acrescenta até 2048 bytes. Imprime `ok` ou `fail`. Use `-` para uma sequência vazia. |
| `s` | Imprime `tamanho/capacidade:hex` e uma quebra de linha. |
| `c` | Limpa o conteúdo lógico, sem imprimir. |
| `o` | Solicita `SIZE_MAX` bytes de origem `NULL`. Imprime `fail` sem ler a origem. |

O hexadecimal usa dois dígitos minúsculos por byte. O byte `00` é dado válido, sem terminador implícito. Os limites numéricos são precondições das entradas válidas.

Comando inválido, hexadecimal inválido, argumentos ou erro de leitura ou escrita exigem diagnóstico em `stderr` e status diferente de zero. Falta de capacidade é um resultado normal `fail`. Uma execução com sucesso termina com status zero e sem mensagens adicionais.

## Exemplo

Com capacidade quatro, dois appends preenchem exatamente a região:

```text
Entrada:
4
a 0001
a ff00
s

Saída:
ok
ok
4/4:0001ff00
```

Os dois bytes zero continuam presentes. Um append de mais um byte nesse estado falha e preserva a sequência.

## Requisitos

- Implemente em C11 ou Rust estável, apenas com a biblioteca padrão. Não substitua a estrutura por uma coleção pronta. Não use alocação dinâmica.
- Mantenha `0 <= size <= capacity`. Aceite capacidade zero e append vazio.
- Preserve a API, os comandos e o formato de saída fornecidos.
- Entregue implementação, testes e uma explicação da diferença entre tamanho e capacidade. Explique por que a falha preserva o estado.
- Em Rust, reproduza os comandos sobre uma região fixa com offsets. Mantenha as mesmas regras observáveis.

## Casos de teste

| Situação | Resultado esperado |
|---|---|
| Capacidade 8, sem appends | `s` imprime `0/8:`. |
| Capacidade 4, bytes `00 01 ff 00` | Sucesso e `4/4:0001ff00`. |
| Capacidade 2, append `ab cd` seguido de `ff` | O segundo append falha. O estado é `2/2:abcd`. |
| Limpar o caso anterior | Estado `0/2:`, com capacidade preservada. |
| Capacidade zero | Append vazio funciona. Um byte e `o` falham. |
| `a zz` ou comando desconhecido | Status diferente de zero e diagnóstico em `stderr`. |

Os vetores públicos ficam em `tests/cases.json`. O teste direto `tests/api_test.c` liga sua implementação à API e verifica bytes de guarda fora da região. O [guia de testes](README.md) contém os comandos de compilação e execução. Acrescente sequências próprias para verificar que uma operação rejeitada não altera nenhum byte válido.

## Extensões opcionais

- Adicione uma operação de truncamento do tamanho lógico.
- Meça a ocupação máxima durante uma sequência de operações.
- Crie uma visualização dos bytes usados e livres. Mantenha a API e o protocolo básicos.

As extensões não fazem parte dos critérios básicos.

## Como participar

Compartilhe sua implementação no fórum de desafios do Discord, com um teste que mostre uma falha sem alteração do estado. Dúvidas, descobertas e soluções parciais também são bem-vindas.
