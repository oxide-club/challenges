---
title: '#17 — Arena de memória alinhada'
slug: '017-arena'
summary: 'Entregue trechos alinhados de uma região fixa, sem sobreposição, e reinicialize tudo de uma vez.'
publishedAt: 2026-10-20
updatedAt: 2026-10-20
draft: false
difficulty: intermediate
categories: [build, investigate]
participation: flagship
recommendedLanguage: C
acceptedLanguages: [C, Rust]
cardTopics: ['Alocação', 'Alinhamento', 'Invariantes']
topics: ['Alocadores', 'Arena', 'Alinhamento', 'Overflow', 'Tempo de vida', 'Testes de API']
github:
  challenge: true
  solutions: [c]
  community: true
featured: false
environment: 'C11 ou Rust estável · Unix/Linux'
---

**Dificuldade:** Intermediário  
**Linguagem recomendada:** C (C11)  
**Linguagens aceitas:** C (C11) e Rust (estável)  
**Conceitos:** Alocadores, arena, alinhamento, overflow, tempo de vida e testes de API.

## O desafio

Implemente um alocador de região fixa que entrega trechos alinhados e reinicializa todos de uma vez.

Cada solicitação pode precisar de preenchimento antes dos bytes úteis. Esse preenchimento também consome capacidade.

Pré-requisitos: ponteiros, structs, alinhamento e aritmética de `size_t`.

## Especificação

Use [materials/api.h](materials/api.h). `arena_init` recebe uma base já alinhada a 16 bytes e a capacidade de uma região válida. O campo `used` começa em zero. A memória continua do chamador.

`arena_alloc(a, n, alignment)` aceita `n` positivo e alinhamento `1`, `2`, `4`, `8` ou `16`. Encontre o menor offset maior ou igual a `used` que é múltiplo do alinhamento. No sucesso, devolva `base + offset` e avance `used` até o fim dos `n` bytes. Nenhuma alocação se sobrepõe a outra ainda válida.

Solicitação inválida ou sem espaço devolve `NULL` e preserva `used`. Verifique o preenchimento e o tamanho por subtração antes de somar. Assim, `SIZE_MAX` não provoca wraparound. `arena_reset` zera `used`. **Todos os ponteiros entregues antes do reset ficam inválidos**, mesmo quando o endereço é reutilizado. Não existe liberação individual.

O executável `oxide-arena` não recebe argumentos. O [adaptador](materials/adapter.c) lê primeiro a capacidade, entre `0` e `65536`, e depois comandos separados por espaços ou quebras de linha:

| Comando | Comportamento e saída |
|---|---|
| `a N ALINHAMENTO` | Imprime o offset do trecho ou `fail`. |
| `s` | Imprime `used/capacity`. |
| `r` | Reinicializa, sem imprimir. |
| `o` | Solicita `SIZE_MAX` bytes alinhados a 16. Imprime `fail`. |

Cada resultado ocupa uma linha. Os limites numéricos são precondições das entradas válidas. Tamanho zero ou alinhamento não permitido são solicitações rejeitadas com `fail`.

Comando inválido, argumentos inválidos ou erro de leitura ou escrita exigem diagnóstico em `stderr` e status diferente de zero. Uma execução com sucesso termina com status zero e sem mensagens adicionais.

## Exemplo

O exemplo mostra preenchimento, falha sem consumo de espaço e reutilização após reset:

```text
Entrada:
32
a 1 1
a 3 8
s
a 1 16
a 17 1
s
r
a 32 16
s

Saída:
0
8
11/32
16
fail
17/32
0
32/32
```

Depois do primeiro byte, o segundo trecho começa no offset oito. Os sete bytes intermediários são preenchimento. A solicitação que falha deixa `used` em dezessete.

## Requisitos

- Implemente em C11 ou Rust estável, apenas com a biblioteca padrão e a região fornecida. Não use alocação dinâmica nem coleções prontas no lugar do algoritmo.
- Preserve `used <= capacity`, o alinhamento dos endereços entregues e a ausência de sobreposição.
- Trate overflow e falta de espaço sem avançar `used`. Tamanho zero é inválido nesta API.
- Preserve a API e o protocolo. Em Rust, trabalhe com offsets em uma região fixa e mantenha as mesmas invariantes.
- Entregue implementação, testes e um diagrama de uma sequência de alocações. Distinga bytes úteis de preenchimento. Explique a invalidação de ponteiros após o reset.

## Casos de teste

| Situação | Resultado esperado |
|---|---|
| Capacidade 32, alocar 1 alinhado a 1 e 3 alinhados a 8 | Offsets 0 e 8. `used = 11`. |
| Alinhamentos 1, 2, 4, 8 e 16 | Endereços múltiplos do alinhamento pedido. |
| Alinhamento 0, 3 ou 32. Tamanho zero | `fail`, sem consumir capacidade. |
| `o` | Falha sem overflow e sem mudar `used`. |
| Alocar exatamente toda a capacidade depois de reset | Offset zero e `used = capacity`. |
| Capacidade zero | Toda solicitação positiva falha. O reset mantém `0/0`. |

Os vetores públicos ficam em `tests/cases.json`. O teste direto `tests/api_test.c` verifica os endereços reais, os limites e a ausência de sobreposição. O [guia de testes](README.md) contém os comandos de compilação e execução. Não desreferencie ponteiros de alocações anteriores depois do reset. Teste a nova sequência de offsets.

## Extensões opcionais

- Adicione marcas e retorno a uma marca, com contrato explícito de invalidação.
- Registre a quantidade de bytes perdida em preenchimento por alinhamento.
- Compare distribuições de pedidos em uma visualização. Mantenha as regras de capacidade e reset.

As extensões não fazem parte dos critérios básicos.

## Como participar

Compartilhe sua implementação e o diagrama no fórum de desafios do Discord, com uma falha que não consome capacidade. Dúvidas, descobertas e soluções parciais também são bem-vindas.
