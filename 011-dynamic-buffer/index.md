---
title: '#11 — Array dinâmico'
slug: '011-dynamic-buffer'
summary: 'Implemente um buffer com crescimento geométrico que preserva os dados e o estado em falhas de alocação.'
publishedAt: 2026-10-20
updatedAt: 2026-10-20
draft: false
difficulty: intermediate
categories: [build, investigate]
participation: flagship
recommendedLanguage: C
acceptedLanguages: [C, Rust]
cardTopics: ['Memória', 'Crescimento geométrico', 'Falha de alocação']
topics: ['Ponteiros', 'Capacidade', 'realloc', 'Overflow', 'Invariantes', 'Testes de API']
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
**Conceitos:** Ponteiros, capacidade, `realloc`, overflow, invariantes e testes de API.

## O desafio

Implemente um buffer de bytes que aumenta a reserva quando um append não cabe.

O desafio é preservar os dados durante vários crescimentos. O buffer também continua válido quando o cálculo do tamanho ou a alocação falha.

Pré-requisitos: ponteiros, structs, `malloc`, `realloc`, `free` e aritmética de `size_t`.

## Especificação

Use a API de [materials/api.h](materials/api.h). `buffer_init` recebe um callback `Resize` e cria um `Buffer` com `data = NULL`, tamanho zero e capacidade zero. `buffer_append` retorna `1` no sucesso ou `0` na falha. A origem fica fora do buffer e contém `n` bytes válidos. Aceite origem `NULL` com comprimento zero ou em uma solicitação rejeitada por overflow antes de qualquer leitura.

A primeira reserva tem oito bytes. Para crescer, dobre a capacidade até caber o novo conteúdo. Se a próxima duplicação excede `SIZE_MAX`, use exatamente o tamanho necessário. Detecte overflow de `size + n` antes de acessar a origem ou chamar o alocador.

O callback segue o contrato de `realloc`: `NULL` indica falha e preserva a região anterior. Uma falha preserva ponteiro, conteúdo, tamanho e capacidade. Publique a nova reserva somente depois do sucesso. O callback devolve memória compatível com `free`.

`buffer_destroy` libera a reserva com `free` e retorna ao estado vazio. Bytes zero são dados. Não use `strlen` para determinar o conteúdo.

O executável `oxide-dynamic-buffer` não recebe argumentos. O [adaptador](materials/adapter.c) lê comandos separados por espaços ou quebras de linha:

| Comando | Comportamento e saída |
|---|---|
| `a HEX` | Acrescenta até 2048 bytes. Imprime `ok` ou `fail`. Use `-` para uma sequência vazia. |
| `s` | Imprime `tamanho/capacidade:hex` e uma quebra de linha. |
| `d` | Libera e esvazia o buffer, sem imprimir. |
| `f` | Faz a próxima chamada real ao alocador falhar, sem imprimir. |
| `o` | Passa origem `NULL` e comprimento `SIZE_MAX`. Imprime `fail`. Use depois de um append não vazio para testar overflow. |

Append vazio e append que já cabe não consomem o gancho de falha. Todos os comandos podem repetir. O hexadecimal usa dígitos minúsculos. Os limites numéricos são precondições das entradas válidas.

Comando inválido, hexadecimal inválido, argumentos ou erro de leitura ou escrita exigem diagnóstico em `stderr` e status diferente de zero. Falha de capacidade, alocação ou overflow é um resultado normal `fail`. Uma execução com sucesso termina com status zero e sem mensagens adicionais.

## Exemplo

Dois appends atravessam a primeira fronteira de capacidade:

```text
Entrada:
a 00
s
a 0102030405060708
s
a ffffffffffffffff
s

Saída:
ok
1/8:00
ok
9/16:000102030405060708
ok
17/32:000102030405060708ffffffffffffffff
```

O tamanho usado passa de um para nove e depois dezessete bytes. A reserva passa de oito para dezesseis e depois trinta e dois.

## Requisitos

- Implemente em C11 ou Rust estável, apenas com a biblioteca padrão. Não use coleções dinâmicas prontas no lugar do algoritmo de crescimento.
- Preserve `size <= capacity`, os bytes anteriores e o estado completo nas falhas. Não suponha que a nova reserva tem o mesmo endereço.
- Mantenha a origem externa como precondição. Append do próprio buffer está fora do escopo.
- Preserve o adaptador, a API e o formato de saída.
- Entregue implementação, testes e uma explicação do crescimento geométrico e do seu custo acumulado. Distinga tamanho usado de capacidade reservada.

## Casos de teste

| Situação | Resultado esperado |
|---|---|
| Buffer recém-inicializado | `s` imprime `0/0:`. |
| Primeiro append de um byte zero | `ok`, seguido de `1/8:00` na consulta. |
| Appends do exemplo | Capacidades 8, 16 e 32, sem perder bytes. |
| Oito bytes reservados, `f`, append de um byte | `fail`. Os oito bytes e a capacidade 8 permanecem. |
| Repetir o append após a falha | Sucesso e capacidade 16. |
| `o` após um append não vazio | Falha por overflow sem acessar a origem nem chamar o alocador. |
| `f`, append vazio, depois append de um byte | O append vazio funciona. A primeira alocação real ainda falha. |
| Destruir e consultar | `0/0:`. |

Os vetores públicos ficam em `tests/cases.json`. O teste direto `tests/api_test.c` verifica cem appends, vários crescimentos, preservação do ponteiro na falha e ausência de chamada ao alocador no overflow. O [guia de testes](README.md) contém os comandos de compilação e execução. Acrescente sequências próprias.

## Extensões opcionais

- Adicione uma operação explícita de reserva mínima.
- Compare a quantidade de realocações para fatores de crescimento diferentes.
- Investigue uma operação de redução de capacidade, com contrato separado para falhas e invalidação de ponteiros.

As extensões não fazem parte dos critérios básicos.

## Como participar

Compartilhe sua implementação no fórum de desafios do Discord, com um append que preserva bytes anteriores e uma falha de alocação que mantém o estado válido. Dúvidas, descobertas e soluções parciais também são bem-vindas.
