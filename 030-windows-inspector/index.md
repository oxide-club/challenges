---
title: "Inspetor de recursos de um processo Windows"
slug: "030-windows-inspector"
area: systems-fundamentals
summary: "Inspecione um alvo Windows cooperativo em três fases e identifique a origem de cada informação."
publishedAt: "2026-10-25"
updatedAt: "2026-10-25"
draft: true
difficulty: "advanced"
categories: ["build"]
participation: "open"
recommendedLanguage: "C++"
acceptedLanguages: ["C++"]
cardTopics: ["Windows", "Inspeção de processos", "Memória virtual"]
topics: ["Windows", "Inspeção de processos", "Memória virtual"]
featured: false
environment: "Windows x64 em VM; alvo e inspetor de 64 bits; C++ com WinAPI; conta comum"
---

**Dificuldade:** Avançado
**Linguagem recomendada:** C++
**Linguagens aceitas:** C++
**Conceitos:** Windows, inspeção de processos, memória virtual
**Ambiente:** Windows x64 em VM; alvo e inspetor de 64 bits; C++ com WinAPI; conta comum

**Em revisão.** Os materiais de preparação estão disponíveis no [guia local](README.md). O núcleo do starter permanece incompleto. Consulte as evidências e limitações de ambiente; a publicação depende de revisão independente, piloto e aprovação editorial.

**Ambiente indisponível:** build e execução Windows não foram realizados.

## O desafio

Desenvolva `wininspect`, um inspetor que inicia e acompanha somente o alvo didático fornecido pelo clube. O clube fornecerá também a DLL benigna e o protocolo das três fases — inicial, recursos ativos e recursos encerrados — como fixtures validadas. Sua solução deve coordenar essas fases e produzir, para cada uma, um relatório de threads, módulos, handles selecionados e regiões didáticas de memória.

Use o inventário publicado pelo alvo como referência e identifique no relatório a origem de cada dado. Os TIDs e o módulo serão confrontados com consultas externas pelas APIs públicas; os três handles selecionados terão inventário cooperativo, produzido pela instrumentação do próprio alvo. A saída não pode apresentar esse inventário como uma enumeração externa ou completa de handles.

A correção depende do cumprimento do contrato abaixo, incluindo sincronização de fases, direitos mínimos, limites das tentativas e esperas, classificação de erros e cleanup. Justifique como a coordenação estabiliza os objetos didáticos e por que ela não torna transacional todo o processo. Produzir um alvo ou uma DLL próprios será opcional; a implementação do inspetor e sua integração com as fixtures fornecidas são o núcleo do desafio.

### Por que construir esta solução

Inspecionar um processo Windows exige tratar PID, TID, módulo, handle e região de memória conforme seus contratos públicos. O desafio é produzir relatórios verificáveis sobre um alvo cooperativo, conciliando aquilo que o alvo publica com aquilo que o inspetor consulta externamente.

A documentação de [`CreateToolhelp32Snapshot`](https://github.com/MicrosoftDocs/sdk-api/blob/656e9656bfaef34dd29cd7ee9e1146aec17e924c/sdk-api-src/content/tlhelp32/nf-tlhelp32-createtoolhelp32snapshot.md) descreve particularidades de arquitetura e alterações concorrentes de módulos. A solução usará coordenação explícita para tornar verificáveis os objetos do exercício, sem exigir uma contagem fixa de todos os recursos do processo.

### Antes de começar

Processos, threads, memória virtual, linking dinâmico e ponteiros de largura adequada. Saber compilar um executável e uma DLL em C/C++, interpretar erros e trabalhar com sincronização básica. O desafio [027-pe-inspector](../027-pe-inspector/index.md) é preparação recomendada; Linux não é requisito operacional.

### Objetivos de aprendizagem

- Identificar os TIDs e o módulo didático de um processo próprio usando APIs documentadas.
- Comparar regiões de memória reservadas, comprometidas e protegidas, preservando as distinções retornadas pela API.
- Relacionar três handles selecionados ao inventário produzido pelo próprio alvo.
- Explicar por que um snapshot não equivale a uma visão transacional de todas as estruturas do Windows.
- Demonstrar tratamento de erros, direitos mínimos necessários e fechamento de recursos.

### Conceitos trabalhados

WinAPI, Toolhelp, objetos e handles, `VirtualQueryEx`, estados de memória, direitos de consulta e ciclo de vida. O participante distinguirá dados observados externamente e informações fornecidas voluntariamente pelo alvo. [`VirtualQueryEx`](https://github.com/MicrosoftDocs/sdk-api/blob/656e9656bfaef34dd29cd7ee9e1146aec17e924c/sdk-api-src/content/memoryapi/nf-memoryapi-virtualqueryex.md) exige `PROCESS_QUERY_INFORMATION` para o handle utilizado e agrupa páginas por atributos; não deve ser descrita como uma API de leitura do conteúdo da memória.

## Especificação

O inspetor iniciará o alvo próprio e conservará sua identidade durante a sessão. Não aceitará um PID arbitrário como modo obrigatório. Ambos registrarão arquitetura e identificador da sessão. A comunicação de controle poderá usar pipes herdados; seu formato será simples e documentado.

Na fase ativa, o alvo criará exatamente dois worker threads didáticos, carregará uma DLL própria por caminho absoluto e manterá três handles selecionados: dois eventos e um arquivo temporário. Publicará os TIDs, caminho da DLL e identificadores lógicos desses três recursos. O inventário de handles virá da instrumentação das criações e fechamentos no alvo, com consulta local de propriedades quando pertinente. Ele não será apresentado como enumeração completa dos handles do processo. As [funções públicas de handles](https://github.com/MicrosoftDocs/win32/blob/ca8274decead49403d70ceeed4af8d4ca74eaf11/desktop-src/SysInfo/handle-and-object-functions.md) orientarão o tratamento de propriedade e fechamento.

O alvo reservará três páginas contíguas: uma permanecerá reservada, outra será comprometida como `PAGE_READWRITE` e a terceira como `PAGE_READONLY`. Publicará somente o intervalo necessário à consulta. O inspetor usará `VirtualQueryEx` para descrever estado, proteção e tamanho das regiões que intersectam esse intervalo, sem ler ou alterar seus bytes.

Cada fase terá mensagem de prontidão e confirmação do inspetor. Workers permanecerão em espera durante a coleta; a DLL e os recursos selecionados só mudarão após confirmação. Isso estabiliza os objetos do exercício, sem congelar o runtime inteiro. Na fase final, o alvo encerrará e aguardará os workers, descarregará a DLL, liberará a região e fechará os três handles antes de anunciar prontidão.

A enumeração de threads filtrará `th32OwnerProcessID`; flags de snapshot não serão interpretadas como filtro automático de threads pelo PID informado. As estruturas receberão o tamanho exigido pela API. Repetições de `ERROR_BAD_LENGTH` terão limite de dez tentativas e prazo total de dois segundos. Falha persistente será registrada, sem loop infinito. Cada espera entre processos terá prazo declarado, de cinco segundos por padrão.

A saída conterá sessão, arquitetura, fase, categoria, origem do dado, identificador lógico e atributos observados. A execução normal produz três arquivos JSONL, um para cada fase 0, 1 e 2, no formato do [guia local](README.md). Endereços e TIDs serão dados da execução, nunca fixtures fixas. Registre nome da API e `GetLastError` quando houver falha. Permissão negada, alvo encerrado e ambiente incompatível serão resultados distintos. Não solicite `PROCESS_ALL_ACCESS`, elevação ou privilégios de debug para cumprir o núcleo.

**Complemento aprovado em 25/10/2026:** o formato anterior não explicitava arquitetura nem representação dos erros. O responsável aprovou `architecture: "x64"`, a categoria `error` com origem `inspector`, atributos `kind`, `api`, `error` e três arquivos JSONL na resposta `call_40bbb1cb744d4a95a946c18134f2904a`, item 0. O [catálogo](materials/errors.md) define as seis classes e separa erros observados de exemplos sintéticos. Isso completa o formato dos entregáveis já exigidos; não declara execução nativa.

### Esclarecimento aprovado: reúso de TID

Em 25/10/2026, o responsável aprovou distinguir ausência de identidade suficiente de falha da solução. Antes, o verificador tratava a reaparição de qualquer TID didático na fase final como continuidade do worker. Essa conclusão depende da hipótese de não reúso: o formato atual só contém TID, e o Windows pode atribuí-lo a outra thread.

Se outro identificador lógico tiver o mesmo TID de um worker da fase ativa, a verificação termina com status 77 e `INCONCLUSIVO`, após conferir os demais requisitos. Isso não aprova a execução e não encobre outras falhas. Um registro ainda identificado como `worker-0` ou `worker-1` na fase final continua sendo incoerente e recebe status 1. Nenhum campo novo é exigido. A confirmação nativa dessa distinção permanece pendente, junto com a validação Windows. A decisão está no registro da resposta à revisão 3 (registro histórico retirado deste repositório).

## Exemplo

Na fase ativa, o alvo publica dois TIDs didáticos. O inspetor deve encontrá-los na enumeração externa filtrada pelo PID do alvo. A existência de outras threads não invalida o resultado.

Os dois eventos e o arquivo temporário aparecem como inventário cooperativo. Essa origem deve permanecer explícita, mesmo quando seus registros são apresentados junto às consultas externas.

## Requisitos

Código do inspetor `wininspect` e instruções de build e execução com as fixtures do clube; três relatórios, logs e testes de erro. Inclua uma justificativa de até três páginas sobre permissões, origem dos dados, sincronização das fases e limites dos snapshots. Identifique quem possui e fecha cada recurso, inclusive nos caminhos de falha.

O relatório deve distinguir consultas externas de threads, módulos e regiões do inventário cooperativo de handles. A revisão da coordenação e dos caminhos de cleanup é obrigatória, juntamente com a demonstração funcional da solução. Não é necessário entregar uma implementação própria do alvo ou da DLL.

### Roteiro de desenvolvimento

1. Leia o protocolo de fases e as fixtures do clube; defina as relações entre PID, TID, módulo, handle e região virtual, indicando origem dos dados e ownership dos recursos.
2. Implemente a inicialização do alvo, a conservação de sua identidade, as mensagens de prontidão e confirmação e os prazos de espera. Capture a fase inicial e identifique quais valores variam entre execuções.
3. Implemente a coleta externa de threads e módulos, com filtro por `th32OwnerProcessID`, tamanhos de estruturas corretos e repetição limitada de `ERROR_BAD_LENGTH`. Na fase ativa, confronte os dois TIDs e a DLL publicados com as listas públicas.
4. Integre o inventário cooperativo dos três handles selecionados, preservando sua origem e os registros de criação e fechamento. Não o apresente como resultado de enumeração universal pelo inspetor.
5. Consulte somente o intervalo didático por `VirtualQueryEx`, separando `State`, `Protect` e `Type`, sem ler ou alterar o conteúdo da memória.
6. Complete a coordenação da fase final, capture o relatório e explique quais ausências são verificáveis e quais contagens globais permanecem instáveis.
7. Exercite erros de DLL, encerramento antecipado e direitos insuficientes. Verifique prazos, classificação dos erros e fechamento de recursos em caminhos normais e de falha; repita a sessão para demonstrar cleanup.

### Materiais fornecidos e pendentes

Consulte os [materiais e suas pendências](materials/README.md). As fontes fornecidas ainda exigem validação Windows pelo clube; essa responsabilidade não é transferida ao participante.

## Casos de teste

- Os dois TIDs publicados aparecem na fase ativa e deixam de ser esperados após o encerramento coordenado; nenhuma contagem total de threads é fixada.
- A DLL própria aparece com identidade verificável durante a fase ativa.
- Os três handles selecionados têm histórico coerente de criação e fechamento.
- O inspetor distingue as páginas reservada, gravável e somente leitura.
- Testes com caminho de DLL inexistente, alvo encerrado antecipadamente e handle de consulta insuficiente produzem erros claros, sem elevação automática.
- Uma execução repetida termina sem processos pendentes, e todos os handles pertencentes à ferramenta têm fechamento demonstrável.
- Os três relatórios registram sessão, fase, categoria, origem do dado, identificador lógico e atributos observados, sem endereços ou TIDs fixos nas fixtures de verificação.
- A solução respeita a prontidão e a confirmação em todas as fases, os limites de repetição e os prazos declarados; a justificativa identifica quais recursos ficam estáveis durante cada coleta.
- O inventário dos três handles é identificado como cooperativo, e sua procedência não é confundida com a coleta externa das demais categorias.

Estes casos especificam a verificação exigida. O [guia local](README.md) identifica a cobertura executada, os comandos e as verificações ainda pendentes.

## Extensões opcionais

Opcionalmente, compare três conceitos com Linux, descrevendo uma semelhança e uma diferença para cada um. Termos familiares não têm equivalência automática entre os sistemas: evite igualar handle a file descriptor ou estrutura interna a interface pública. Essa comparação conceitual amplia a compreensão e não é requisito de correção do inspetor.

Também é possível investigar quais mudanças em objetos não coordenados continuariam possíveis durante uma coleta. A justificativa obrigatória sobre os limites do snapshot e a revisão da sincronização das fases permanecem nos entregáveis do núcleo.

Extensões: produzir alvo e DLL próprios que respeitem o mesmo contrato, TLS, Rust por FFI e observação de PEB/TEB numa versão explicitamente identificada. Estruturas internas não integram o contrato obrigatório. O exercício não inclui drivers, inspeção de processos protegidos, leitura arbitrária de memória ou enumeração universal de handles. Conexões: desafio `025-rust-c-ffi` e desafio `027-pe-inspector`.

## Como participar

Desenvolva a solução em seu próprio repositório. Compartilhe código, ambiente, resultados e justificativa técnica na conversa do clube. Você pode apresentar uma tentativa incompleta; descreva o requisito ainda não atendido e um caso pequeno que permita reproduzir a dúvida.

Organize a memória técnica por contrato, decisões e invariantes, falhas e recursos, verificação, ambiente e limitações. Respeite os limites de páginas quando indicados nos requisitos.

### Referências orientadas

1. [Microsoft — `CreateToolhelp32Snapshot`](https://github.com/MicrosoftDocs/sdk-api/blob/656e9656bfaef34dd29cd7ee9e1146aec17e924c/sdk-api-src/content/tlhelp32/nf-tlhelp32-createtoolhelp32snapshot.md): estudar flags, filtro de threads, arquitetura e erros transitórios. Diferentemente da recomendação de repetir até sucesso, o exercício impõe prazo e dez tentativas. Pergunta: por que informar PID não filtra automaticamente threads?
2. [Microsoft — `VirtualQueryEx`](https://github.com/MicrosoftDocs/sdk-api/blob/656e9656bfaef34dd29cd7ee9e1146aec17e924c/sdk-api-src/content/memoryapi/nf-memoryapi-virtualqueryex.md): localizar direitos necessários, agrupamento de páginas e significado do retorno. O exercício consulta somente o intervalo didático. Pergunta: qual atributo distingue reserva de compromisso sem ler bytes?
3. [Microsoft — Handle and Object Functions](https://github.com/MicrosoftDocs/win32/blob/ca8274decead49403d70ceeed4af8d4ca74eaf11/desktop-src/SysInfo/handle-and-object-functions.md): seguir `GetHandleInformation` e `CloseHandle`; relacionar a documentação ao inventário próprio. A lista de funções não fornece enumeração universal de handles. Pergunta: quem deve fechar cada handle recebido?
4. [Microsoft — Taking a Snapshot and Viewing Processes](https://github.com/MicrosoftDocs/win32/blob/ca8274decead49403d70ceeed4af8d4ca74eaf11/desktop-src/ToolHelp/taking-a-snapshot-and-viewing-processes.md): código real de exemplo, não ferramenta de produção. Ler inicialização de `dwSize`, iteração e caminhos de cleanup; identificar por que o pedido amplo de acesso do exemplo deve ser reduzido neste desafio.

As referências WinAPI e o exemplo real usam revisões fixadas dos repositórios oficiais MicrosoftDocs: `sdk-api` em `656e9656bfaef34dd29cd7ee9e1146aec17e924c` e `win32` em `ca8274decead49403d70ceeed4af8d4ca74eaf11`, consultadas em 25/10/2026. A leitura de código real é complementar; a documentação necessária para interpretar o contrato continua indicada nas seções correspondentes.
