---
title: "Inspetor de executáveis PE"
slug: "027-pe-inspector"
area: binary-reverse-engineering
summary: "Inspecione PE32+ e classifique intervalos de RVA com validação de limites e saída JSON."
publishedAt: "2026-10-25"
updatedAt: "2026-10-25"
draft: false
difficulty: "intermediate"
categories: ["build"]
participation: "open"
recommendedLanguage: "C"
acceptedLanguages: ["C", "Rust"]
cardTopics: ["PE", "Parsing binário", "Validação"]
topics: ["PE", "Parsing binário", "Validação"]
featured: false
environment: "Linux x86_64 validado; Windows não executado; implementação em C ou Rust"
---

**Dificuldade:** Intermediário\
**Linguagem recomendada:** C\
**Linguagens aceitas:** C, Rust\
**Conceitos:** PE, parsing binário e validação\
**Ambiente:** Linux x86_64 validado; Windows não executado; implementação em C ou Rust

Os materiais estão disponíveis no [guia local](README.md). O núcleo do starter permanece incompleto para implementação pelo participante. Consulte os requisitos e as limitações de ambiente antes de começar.

## O desafio

Implemente `peinspect arquivo [--rva HEX --size DEC]`. As opções formam um par obrigatório quando presentes. A ferramenta deve ler exemplos didáticos ou de procedência registrada, validar o subconjunto PE definido no contrato e produzir JSON com inventário e classificação da consulta, ou um diagnóstico controlado.

A consulta descreve um intervalo de RVAs; não carrega DLLs, resolve imports ou transfere controle ao entry point. Escolha C ou Rust para uma implementação avaliada. Desenhe o layout de um fixture, identifique as dependências entre campos e use essa representação para justificar os limites de acesso. Comparar implementações é extensão.

### Por que construir esta solução

Arquivo, imagem carregada e espaço de endereçamento são objetos diferentes. Confundi-los produz consultas de RVA incorretas e acessos indevidos a padding, truncamentos ou regiões sem bytes no disco. O desafio é construir um leitor que mantenha essas distinções e rejeite entradas fora do subconjunto aceito. A documentação distingue RVA, posição no arquivo e zero-fill, sem que o leitor precise funcionar como loader ([PE Format](https://learn.microsoft.com/en-us/windows/win32/debug/pe-format)).

### Antes de começar

Leitura de arquivos como bytes; inteiros de largura fixa; little-endian; intervalos semiabertos; diferença entre endereço e offset; testes de unidade. Em C, dominar acesso a buffers sem pressupor alinhamento. Em Rust, conhecer slices, `Result` e conversões numéricas verificadas. Conhecimentos de representação binária, compilação e protocolos binários devem permitir desenhar um layout e justificar cada acesso antes desta atividade.

### Objetivos de aprendizagem

- Identificar DOS header, assinatura PE, COFF header, optional header e section table em um hexdump.
- Produzir um inventário verificável de arquitetura, image base, entry point e seções.
- Implementar consultas que classifiquem bytes de cabeçalho, bytes de seção, zero-fill e região não mapeada.
- Demonstrar rejeição controlada de truncamento, overflow e intervalos ambíguos.
- Justificar as invariantes de acesso e a política de RVA do subconjunto aceito, distinguindo inspeção estrutural de aceitação pelo loader.

### Conceitos trabalhados

Parsing por camadas, representação externa independente de structs da linguagem, aritmética de offsets, validação estrutural, classificação de erros e construção de fixtures independentes. Trabalha-se também a diferença entre reconhecer um formato, aceitar um subconjunto e garantir que um sistema operacional conseguirá executá-lo.

## Especificação

O contrato abaixo define o **subconjunto de inspeção** escolhido para este desafio; aceitação não significa aprovação pelo loader do Windows.

- Arquivos de até 64 MiB; assinatura DOS `MZ`, assinatura `PE\0\0`, `Machine = 0x8664` e optional-header magic `0x20b`. PE32, COFF sem imagem e outras arquiteturas recebem `unsupported_format`.
- Entre 1 e 96 seções. O optional header contém seus campos fixos e a quantidade declarada de data directories, limitada a 16. Seu tamanho declarado deve conter essas estruturas. Bytes adicionais presentes são ignorados. Os diretórios são inventariados como números opacos: seu conteúdo não é percorrido.
- `SizeOfHeaders` deve cobrir a section table e caber no arquivo. Todo intervalo raw não vazio deve estar integralmente no arquivo, após os cabeçalhos. Intervalos raw entre seções não podem sobrepor-se.
- O intervalo consultável de uma seção é `[VirtualAddress, VirtualAddress + VirtualSize)`; seu prefixo raw tem `min(VirtualSize, SizeOfRawData)` bytes. Seções com ambos os tamanhos zerados são vazias; `VirtualSize = 0` com dados raw recebe `unsupported_layout`. Intervalos virtuais não se sobrepõem nem invadem cabeçalhos. Padding raw além de `VirtualSize` é listado, sem RVAs consultáveis.
- A consulta contém `size` entre 1 e 4096 e RVA inicial de 32 bits. Par incompleto, valores inválidos ou fim acima de `2^32` são uso inválido. Início em lacuna produz `unmapped`; início mapeado cujo intervalo cruza uma fronteira produz `cross_region`. Caso contrário, classifique cabeçalhos, prefixo raw ou zero-fill. Cabeçalhos correspondem ao próprio offset; zero-fill não possui bytes no arquivo.
- Somas e multiplicações são verificadas antes de qualquer acesso. Um limite exclusivo de RVA pode ser `2^32`, mas não superior. Conversões para índices locais precisam preservar o valor. Alinhamentos, checksum, permissões de execução e validade de imports ficam fora da validação obrigatória; bytes de overlay são permitidos e ignorados.

O JSON contém `schema_version=1`, `machine="0x8664"`, `image_base`, `entry_rva`, `size_of_headers`, `data_directories`, `sections` e `query`. Cada seção contém `name_hex` (16 dígitos hexadecimais minúsculos), `rva`, `virtual_size`, `raw_offset` e `raw_size`, na ordem original. `query` é `null` ou contém `rva`, `size`, `kind`, `section_index` e `file_offset`. `kind` admite `headers`, `section_raw`, `zero_fill`, `cross_region` e `unmapped`. `section_index` identifica a seção do início, base zero, ou é `null`. `file_offset` contém offset somente para consultas inteiramente em headers/raw; caso contrário é `null`. Endereços e offsets usam `0x` seguido de dígitos hexadecimais minúsculos, sem zeros adicionais; tamanhos são inteiros. `name_hex` conserva exatamente 16 dígitos hexadecimais minúsculos, sem prefixo. `data_directories` contém objetos `{"address": "0x...", "size": N}` na ordem declarada. `address` é opaco, inclusive no diretório de certificados; não representa sempre um RVA.

Complemento de serialização aprovado pelo responsável em 25/10/2026. Na mesma data, foi aprovado o [catálogo de diagnósticos e transporte JSON](materials/README.md#interface-de-diagnóstico): sucesso em stdout; falha em stderr, com stdout vazio.

Violações simultâneas não têm precedência global obrigatória. Um diagnóstico é admissível quando sua condição no catálogo é satisfeita pelos bytes da entrada. Para derivá-lo, cada campo usado no cálculo deve estar inteiramente no arquivo; offsets, tamanhos e fins devem ser calculados sem overflow. Use os offsets declarados: a section table começa em `e_lfanew + 24 + SizeOfOptionalHeader`, mesmo quando outro teste já poderia rejeitar esse tamanho. Não leia campos ausentes nem suponha o tamanho usual de 112 bytes para reposicionar a tabela. A validação semântica de outra estrutura não é pré-condição para diagnosticar um intervalo cujos campos estão presentes.

Os conjuntos de códigos da suíte registram essas alternativas, com a derivação dos casos multiviolação nos materiais. Não é obrigatório emitir cada código do catálogo em alguma entrada: outro diagnóstico admissível pode identificar a mesma entrada inválida. Isso não permite aceitar o arquivo nem produzir inventário parcial. A aprovação preserva a liberdade de ordem das checagens.

Status: 0 para inspeção/consulta classificadas, 2 para uso inválido, 3 para arquivo rejeitado e 4 para I/O. Falhas estruturais informam código e campo/offset, sem inventário parcial.

RVA (*relative virtual address*) é o endereço relativo à base da imagem. Neste contrato, “raw” identifica os bytes de uma seção armazenados no arquivo, em contraste com seu intervalo virtual.

## Exemplo

Considere `SizeOfHeaders = 0x200` e uma seção com `VirtualAddress = 0x1000`, `VirtualSize = 0x300`, `SizeOfRawData = 0x200` e `PointerToRawData = 0x200`.

| RVA inicial | Tamanho | Classificação | Offset no arquivo |
| --- | --- | --- | --- |
| `0x80` | 1 | `headers` | `0x80` |
| `0x1010` | 1 | `section_raw` | `0x210` |
| `0x11ff` | 2 | `cross_region` | `null` |
| `0x1200` | 1 | `zero_fill` | `null` |
| `0x1300` | 1 | `unmapped` | `null` |

Esta tabela é um exemplo normativo da classificação. Ela não representa uma execução já realizada.

## Requisitos

Código do leitor; especificação da saída; fixtures e seus valores esperados; comandos reproduzíveis de build e inspeção; hexdump anotado de um fixture; justificativa das invariantes de acesso e da política de RVA. Inclua a origem de cada exemplo e os resultados dos casos mínimos.

A explicação técnica deve mostrar por que cada acesso está dentro dos limites e por que cada intervalo recebe sua classificação. Um relato do aprendizado e comparações com leitores de produção são opcionais. Caso uma ferramenta externa seja usada para comparação, registre sua versão e as divergências de escopo.

### Roteiro de desenvolvimento

1. Anote manualmente os limites de cada estrutura no fixture válido e defina a representação de saída.
2. Estabeleça as invariantes que permitem acessar os cabeçalhos e a tabela de seções, com aritmética verificada antes de qualquer leitura ou conversão para índice.
3. Implemente a leitura por camadas e as rejeições de formato, tamanho, truncamento, overflow e intervalos ambíguos previstas no contrato.
4. Calcule os resultados de três RVAs próximos da fronteira raw/zero-fill e implemente a classificação de consultas, incluindo cabeçalhos, lacunas e cruzamentos de fronteira.
5. Introduza uma alteração por fixture inválido, defina o diagnóstico esperado e teste a preservação do processo e a ausência de inventário parcial.
6. Valide campos, JSON e status contra os fixtures e os resultados independentes fornecidos, mantendo distinta a política do desafio e qualquer tolerância de ferramentas externas.

### Materiais fornecidos

Consulte o [inventário dos materiais](materials/README.md). O clube fornece gerador de fixtures, manifesto de offsets, resultados independentes e validador JSON. O starter Rust preserva as tarefas de implementação.

## Casos de teste

O núcleo está concluído quando os valores concordam com os fixtures e cada rejeição preserva o processo.

- Fixture com `SizeOfHeaders = 0x200` e seção `VA=0x1000`, `VirtualSize=0x300`, `RawSize=0x200`, `RawPointer=0x200`: RVA `0x1010` corresponde ao offset `0x210`; `0x1200` é zero-fill; `0x1300` é unmapped.
- A consulta `0x11ff` com tamanho 2 recebe `cross_region`; `0x80` com tamanho 1 pertence aos cabeçalhos.
- Truncamentos no DOS header, PE header, optional header, section table e último byte raw rejeitam a entrada. Se houver mais de uma violação, aceite um dos diagnósticos admissíveis do catálogo, conforme a regra de derivação e os conjuntos dos materiais; não se exige que a implementação emita todos os códigos de truncamento.
- Inclua raw maior que virtual, sobreposição raw, sobreposição virtual, número excessivo de seções e soma de RVA acima de `2^32`.
- Um arquivo com bytes adicionais de overlay mantém os valores originais. Nenhum teste exige executar o PE.

A [suíte executável](tests/check.py) verifica 76 casos, incluindo os limites de arquivo e consulta. O [catálogo auxiliar de diagnósticos](materials/README.md#interface-de-diagnóstico) fixa os códigos dos casos isolados e seu transporte JSON.

## Extensões opcionais

Opcionalmente, compare os campos públicos com `llvm-readobj` e explique uma diferença entre o contrato didático e a tolerância de um leitor de produção. A ferramenta independente oferece inspeção de cabeçalhos e seções; sua saída ajuda a conferir valores, mas não estabelece a política particular deste exercício ([manual de llvm-readobj](https://releases.llvm.org/20.1.0/docs/CommandGuide/llvm-readobj.html)).

Também é possível descrever as verificações adicionais necessárias para analisar imports ou comparar as decisões de representação com ELF. Essas análises não tornam obrigatório percorrer diretórios, executar o PE ou ampliar o subconjunto aceito.

Imports, exports, relocations, resources e comparação PE/ELF são extensões. Maior tolerância exige contrato e fixtures próprios. Certificados merecem estudo específico: seu diretório usa offset de arquivo ([PE Format](https://learn.microsoft.com/en-us/windows/win32/debug/pe-format)).

## Como participar

Desenvolva a solução em seu próprio repositório. Compartilhe código, ambiente, resultados e justificativa técnica na conversa do clube. Você pode apresentar uma tentativa incompleta; descreva o requisito ainda não atendido e um caso pequeno que permita reproduzir a dúvida.

Organize a memória técnica por contrato, decisões e invariantes, falhas e recursos, verificação, ambiente e limitações. Não há limite de páginas neste pacote.

### Referências orientadas

- [Microsoft — PE Format](https://learn.microsoft.com/en-us/windows/win32/debug/pe-format): começar por “General Concepts”, optional header e “Section Table”; identificar a origem dos campos usados.
- [LLVM — llvm-readobj](https://releases.llvm.org/20.1.0/docs/CommandGuide/llvm-readobj.html): localizar as opções de file headers e sections para construir a comparação.
- **Código real:** [LLVM — COFFObjectFile.cpp](https://github.com/llvm/llvm-project/blob/llvmorg-20.1.8/llvm/lib/Object/COFFObjectFile.cpp). Ler `getObject`, sua chamada a `Binary::checkOffset` e `COFFObjectFile::getRvaPtr`; explicar quais pressupostos e verificações estão distribuídos entre funções. É leitura crítica de produção, não implementação a copiar.

As [referências registradas](materials/README.md#origem-revisões-e-licenças) identificam a consulta de 25/10/2026 e a revisão LLVM `llvmorg-20.1.8`. A leitura de código real é complementar. A documentação necessária para interpretar o contrato continua indicada nas seções correspondentes.
