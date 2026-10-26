---
title: "IPC e snapshots consistentes entre processos"
slug: "031-ipc-snapshots"
area: systems-fundamentals
summary: "Construa um protocolo local autenticado com memória compartilhada, mutex e snapshots consistentes."
publishedAt: "2026-10-25"
updatedAt: "2026-10-25"
draft: false
difficulty: "advanced"
categories: ["build"]
participation: "open"
recommendedLanguage: "C"
acceptedLanguages: ["C"]
cardTopics: ["IPC", "Memória compartilhada", "Sincronização"]
topics: ["IPC", "Memória compartilhada", "Sincronização"]
featured: false
environment: "Linux x86-64 em VM; C; mesma libc e ABI nos dois programas; usuário comum"
---

**Dificuldade:** Avançado
**Linguagem recomendada:** C
**Linguagens aceitas:** C
**Conceitos:** IPC, memória compartilhada e sincronização.
**Ambiente:** Linux x86-64 em VM; C; mesma libc e ABI nos dois programas; usuário comum

Os materiais estão disponíveis no [guia local](README.md). O núcleo do starter permanece incompleto para implementação pelo participante. Consulte os requisitos e as limitações de ambiente antes de começar.

## O desafio

Desenvolva `target` e `observer` para executar o protocolo local especificado, compartilhar o contador e produzir snapshots consistentes. A solução deve autenticar a sessão, validar mensagens e sequências, transferir a capacidade de acesso à região, sincronizar todos os acessos e encerrar recursos em sucesso e falha.

Demonstre os três comandos autorizados, as tentativas recusadas, as atualizações concorrentes no modo de teste e a desconexão inesperada, correlacionando os eventos. A correção exige tanto os comportamentos do contrato quanto a justificativa das invariantes, da exclusão mútua e das fronteiras de confiança; testes de coerência não dispensam a análise de sincronização.

Comandos não receberão endereços arbitrários ou código. O núcleo não inclui injeção, processos de terceiros ou privilégio administrativo.

### Por que construir esta solução

Instrumentar um processo cooperativo exige decisões sobre identidade, autorização, consistência e encerramento de recursos. O desafio exige explicitar o que o alvo publica, quem recebe acesso e quais alterações ele aceita.

Unix sockets transferem descritores; [`SO_PEERCRED`](https://git.kernel.org/pub/scm/docs/man-pages/man-pages.git/plain/man/man7/unix.7?h=man-pages-6.16) fornece credenciais da conexão. O exercício combina essas capacidades com controle de sessão e explicita os limites de confiar em participantes cooperativos sob o mesmo UID.

### Antes de começar

Processos, descritores, sockets, memória virtual, mutexes e data races em C. Saber tratar leituras parciais, intervalos numéricos e ownership. Preparação recomendada: laboratório `019-atomics-lab` e laboratório `022-page-protection-lab`.

### Objetivos de aprendizagem

- Implementar três comandos autorizados e rejeitar comandos fora do contrato.
- Relacionar identidade do peer, segredo da sessão e capacidade concedida por um descritor.
- Produzir snapshots sem leitura concorrente desprotegida de dados compartilhados.
- Demonstrar timeout, desconexão e cleanup sem reutilizar recursos inválidos.
- Explicar por que o protótipo não constitui isolamento contra um observador malicioso que já recebeu memória gravável.

### Conceitos trabalhados

IPC, autenticação, validação, memória compartilhada e sincronização. O projeto distingue identificadores numéricos de recursos transferidos e acompanha o lifetime dos recursos mantidos por cada processo.

## Especificação

O alvo criará um socket `AF_UNIX`/`SOCK_STREAM` num diretório privado da sessão, com diretório `0700` e socket `0600`. Usará sessão nova e token aleatório de 256 bits gerado pelo SO. Iniciará o observador e entregará o token por pipe herdado reservado a esse fim; token não aparecerá em argumentos, ambiente ou logs. O alvo verificará o UID por `SO_PEERCRED` e o token antes de disponibilizar comandos ou descritores. A sessão aceitará um observador autenticado; credencial ou token incorretos encerrarão a conexão sem modificar o contador.

O protocolo terá linhas ASCII de até 256 bytes, incluindo o LF final, com um espaço entre campos. Inteiros serão decimais sem sinal nem zeros iniciais, exceto `0`; `seq` é `uint64_t`, começa em 1, cresce sem wrap e deve ser o próximo esperado. O token terá 64 dígitos hexadecimais minúsculos. Leituras parciais não completam mensagens.

| Pedido | Resposta de sucesso |
|---|---|
| `HELLO 1 <token>` | `OK 0 HELLO <bytes_da_região>` |
| `SNAPSHOT <seq>` | `OK <seq> STATE <geração> <contador> <counter_xor>` |
| `SET_COUNTER <seq> <valor>` | `OK <seq> STATE <geração> <contador> <counter_xor>` |
| `STOP <seq>` | `OK <seq> STOP` |

Erros seguem `ERR <seq> <código>`, com 0 se a sequência não for identificável. Com sequência esperada, opcode desconhecido na forma `OP <seq>` produz `COMMAND`; valor inválido de `SET_COUNTER` produz `VALUE`. Ambos consomem sequência sem mudar estado. Sintaxe, campos extras ou linha longa (`FRAME`), versão (`VERSION`), autenticação (`AUTH`) e sequência incorreta (`SEQ`) fecham a conexão. Pré-autenticação, encerre só a tentativa; depois, invalide a sessão. `TIMEOUT`, `RESOURCE` e `STATE` também invalidam, respondendo quando possível. Quando a sequência esperada for `UINT64_MAX`, somente `STOP` será aceito; qualquer outro comando produz `STATE`, preserva o estado e invalida a sessão. Não incremente nem reutilize essa sequência.

O alvo criará e dimensionará um `memfd`; um único descritor por `SCM_RIGHTS` acompanhará `OK 0 HELLO`. O observador verificará quantidade e tamanho por `fstat` antes de mapear; depois de mapear, adquirirá o mutex e verificará a versão antes de acessar os demais dados, fechando descritores inesperados. O nome do objeto será apenas diagnóstico, conforme seu [contrato público](https://git.kernel.org/pub/scm/docs/man-pages/man-pages.git/plain/man/man2/memfd_create.2?h=man-pages-6.16).

A região terá versão 1, geração 0, contador 0 e `counter_xor = UINT64_MAX`, todos `uint64_t`, além do mutex com atributos `PTHREAD_PROCESS_SHARED` e `PTHREAD_MUTEX_ROBUST`. Invariantes: contador entre 0 e 1.000.000 e `counter_xor == (contador ^ UINT64_MAX)`. Todos os acessos ocorrerão sob esse [mutex entre processos](https://git.kernel.org/pub/scm/docs/man-pages/man-pages.git/plain/man/man3/pthread_mutexattr_setpshared.3?h=man-pages-6.16). Ambos mapearão a região como gravável para operá-lo: a capacidade concedida supera a leitura lógica.

`SET_COUNTER` aceita 0–1.000.000, atribui o valor, recalcula o redundante e incrementa geração, mesmo se o valor repetir. Somente em `--test-worker`, uma worker faz `contador = (contador + 1) % 1000001` e a mesma atualização de geração/redundante, aguardando 10 ms entre operações. Valide a possibilidade de incrementar a geração antes de alterar qualquer campo. Overflow produz `STATE`, preserva o estado e invalida a sessão; não há wrap.

Cada resposta `STATE` contém cópia sob mutex; `SNAPSHOT` não altera geração. A leitura posterior do mapeamento também exige mutex e cópia privada: sua geração deve ser maior ou igual à respondida. Registre-a como observação posterior; gerações iguais exigem dados iguais. Repetir leituras comuns com contador de versão não constitui seqlock sem data races.

Cada operação, inclusive aquisição do mutex, terá prazo de dois segundos. `STOP` encerra a worker, confirma e fecha a conexão; o observador libera recursos e termina. O alvo aguarda o filho antes do cleanup compartilhado. Falha ou morte de peer invalida a sessão. `EOWNERDEAD` invalida com `STATE`, sem recuperação da sessão; libere o ownership recebido sem declarar o estado consistente e encerre os usuários antes de liberar a região. Destrua o mutex somente destravado e sem usuários; encerre os usuários antes de desmontar a região. Feche descritores e remova socket e diretório da sessão.

### Esclarecimentos aprovados na preparação

Em 25/10/2026, o responsável aprovou: limite de 256 bytes incluindo LF; em `UINT64_MAX`, aceitar somente STOP e invalidar os demais pedidos com STATE sem alterar dados; mutex robusto entre processos, EOWNERDEAD sem recuperação da sessão e encerramento de usuários antes de liberar a região. Essas decisões fecham ambiguidades do contrato curricular. O layout e o transporte auxiliares estão no [guia local](README.md).

Os registros originais de aprovação (registro histórico retirado deste repositório) foram conferidos pela revisão independente. As mensagens do responsável permanecem preservadas privadamente; os registros e hashes históricos foram retirados deste repositório.

| Esclarecimento de 25/10/2026 | Regra anterior | Regra aprovada | Impacto na verificação | Aprovação |
| --- | --- | --- | --- | --- |
| Momento da verificação de versão | O caderno e a redação inicial pediam verificar a versão antes de mapear. | Confira quantidade de descritores e tamanho por `fstat` antes de mapear. Depois de mapear, adquira o mutex e confira a versão antes de acessar os demais dados. | O fixture de versão inválida precisa ter tamanho e mutex válidos. A ordem dos acessos exige também auditoria da implementação. | Registro privado 05 |
| Morte do dono do mutex | O caderno dizia “sem recuperação obrigatória”, permitindo interpretar recuperação como opcional. | `EOWNERDEAD` invalida a sessão; não recupere os dados nem continue os comandos. Libere o ownership recebido sem `pthread_mutex_consistent`, encerre todos os usuários e somente depois libere a região. | Exija STATE, conexão encerrada, estado não recuperado e encerramento dos usuários; uma implementação que continua a sessão é rejeitada. | Registro privado 02 |

## Exemplo

Em uma sessão autenticada, sem `--test-worker`, a sequência abaixo parte do estado inicial. O token e a transferência do descritor foram omitidos deste exemplo:

```text
SNAPSHOT 1
OK 1 STATE 0 0 18446744073709551615
SET_COUNTER 2 7
OK 2 STATE 1 7 18446744073709551608
SNAPSHOT 3
OK 3 STATE 1 7 18446744073709551608
STOP 4
OK 4 STOP
```

As linhas alternam pedido e resposta; cada linha termina em LF. Uma atribuição repetida de `7` também deve incrementar a geração.

## Requisitos

Forneça também um build separado com `-DOX_TEST_HOOKS` e opção `--test-sequence-max`, conforme o guia local, para verificar a sequência máxima. O build normal deve recusar essa opção.

Executáveis, instruções, contrato, logs e testes; modelo de ameaças de até duas páginas. Identifique quem cria, transfere, fecha e desmonta cada recurso, inclusive nas falhas.

Inclua a justificativa das invariantes, dos pontos protegidos pelo mutex, do tratamento de overflow e da relação entre a resposta `STATE` e a observação posterior da região. O modelo de ameaças deve explicar a diferença entre autorização lógica dos comandos e a memória gravável concedida ao observador. Essa análise e a revisão de sincronização integram a correção do desafio.

### Roteiro de desenvolvimento

1. Defina o ciclo de vida da sessão e desenhe quais capacidades existem antes e depois de autenticar e transferir o descritor. Identifique quem cria, transfere, fecha e desmonta cada recurso.
2. Implemente framing, validação, autenticação e sequências do protocolo. Defina as respostas, o consumo de sequência, o estado preservado e a invalidação exigidos para cada mensagem inválida.
3. Implemente a região compartilhada, suas invariantes e a exclusão mútua entre processos. Revise todos os acessos, inclusive cópias de resposta e leituras posteriores do observador; valide o incremento de geração antes de alterar campos.
4. Complete `SNAPSHOT`, `SET_COUNTER` e `STOP`. Acompanhe `snapshot → set_counter → snapshot`, verificando geração e valor, inclusive atribuição repetida e observação posterior do mapeamento.
5. Implemente `--test-worker` e intercale pedidos e atualizações da worker do alvo sob o mesmo mutex. Execute os mil snapshots e compare as invariantes e as gerações registradas.
6. Aplique o prazo a cada operação, inclusive à aquisição do mutex. Interrompa um peer e provoque bloqueio em testes controlados; acompanhe erro ou timeout, invalidação, encerramento de usuários e liberação dos recursos.
7. Execute dez sessões sucessivas, confira descritores e sockets após cleanup normal e revise os caminhos de falha. Justifique o que um processo do mesmo UID ou um observador malicioso ainda poderia fazer com a capacidade recebida.

### Materiais disponíveis

Consulte a [preparação dos materiais](materials/README.md). O guia distingue os apoios disponíveis das verificações pendentes; obrigações do clube não passam ao participante.

## Casos de teste

- Uma sessão válida executa os três comandos e produz gerações coerentes.
- Token incorreto, comando desconhecido, linha longa, valor fora do intervalo e sequência repetida não alteram estado.
- Mil snapshots intercalados com atualizações preservam a relação entre contador e campo redundante; a revisão identifica exclusão mútua em todos os acessos.
- Interrupção do peer e bloqueio controlado terminam por erro ou timeout, sem espera infinita.
- Dez sessões sucessivas terminam sem crescimento dos descritores pertencentes ao supervisor nem sockets abandonados após cleanup normal.
- O relatório reconhece que testes de coerência complementam a análise de sincronização; não a substituem.
- A revisão dos caminhos de erro confirma o consumo de sequência, a preservação do estado e o encerramento ou invalidação exigidos para cada classe do contrato.
- A justificativa da solução cobre todos os acessos à região, os prazos de aquisição do mutex e a ordem de encerramento dos usuários e de destruição dos recursos compartilhados.
- O modelo de ameaças explicita a capacidade de escrita recebida pelo observador e os limites de UID/token; essa justificativa é obrigatória mesmo quando todos os testes funcionais passam.

Estes casos especificam a verificação exigida. O [guia local](README.md) identifica a cobertura executada, os comandos e as verificações ainda pendentes.

## Extensões opcionais

Depois de cumprir o núcleo, investigue como snapshots imutáveis poderiam alterar a capacidade concedida ao observador e como outra forma de IPC mudaria a transferência de recursos e o encerramento. Uma comparação com conexão de outro UID pode usar o ambiente adicional fornecido pelo clube, sem torná-lo requisito do núcleo.

Essas investigações não substituem a justificativa obrigatória das fronteiras de confiança da solução entregue nem a revisão de exclusão mútua, invariantes, sequência, invalidação e cleanup.

Extensões: pipes, conexão de outro UID e snapshots imutáveis. UID/token não isolam código hostil da mesma identidade. O observador recebe memória gravável e deve cooperar; adulteração direta não é impedida. Conexões: laboratório `019-atomics-lab`, desafio `029-minimal-debugger`, laboratório `022-page-protection-lab`.

## Como participar

Desenvolva a solução em seu próprio repositório. Compartilhe código, ambiente, resultados e justificativa técnica na conversa do clube. Você pode apresentar uma tentativa incompleta; descreva o requisito ainda não atendido e um caso pequeno que permita reproduzir a dúvida.

Organize a memória técnica por contrato, decisões e invariantes, falhas e recursos, verificação, ambiente e limitações. Respeite os limites de páginas quando indicados nos requisitos.

### Referências orientadas

1. [Linux man-pages 6.16 — `unix(7)`](https://git.kernel.org/pub/scm/docs/man-pages/man-pages.git/plain/man/man7/unix.7?h=man-pages-6.16): ler permissões, `SO_PEERCRED` e `SCM_RIGHTS`; distinguir credenciais e declarações do cliente.
2. [Linux man-pages 6.16 — `memfd_create(2)`](https://git.kernel.org/pub/scm/docs/man-pages/man-pages.git/plain/man/man2/memfd_create.2?h=man-pages-6.16): estudar tamanho inicial, descritores e lifetime.
3. [Linux man-pages 6.16 — `pthread_mutexattr_setpshared(3)`](https://git.kernel.org/pub/scm/docs/man-pages/man-pages.git/plain/man/man3/pthread_mutexattr_setpshared.3?h=man-pages-6.16): explicar por que o atributo padrão não atende a processos distintos.
4. [Linux v6.12 — `net/unix/af_unix.c`](https://raw.githubusercontent.com/torvalds/linux/v6.12/net/unix/af_unix.c): código de produção; ler `unix_stream_connect`, associação de peer e credenciais. A revisão adotada é v6.12. Locking interno do kernel não define a sincronização do programa C.

[Linux man-pages 6.16 — `pthread_mutexattr_setrobust(3)`](https://git.kernel.org/pub/scm/docs/man-pages/man-pages.git/plain/man/man3/pthread_mutexattr_setrobust.3?h=man-pages-6.16): distinguir ownership recebido por `EOWNERDEAD`, consistência e invalidação sem recuperação.

As referências usam Linux man-pages 6.16 e as revisões de código identificadas acima. Consulte [origem, licenças e leitura dirigida](references.md), com a conferência de 25/10/2026. A leitura de produção complementa o contrato; não amplia o núcleo.
