# 030-windows-inspector — guia local

**Bloqueio de ambiente registrado:** build e execução Windows não foram realizados. O responsável optou por registrar essa limitação nesta etapa. O host disponível é Linux x86-64, sem runtime Windows nem compilador MinGW identificado. Fontes não equivalem a fixtures nativas validadas; `draft: true` permanece.

## Ambiente solicitado e build

VM Windows 11 x64, conta comum, Visual Studio 2022 Build Tools com C++ x64 e Windows SDK; Python x64. A revisão exata de MSVC/SDK e do Windows deverá ser registrada na primeira execução. Essas versões ainda não foram validadas nem fixadas por resultado local.

O clube deve disponibilizar uma VM com Build Tools e SDK previamente instalados e uma conta comum para compilar e executar o exercício. A instalação inicial do Visual Studio exige administração por padrão; não se promete instalar essa toolchain sem privilégios. Se a VM não estiver preparada, registre bloqueio de ambiente e solicite a imagem ao responsável. Consulte a [documentação de instalação](https://learn.microsoft.com/en-us/visualstudio/install/install-visual-studio?view=visualstudio).

No terminal x64 Native Tools, sem elevação, abra PowerShell e execute neste diretório:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File materials/build.ps1
python tests/fixtures.py --output build/fixture-evidence.json
python tests/check.py --prepare
```

`-ExecutionPolicy Bypass` afeta somente o processo PowerShell iniciado; não altera a política permanente. Políticas de grupo têm precedência: se bloquearem a execução, registre o bloqueio e use a VM preparada pelo clube. Consulte a [documentação de execution policies](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_execution_policies?view=powershell-5.1). Esse roteiro ainda não foi executado no ambiente nativo.

O script cria `fixture.exe`, `benign.dll` e o starter `wininspect.exe`, usando C++17, `/W4 /EHsc /MD`. O starter retorna 1 intencionalmente. Complete somente o inspetor; o alvo e a DLL são apoios do clube, não tarefas transferidas ao participante.

## Protocolo do alvo

Inicie `fixture.exe SESSION ABSOLUTE_DLL [early]` com stdin/stdout redirecionados por pipes herdados. `SESSION` contém 1–64 caracteres `[a-z0-9-]`; gere uma sessão nova. A DLL exige caminho absoluto. O modo `early` termina com status 23 após a confirmação inicial; caminho inexistente exercita `LoadLibraryW`.

stdout: uma linha JSON UTF-8 por fase. Campos: `session`, `architecture` (`x64`), `pid`, `phase` (0, 1, 2), `ready:true`, `tids`, `module`, `handles`, `region`. Endereços são inteiros sem sinal da execução. stdin: `ACK 0\n`, `ACK 1\n`, `ACK 2\n`, somente após coletar a respectiva fase. Prazo monotônico de cinco segundos para cada confirmação; mensagens inválidas encerram com 1. Limite cada espera do inspetor também a cinco segundos.

Na fase 0, inventários didáticos vazios. Na fase 1, dois TIDs, caminho da DLL, handles lógicos `event-stop`, `event-spare`, `file-temp` com ação `create` (o registro `file-temp` inclui `path` absoluto), região com `base`, `size` e `page_size`. As três páginas são reservada, comprometida RW e comprometida RO, nessa ordem. Na fase 2, workers encerrados, DLL descarregada, região liberada e ações `close` dos três handles. O arquivo temporário é removido ao fechar. O alvo mantém o evento de parada até aguardar os workers.

Erros de API saem em stderr como `{ "api": "...", "error": N }`, com `GetLastError` capturado antes de outras chamadas. A ausência de um dado não deve ser apresentada como sucesso de enumeração. Falha persistente de snapshot, permissão negada, alvo encerrado e arquitetura incompatível são classes distintas no relatório do inspetor.

## Relatório e verificação

`materials/report-template.json` é um molde vazio de registro, não um relatório válido nem um JSON Schema. Entregue `phase-0.jsonl`, `phase-1.jsonl` e `phase-2.jsonl`: cada arquivo contém somente registros da respectiva fase e pelo menos um registro. Cada linha possui `session`, `architecture: "x64"`, `phase`, `category`, `origin`, `id`, `attributes`. A sessão deve ser a mesma nos três arquivos; IDs e atributos pertencem à execução observada.

| Categoria | Origem | Atributos mínimos |
| --- | --- | --- |
| `thread` | `external` | `tid`, inteiro positivo observado; sem TIDs duplicados na mesma fase. |
| `module` | `external` | `path`, caminho absoluto observado. |
| `memory` | `external` | `BaseAddress`, `RegionSize`, `State`; em regiões reservadas, também `Type`; em regiões comprometidas, também `Protect` e `Type`, retornados pela consulta. |
| `handle` | `cooperative` | `action: "create"` na fase 1 e `"close"` na fase 2. |
| `error` | `inspector` | `kind`, `api`, `error`, segundo o [catálogo](materials/errors.md). |

IDs didáticos: `worker-0`, `worker-1`, `benign-dll`, `page-0` a `page-2`, `event-stop`, `event-spare`, `file-temp`. Os três handles precisam de um registro de criação e um de fechamento; não são recriados na fase final. Não se fixa uma contagem global de threads ou módulos. Para `MEM_FREE`, `Protect` e `Type` não são usados como evidência de liberação; o estado da região é a propriedade relevante. Em `MEM_RESERVE`, `Protect` é indefinido. Consulte [MEMORY_BASIC_INFORMATION](https://github.com/MicrosoftDocs/sdk-api/blob/656e9656bfaef34dd29cd7ee9e1146aec17e924c/sdk-api-src/content/winnt/ns-winnt-memory_basic_information.md).

```powershell
python tests/check.py --report build/phase-0.jsonl build/phase-1.jsonl build/phase-2.jsonl
python tests/check.py --error-report build/errors.jsonl
```

Esse consumidor verifica formato e propriedades básicas; não comprova consultas WinAPI nem a procedência dos dados. `tests/fixtures.py` foi escrito para conferir o alvo independentemente via Toolhelp e VirtualQueryEx, comparar TIDs/DLL/páginas e exercitar DLL ausente, término antecipado e direitos insuficientes. Ainda não foi executado em Windows. O verificador compara PID e sessão com o processo iniciado; após a fase final, consulta novamente as três páginas para exigir `MEM_FREE` e verifica a remoção do caminho temporário publicado. O inspetor deve limitar ERROR_BAD_LENGTH a dez tentativas e dois segundos, usar `PROCESS_QUERY_INFORMATION` para VirtualQueryEx e não solicitar PROCESS_ALL_ACCESS.

## Origem, referências e licenças

C++, Python e PowerShell originais preparados com assistência de IA: MIT. Dados: CC0 1.0; texto: CC BY 4.0. A DLL apenas exporta uma função de versão e não cria recursos no loader lock.

Foram consultadas em 25/10/2026 [VirtualQueryEx](https://github.com/MicrosoftDocs/sdk-api/blob/656e9656bfaef34dd29cd7ee9e1146aec17e924c/sdk-api-src/content/memoryapi/nf-memoryapi-virtualqueryex.md), revisão exibida 24/05/2022, [CreateToolhelp32Snapshot](https://github.com/MicrosoftDocs/sdk-api/blob/656e9656bfaef34dd29cd7ee9e1146aec17e924c/sdk-api-src/content/tlhelp32/nf-tlhelp32-createtoolhelp32snapshot.md) e [o exemplo de snapshots](https://github.com/MicrosoftDocs/win32/blob/ca8274decead49403d70ceeed4af8d4ca74eaf11/desktop-src/ToolHelp/taking-a-snapshot-and-viewing-processes.md). São fontes externas vinculadas, não redistribuídas nem relicenciadas. Pergunta de leitura: quais direitos o exemplo pede que este inspetor não precisa? As quatro referências do enunciado foram fixadas em commits dos repositórios oficiais MicrosoftDocs. URLs originais, revisões e hashes estão na proveniência (registro histórico retirado deste repositório). A fixação documental não substitui validação WinAPI.

## Limites desta entrega

Não há referência privada Windows aprovada, resultados nativos, mutantes nativos ou piloto. A verificação de fontes/JSON em Linux não substitui esses resultados. Estimativa curricular provisória: 12–18 horas; recalibrar no piloto.

## Retificação de 25/10/2026

A revisão anterior demonstrou que relatórios sem fechamento, sem TID, com categoria desconhecida e recriação de handle passavam. Os controles atuais rejeitam esses casos. `tests/report_controls.py` testa o consumidor com dados sintéticos; `tests/fixture_controls.py` testa regras de comparação com doubles de observações independentes. Nenhum dos dois chama WinAPI. `--prepare` executa ambos inclusive no Linux e então retorna 77 com `NOT_RUN` para o build e a execução nativos.

A resposta à revisão (registro histórico retirado deste repositório) preserva resultados anteriores, comandos, hashes e limites. O usuário confirmou manter o bloqueio Windows nesta etapa. Sem build, alvo/DLL executados, referência do inspetor, mutantes nativos, sessões repetidas e piloto, este pacote não está validado para publicação.

Propostas terminológicas locais (PTC 5.6): `cleanup` significa liberar recursos e encerrar/recolher atividades sob responsabilidade do programa; propõe-se “liberação e encerramento de recursos”. `ownership`, neste pacote WinAPI, designa a responsabilidade por possuir e fechar cada handle; propõe-se “responsabilidade pelo recurso”. Estado: propostas, sem alteração do glossário canônico e sem substituição automática de identificadores ou conceitos de Rust.

## Reúso de TID e resultado inconclusivo

O relatório registra TID, sem horário de criação ou outro discriminante de identidade. A hipótese de não reúso permite confrontar a ausência dos workers entre fases. Se um TID didático reaparece na fase final com outro identificador lógico, `tests/check.py --report ...` retorna 77/`INCONCLUSIVO`: pode ser uma thread nova ou um worker indevidamente renomeado. Não se considera a execução aprovada. Um registro ainda identificado como worker é falha (1), e a colisão não encobre incoerências nos demais registros.

`tests/fixtures.py` usa a mesma distinção para a consulta externa final, depois de verificar as outras propriedades da fase. A fixture continua obrigada a encerrar e aguardar os workers. Uma colisão é registrada sem interromper o protocolo: o verificador envia `ACK 2`, verifica o término e executa os modos `missing-dll` e `early`. Somente depois, se nenhuma outra verificação falhar, retorna 77/`INCONCLUSIVO`. Falhas de confirmação, status final ou dos outros modos continuam retornando 1. Registre o caso e repita a observação em Windows para investigar a identidade, sem presumir falha apenas pelo TID. A observação real de reúso de TID e de endereço integra as pendências nativas. O controle atual de intervalos de memória ainda pressupõe ausência de uma nova alocação sobre o intervalo liberado (N3-031-02, melhoria opcional não corrigida nesta rodada).

Na raiz do pacote, `python3 tests/report_controls.py` verifica quatro conjuntos conformes, duas colisões inconclusivas e 27 controles negativos, além das seis classes de erro. `python3 tests/fixture_controls.py` verifica três conjuntos conformes, uma colisão inconclusiva e 20 controles negativos. São dados sintéticos; nenhuma execução WinAPI é declarada.

Os controles de `fixture_controls.py` também executam dez combinações de protocolo com um executor double: sem/com colisão, combinadas com sucesso ou falha no ACK 2, término, DLL ausente e modo early. O laço testado é o usado pelo verificador nativo; estes controles não executam WinAPI.

`python3 tests/native_controls.py` executa 12 cenários chamando `verify()` e seu `execute` nativo, com doubles de kernel32, Popen e existência do arquivo temporário. Os testes não substituem a sequência de ACKs nem as regras de observação; verificam o término, kill/wait e fechamento dos handles em cada cenário. `fixture_controls.py` e `--prepare` também executam esses controles. Isso testa o fluxo Python, sem alegar execução WinAPI ou processos Windows.
