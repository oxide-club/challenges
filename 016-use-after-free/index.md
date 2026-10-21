---
title: '#16 — Quem liberou este buffer?'
slug: '016-use-after-free'
summary: 'Reproduza um uso de memória após liberação com sanitizador, reconstrua a linha do tempo e corrija o contrato.'
publishedAt: 2026-10-20
updatedAt: 2026-10-20
draft: false
difficulty: beginner
categories: [debug, investigate]
participation: open
recommendedLanguage: C
acceptedLanguages: [C, Rust]
cardTopics: ['Tempo de vida', 'AddressSanitizer', 'Propriedade de memória']
topics: ['Tempo de vida', 'Use after free', 'AddressSanitizer', 'Propriedade de memória', 'Debugging', 'Teste de regressão']
github:
  challenge: true
  solutions: [c]
  community: true
featured: false
environment: 'C11 ou Rust estável · Unix/Linux · AddressSanitizer'
---

**Dificuldade:** Fácil  
**Linguagem recomendada:** C (C11)  
**Linguagens aceitas:** C (C11) e Rust (estável)  
**Conceitos:** Tempo de vida, use after free, AddressSanitizer, propriedade de memória e teste de regressão.

## O desafio

Um programa curto produz um buffer e outro trecho o consome. O acesso deixa de ser válido em algum ponto do caminho.

Investigue o código fornecido, reproduza o diagnóstico e reconstrua a sequência de eventos. Depois proponha uma correção.

Pré-requisitos: ponteiros, `malloc`, `free` e leitura de uma pilha de chamadas. A entrega inclui evidências de debugging, além do código.

## Especificação

Comece por [materials/buggy.c](materials/buggy.c) e pelo [relatório de sanitizador](materials/sanitizer-report.txt). Use as pilhas de alocação, liberação e acesso para identificar quais partes do programa controlam a região e quando ela deixa de poder ser lida. Endereços e linhas exatas do relatório variam conforme a compilação.

O contrato a preservar está em [materials/api.h](materials/api.h). `copy_bytes` recebe uma origem com `n` bytes válidos. Devolve uma cópia independente, compatível com `free`, ou `NULL` se a alocação falha. Com `n = 0`, a origem pode ser `NULL` e o resultado de sucesso é uma alocação liberável. A entrada pertence ao chamador. A saída passa a pertencer ao chamador e continua válida enquanto ele a usa. Determine como o código inicial viola esse contrato. Justifique a mudança necessária sem alterar o comportamento de cópia.

O [adaptador](materials/adapter.c) não recebe argumentos nem interpreta comandos. Ele lê de `stdin` até 65536 bytes binários brutos, inclusive zeros, espaços e quebras de linha. O adaptador chama `copy_bytes`, imprime dois dígitos hexadecimais minúsculos por byte e uma quebra de linha final. Depois libera o resultado. Entrada vazia produz somente a quebra de linha.

Entrada excessiva, falha de alocação, argumentos inválidos ou erro de leitura ou escrita exigem diagnóstico em `stderr` e status diferente de zero. Não há resultado normal `fail`. Uma execução com sucesso termina com status zero e sem mensagens adicionais.

Para reproduzir o starter com AddressSanitizer:

```sh
cc -std=c11 -g -O0 -fsanitize=address -fno-omit-frame-pointer materials/buggy.c -o /tmp/oxide-buggy
ASAN_OPTIONS=detect_leaks=0 /tmp/oxide-buggy
```

Espere status diferente de zero e o diagnóstico `heap-use-after-free`. O valor observado sem sanitizador não é uma saída válida. Um acesso fora do tempo de vida tem comportamento indefinido.

## Exemplo

No adaptador correto, os bytes `41 00 42 ff` produzem:

```text
410042ff
```

Há uma quebra de linha depois do último dígito. O exemplo inclui um byte zero no meio: o comprimento explícito controla a cópia. O texto ASCII `Oxide` produz `4f78696465` e uma quebra de linha.

## Requisitos

- Reproduza o defeito do starter com sanitizador e registre o diagnóstico. Não baseie a regressão em uma saída acidental de comportamento indefinido.
- Entregue uma linha do tempo de criação, liberação e acesso. Identifique o responsável por cada `free`. Explique quais ponteiros precisam continuar válidos em cada etapa.
- Forneça o patch, a implementação da API e uma regressão que distinga a versão inicial da corrigida. Preserve a independência da cópia e o tratamento de dados binários.
- Implemente em C11 ou Rust estável, apenas com a biblioteca padrão. Preserve o conceito de tempo de vida estudado. A investigação do starter em C continua parte da atividade.
- Mantenha o adaptador e o formato de saída.

## Casos de teste

| Situação | Resultado esperado |
|---|---|
| Starter sob AddressSanitizer | Status diferente de zero e `heap-use-after-free`. |
| Entrada vazia no adaptador correto | Somente `\n`. |
| Bytes `41 00 42 ff` | `410042ff` e quebra de linha. |
| Texto `Oxide` | `4f78696465` e quebra de linha. |
| Alterar a origem depois da cópia | O resultado independente mantém os bytes anteriores. |
| Cópia de comprimento zero | O chamador pode liberar o resultado de sucesso. |

Os vetores públicos ficam em `tests/cases.json`. O teste direto `tests/api_test.c` verifica a independência da cópia. O script `tests/sanitizer_regression.py` exige o diagnóstico no starter. Na correção, todos os vetores precisam passar sob ASan e UBSan. O [guia de testes](README.md) contém os comandos. Acrescente um caso que documente a responsabilidade pela liberação sem acessar ponteiros inválidos.

## Extensões opcionais

- Investigue separadamente um caso de double free e compare as pilhas do diagnóstico.
- Desenhe o fluxo de propriedade entre funções em um programa maior.
- Acrescente falha de alocação injetável em uma variante da API. Documente o contrato antes de implementar.

As extensões não fazem parte dos critérios básicos.

## Como participar

Compartilhe a linha do tempo, o patch e a regressão no fórum de desafios do Discord. Dúvidas, descobertas e soluções parciais também são bem-vindas.
