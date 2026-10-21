---
title: '#18 — Um alocador com liberação individual'
slug: '018-free-list'
summary: 'Gerencie uma região fixa com first-fit, divisão de blocos e união de vizinhos livres após liberações.'
publishedAt: 2026-10-20
updatedAt: 2026-10-20
draft: false
difficulty: advanced
categories: [build, investigate]
participation: open
recommendedLanguage: C
acceptedLanguages: [C, Rust]
cardTopics: ['Alocação', 'First-fit', 'Fragmentação']
topics: ['Alocadores', 'First-fit', 'Coalescência', 'Fragmentação', 'Invariantes', 'Testes de API']
github:
  challenge: true
  solutions: [c]
  community: true
featured: false
environment: 'C11 ou Rust estável · Unix/Linux'
---

**Dificuldade:** Difícil  
**Linguagem recomendada:** C (C11)  
**Linguagens aceitas:** C (C11) e Rust (estável)  
**Conceitos:** Alocadores, first-fit, coalescência, fragmentação, invariantes e testes de API.

## O desafio

Construa um alocador que reutiliza partes de uma região fixa depois de liberações individuais.

Use a política first-fit: percorra os blocos em ordem e escolha o primeiro bloco livre que comporta a solicitação. A divisão e a união de blocos mantêm um mapa consistente, mesmo com a região fragmentada.

Pré-requisitos: ponteiros, structs, alinhamento e aritmética de `size_t`.

## Especificação

Use a API de [materials/api.h](materials/api.h). `pool_init` recebe uma região emprestada alinhada a oito bytes. Os metadados ficam fora da região, em `Pool.blocks`, com até 1024 descritores ordenados por offset. Os metadados não descontam bytes da capacidade útil.

A capacidade útil é a capacidade recebida arredondada para baixo a um múltiplo de oito. Se a capacidade útil é zero, o mapa fica vazio. Caso contrário, o mapa começa com um único bloco livre.

`pool_alloc` recebe um tamanho positivo. Arredonde o tamanho para cima a um múltiplo de oito e procure o primeiro bloco livre suficiente. Verifique overflow antes da soma de arredondamento. Se sobra no mínimo oito bytes, divida o bloco. Se a divisão exige um descritor indisponível, falhe e preserve o mapa. Um encaixe exato não exige um novo descritor. No sucesso, devolva `base + offset`. Tamanho inválido, overflow ou falta de recurso devolve `NULL` sem modificar o estado. Não use `malloc`.

`pool_free` aceita somente um ponteiro vivo entregue pelo mesmo pool. Marque o bloco como livre e una todos os blocos livres adjacentes. Liberações inválidas, `realloc` e concorrência estão fora do contrato da API.

O executável `oxide-free-list` não recebe argumentos. O [adaptador](materials/adapter.c) lê primeiro a capacidade, entre `0` e `65536`, e depois tokens separados por espaços ou quebras de linha:

| Comando | Comportamento e saída |
|---|---|
| `a N` | Imprime `ID:OFFSET` ou `fail`. Os IDs começam em zero e só avançam no sucesso. O limite é 8192 alocações com sucesso. |
| `f ID` | Libera um ID vivo, sem imprimir. |
| `m` | Imprime os blocos em ordem como `offset:tamanho:U` ou `offset:tamanho:F`, separados por um espaço. Um mapa vazio imprime `empty`. |
| `o` | Solicita `SIZE_MAX` bytes. Imprime `fail`. |

`U` significa usado e `F` significa livre. Cada resultado ocupa uma linha. Os limites numéricos são precondições das entradas válidas. O adaptador rejeita IDs inválidos antes de chamar a API.

Comando inválido, argumentos inválidos ou erro de leitura ou escrita exigem diagnóstico em `stderr` e status diferente de zero. Falta de espaço, falta de descritores ou overflow é um resultado normal `fail`. Uma execução com sucesso termina com status zero e sem mensagens adicionais.

## Exemplo

A sequência preenche a região, cria um espaço livre entre blocos usados e mostra uma solicitação maior que esse espaço. Depois da união de vizinhos, dezesseis bytes voltam a caber:

```text
Entrada:
24
a 8
a 8
a 8
a 1
m
f 1
a 16
m
f 0
a 16
m
o
a 0
m

Saída:
0:0
1:8
2:16
fail
0:8:U 8:8:U 16:8:U
fail
0:8:U 8:8:F 16:8:U
3:0
0:16:U 16:8:U
fail
fail
0:16:U 16:8:U
```

O ID três só é atribuído quando uma nova alocação funciona. Os pedidos rejeitados não alteram o mapa.

## Requisitos

- Implemente em C11 ou Rust estável, apenas com a biblioteca padrão. Não use alocação dinâmica nem coleções prontas no lugar da lista de blocos.
- Mantenha os blocos contíguos, positivos, alinhados e sem sobreposição. A soma dos tamanhos é igual à capacidade útil.
- Depois de uma liberação, não deixe blocos livres adjacentes. Preserve os blocos vivos e seu conteúdo durante a divisão e a união.
- Implemente first-fit, divisão e coalescência. Por exemplo, uma região livre de 64 bytes vira `[0,16 usado][16,48 livre]` ao reservar nove bytes.
- Preserve a API e o protocolo. Em Rust, use offsets em uma região fixa.
- Entregue implementação, testes e uma explicação das invariantes. Demonstre uma solicitação que falha por fragmentação e volta a caber após a coalescência.

## Casos de teste

| Situação | Resultado esperado |
|---|---|
| Capacidade 64, reservar 9 | Offset zero. Blocos de 16 usados e 48 livres. |
| Liberar espaço antes de um bloco livre maior | A próxima reserva escolhe o primeiro bloco suficiente. |
| Três blocos de 8 em uma região de 24, liberar somente o central | Um pedido de 16 falha sem mudar o mapa. |
| Liberar também o primeiro bloco | A união cria 16 livres. Um pedido de 16 funciona no offset zero. |
| Liberar todos os blocos | Um bloco livre cobre toda a capacidade útil. |
| Capacidade 7 | Mapa `empty`. Toda solicitação positiva falha. |
| Tamanho zero ou `SIZE_MAX` | Falha sem alterar o estado. |
| Região de 8200, após 1023 reservas de 8 | Os 1024 descritores estão ocupados. Dividir o bloco livre final de 16 falha. Encaixar 16 funciona. |

Os vetores públicos ficam em `tests/cases.json` e incluem uma sequência comparada com um modelo independente. O teste direto `tests/api_test.c` usa sentinelas nos blocos vivos para detectar sobreposição e verifica a preservação do mapa na falta de descritores. O [guia de testes](README.md) contém os comandos de compilação e execução. Confira offsets e mapas completos, não só o status.

## Extensões opcionais

- Meça a fragmentação externa e compare sequências de pedidos.
- Implemente best-fit em uma variante separada e compare os mapas produzidos.
- Projete um contrato para detectar liberações inválidas, com testes próprios. Não torne isso requisito da API básica.

As extensões não fazem parte dos critérios básicos.

## Como participar

Compartilhe sua implementação no fórum de desafios do Discord, com um mapa antes e depois de uma coalescência. Dúvidas, descobertas e soluções parciais também são bem-vindas.
