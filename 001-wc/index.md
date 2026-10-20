---
title: '#1 — Construa seu wc'
slug: '001-wc'
summary: 'Conte linhas, palavras e bytes lendo a entrada aos poucos, sem carregar todos os dados na memória.'
publishedAt: 2026-10-18
updatedAt: 2026-10-19
draft: false
difficulty: beginner
categories: [build, investigate]
participation: flagship
recommendedLanguage: C
acceptedLanguages: [C]
cardTopics: ['Entrada e saída', 'Fim de arquivo', 'Estado']
topics: ['Entrada e saída', 'Streams', 'EOF', 'Gerenciamento de estado']
github:
  challenge: true
  solutions: [c]
  community: true
featured: true
environment: 'C11 · Exemplos para terminais Unix/Linux'
---

**Dificuldade:** Iniciante  
**Linguagem:** C (C11)  
**Conceitos:** Entrada e saída, streams, EOF e gerenciamento de estado.

## O desafio

O `wc` (*word count*) é uma ferramenta Unix utilizada para contar linhas, palavras e bytes de uma entrada.

Seu objetivo é construir uma versão simplificada dessa ferramenta em C, chamada `oxide-wc`.

## Especificação

Seu programa deve ler dados da entrada padrão (`stdin`) até o fim da entrada e contabilizar:

- **Linhas:** número de ocorrências de `'\n'`.
- **Palavras:** sequências contínuas de um ou mais bytes que não sejam separadores. Considere separadores: espaço, `'\t'`, `'\n'`, `'\r'`, `'\v'` e `'\f'`.
- **Bytes:** quantidade total de bytes lidos, incluindo separadores.

A saída deve conter exatamente três números inteiros não negativos, separados por um espaço, na ordem: linhas, palavras e bytes. Finalize com uma quebra de linha.

### Exemplo

```bash
$ printf 'Hello world\nC is fun\n' | ./oxide-wc
2 5 21
```

## Requisitos

- Utilize C11 e sua biblioteca padrão.
- Leia os dados de `stdin`, sem argumentos obrigatórios.
- Processe a entrada sem armazená-la integralmente na memória.
- Não invoque o `wc` original.
- Não imprima mensagens adicionais em `stdout`.

Considere entradas ASCII, operações de leitura e escrita bem-sucedidas e contagens que caibam no tipo inteiro escolhido.

## Casos de teste

| Entrada | Saída esperada |
|---|---|
| `printf ''` | `0 0 0` |
| `printf 'hello'` | `0 1 5` |
| `printf 'hello\n'` | `1 1 6` |
| `printf 'a b\n'` | `1 2 4` |
| `printf 'a\nb'` | `1 2 3` |
| `printf 'one   two\n'` | `1 2 10` |
| `printf ' \t\n\r\v\f'` | `1 0 6` |
| `printf '\r\n'` | `1 0 2` |

Você pode comparar os resultados com `LC_ALL=C wc -l -w -c`, desconsiderando os espaços de alinhamento da ferramenta original.

## Extensões opcionais

1. **Arquivos:** aceite um caminho de arquivo como argumento.
2. **Flags:** implemente as opções `-l`, `-w` e `-c`.
3. **Desempenho:** compare estratégias de leitura utilizando `fgetc()` e `fread()`.
4. **Robustez:** investigue UTF-8, entradas binárias, estouro de contadores e falhas de I/O.

## Como participar

Compartilhe sua implementação no fórum de desafios do Discord, acompanhada de um exemplo de execução e de alguma descoberta ou dificuldade encontrada.

**Não é necessário concluir o desafio para participar.** Dúvidas, experimentos, casos de teste e implementações parciais também são contribuições válidas.

O objetivo não é apenas fazer o programa funcionar, mas compreender e explicar as decisões tomadas durante sua construção.

## Precisa de uma dica?

Está com dificuldades ou não sabe por onde começar?

Preparamos **dicas progressivas** para ajudar você a avançar sem revelar a solução.

[Acesse as dicas no Discord](https://discord.com/channels/1561460326136811570/1561825043577573547)

Você também pode compartilhar dúvidas, experimentos e descobertas no tópico do desafio.
