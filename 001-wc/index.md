---
title: 'Construa seu wc'
slug: '001-wc'
area: systems-fundamentals
summary: 'Conte linhas, palavras e bytes lendo a entrada aos poucos, sem carregar todos os dados na memória.'
publishedAt: 2026-10-18
updatedAt: 2026-10-20
draft: false
difficulty: beginner
categories: [build, investigate]
participation: flagship
recommendedLanguage: C
acceptedLanguages: [C]
cardTopics: ['Bytes e fluxo', 'Contagem de palavras', 'Estado']
topics: ['Entrada e saída', 'Streams', 'EOF', 'Separadores ASCII', 'Gerenciamento de estado']
github:
  challenge: true
  solutions: [c]
  community: true
featured: true
environment: 'C11 · Unix/Linux · entrada ASCII'
---

**Dificuldade:** Fácil  
**Linguagem recomendada:** C (C11)  
**Linguagens aceitas:** C (C11)  
**Conceitos:** Entrada e saída, streams, EOF, separadores ASCII e estado.

## O desafio

O `wc` (*word count*) conta linhas, palavras e bytes de uma entrada.

Implemente o `oxide-wc`, uma versão simplificada dessa ferramenta. Leia a entrada aos poucos e mantenha as contagens entre leituras.

Pré-requisitos: laços, variáveis e I/O básico. O desafio usa texto ASCII e não exige suporte a Unicode.

## Especificação

Execute `oxide-wc` sem argumentos obrigatórios. Leia bytes de `stdin` até o fim da entrada e conte:

- **Linhas:** ocorrências do byte `\n`.
- **Palavras:** sequências não vazias de bytes que não são separadores.
- **Bytes:** todos os bytes lidos, inclusive os separadores.

Os seis separadores são espaço, `\t`, `\n`, `\r`, `\v` e `\f`. Separadores consecutivos não criam palavras vazias. Uma palavra pode terminar no fim da entrada, sem separador final.

Escreva em `stdout` as contagens de linhas, palavras e bytes, nessa ordem. Use inteiros decimais não negativos, separados por um único espaço, com LF no final. Não acrescente espaços de alinhamento.

Entrada vazia produz `0 0 0` e LF. Uma última linha sem `\n` não aumenta a contagem de linhas.

Considere entradas ASCII, operações de leitura e escrita bem-sucedidas e contagens que cabem no tipo inteiro escolhido. Falhas de I/O e overflow ficam fora do contrato básico.

## Exemplo

```sh
printf 'Hello world\nC is fun\n' | ./oxide-wc
```

Saída exata:

```text
2 5 21
```

A entrada tem duas quebras de linha, cinco palavras e 21 bytes. Os espaços e as quebras de linha contam como bytes.

## Requisitos

- Implemente em C11, apenas com a biblioteca padrão.
- Leia a entrada em fluxo, sem guardar todos os dados na memória. Use memória adicional constante.
- Mantenha o estado necessário para distinguir separadores de palavras.
- Não invoque o `wc` original para calcular o resultado.
- Retorne status zero no sucesso. Escreva em `stdout` apenas as três contagens e o LF final.
- Entregue o código-fonte, as instruções de compilação, os testes e uma explicação do estado usado.

## Casos de teste

| Entrada | Saída esperada, seguida de LF |
|---|---|
| Vazia | `0 0 0` |
| `hello` | `0 1 5` |
| `hello\n` | `1 1 6` |
| `a b\n` | `1 2 4` |
| `a\nb` | `1 2 3` |
| `one   two\n` | `1 2 10` |
| ` \t\n\r\v\f` | `1 0 6` |
| `\r\n` | `1 0 2` |

Os vetores também cobrem espaços nas bordas, uma palavra de 128 KiB e 32768 linhas. Compare as contagens com `LC_ALL=C wc -l -w -c`. Desconsidere os espaços de alinhamento da ferramenta original.

Os vetores públicos ficam em `tests/cases.json`. O [guia de testes](README.md) contém os comandos de compilação e execução. Os [materiais](materials/README.md) fornecem entradas e saídas exatas. Acrescente casos próprios.

## Extensões opcionais

- Aceite um caminho de arquivo como argumento.
- Acrescente as opções `-l`, `-w` e `-c`.
- Compare as leituras com `fgetc` e `fread`.
- Investigue UTF-8, entradas binárias, overflow de contadores e falhas de I/O.

As extensões preservam a execução básica por `stdin` e a saída especificada.

## Como participar

Compartilhe sua implementação no fórum de desafios do Discord, com um exemplo e uma explicação das contagens. Dúvidas, descobertas e soluções parciais também são bem-vindas.

Consulte as [dicas progressivas no Discord](https://discord.com/channels/1561460326136811570/1561825043577573547) quando precisar de apoio.
