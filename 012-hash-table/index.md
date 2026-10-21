---
title: '#12 — Uma tabela hash que cresce'
slug: '012-hash-table'
summary: 'Mapeie inteiros com endereçamento aberto, resolva colisões e preserve todos os pares ao redimensionar.'
publishedAt: 2026-10-20
updatedAt: 2026-10-20
draft: false
difficulty: advanced
categories: [build, investigate]
participation: open
recommendedLanguage: C
acceptedLanguages: [C, Rust]
cardTopics: ['Memória', 'Endereçamento aberto', 'Redimensionamento']
topics: ['Tabela hash', 'Sondagem linear', 'Colisões', 'Redimensionamento', 'Invariantes', 'Testes de API']
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
**Conceitos:** Tabela hash, sondagem linear, colisões, redimensionamento e testes de API.

## O desafio

Construa uma tabela que mapeia chaves inteiras para valores inteiros.

Quando duas chaves disputam a mesma posição, resolva a colisão. Quando a tabela cresce, reconstrua as posições sem perder nenhum par.

Pré-requisitos: arrays, ponteiros, structs, alocação dinâmica e aritmética de `size_t`. Não há remoção nesta edição.

## Especificação

Implemente a API de [materials/api.h](materials/api.h) com endereçamento aberto e sondagem linear. Chaves e valores são `int32_t`. A capacidade inicial é zero. A primeira inserção reserva oito slots. Depois disso, a capacidade é sempre uma potência de dois. O hash público é:

```c
(uint32_t)key & (capacity - 1)
```

Antes de inserir uma **chave nova** com `count >= capacity / 2`, dobre a capacidade e reintroduza todos os pares com o hash da nova capacidade. Atualizar uma chave existente não aumenta a contagem e não aloca. Inicialize os slots antes de consultar `occupied`.

- `table_init` cria a tabela vazia e recebe o callback `Allocate`. O callback devolve memória compatível com `free`.
- `table_put` insere ou atualiza. Retorna `1` no sucesso e `0` na falha. Falha de alocação ou overflow preserva todos os pares, a contagem e a capacidade.
- `table_get` retorna `1` e escreve o valor encontrado. Se a chave não existe, retorna `0` sem alterar a variável de saída.
- `table_destroy` libera a reserva e retorna ao estado vazio.

O executável `oxide-hash-table` não recebe argumentos. O [adaptador](materials/adapter.c) aceita tokens separados por espaços ou quebras de linha:

| Comando | Comportamento e saída |
|---|---|
| `p CHAVE VALOR` | Insere ou atualiza. Imprime `ok` ou `fail`. |
| `g CHAVE` | Imprime o valor ou `missing`. |
| `s` | Imprime `count/capacity`. |
| `f` | Faz a próxima alocação real falhar, sem imprimir. |

Cada resultado ocupa uma linha. Chaves e valores no intervalo de `int32_t` são precondições das entradas válidas.

Comando incompleto ou desconhecido, argumentos inválidos ou erro de leitura ou escrita exigem diagnóstico em `stderr` e status diferente de zero. Falha de alocação ou overflow é um resultado normal `fail`. Uma execução com sucesso termina com status zero e sem mensagens adicionais.

## Exemplo

As chaves abaixo colidem na capacidade oito. Atualizar a chave oito altera apenas o seu valor:

```text
Entrada:
p 0 10
p 8 20
p 16 30
p 24 40
p 8 99
s
g 0
g 8
g 16
g 24
g 32
p 32 50
s
g 0
g 8
g 16
g 24
g 32

Saída:
ok
ok
ok
ok
ok
4/8
10
99
30
40
missing
ok
5/16
10
99
30
40
50
```

A quinta chave nova força o crescimento. Todos os pares continuam acessíveis.

## Requisitos

- Implemente em C11 ou Rust estável, apenas com a biblioteca padrão. Não use mapas ou coleções prontas no lugar da tabela.
- Implemente sondagem linear e reconstrução durante o crescimento. Não copie os slots para as mesmas posições da nova reserva.
- Preserve o estado nas falhas. Verifique os cálculos da capacidade e dos bytes antes da alocação.
- Preserve a API e o protocolo fornecidos. Remoção e concorrência estão fora do escopo.
- Entregue implementação, testes de colisão, crescimento e atualização e uma explicação das invariantes.

## Casos de teste

| Situação | Resultado esperado |
|---|---|
| Chaves 0, 8, 16 e 24 | Todos os valores são recuperados, apesar das colisões. |
| Atualizar a chave 8 | Novo valor, mesma contagem e mesma capacidade. |
| Inserir a quinta chave nova | A capacidade passa de 8 para 16. Todos os pares sobrevivem. |
| `f` antes da primeira inserção | `fail` e estado `0/0`. |
| `f` antes de um crescimento | Estado anterior preservado. Repetir a inserção pode funcionar. |
| Consulta ausente | `missing`. Na API, a variável de saída permanece intacta. |
| Chave `-2147483648`, valor `2147483647` | Inserção e consulta corretas. |

Os vetores públicos ficam em `tests/cases.json` e incluem uma sequência gerada por modelo, com centenas de operações e vários crescimentos. O teste direto `tests/api_test.c` compara inserções e atualizações com um modelo simples. O [guia de testes](README.md) contém os comandos de compilação e execução. Acrescente sequências próprias.

## Extensões opcionais

- Meça o número de sondagens por operação para conjuntos de chaves diferentes.
- Compare funções de hash em uma variante separada. Mantenha a sondagem e a política de crescimento.
- Projete remoção com estados adicionais de slot e testes próprios. Não a acrescente ao contrato obrigatório.

As extensões não fazem parte dos critérios básicos.

## Como participar

Compartilhe sua implementação no fórum de desafios do Discord, com um teste de colisão forçada e um crescimento que preserva todos os pares. Dúvidas, descobertas e soluções parciais também são bem-vindas.
