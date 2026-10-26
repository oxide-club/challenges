# Catálogo de erros e estados de execução

Este catálogo define os casos a exercitar. A execução WinAPI permanece pendente. Um registro de erro usa `category: "error"`, `origin: "inspector"` e `attributes` com `kind`, `api`, `error`. A origem identifica quem classifica a falha; não transforma dados cooperativos em consultas externas.

| `kind` | Caso controlado | `api` e `error` | Evidência exigida |
| --- | --- | --- | --- |
| `permission-denied` | Consultar a região com handle aberto somente com `PROCESS_QUERY_LIMITED_INFORMATION`. | Nome da API que falhou; `error: 5` (`ERROR_ACCESS_DENIED`). | Retorno de falha e `GetLastError` capturado imediatamente. Não solicitar mais privilégios automaticamente. |
| `target-exited` | Modo `early`, após ACK 0. | `null`, `null` quando o término é observado sem falha de API. | Status 23 do alvo e fase alcançada; `exit_status` pode registrar 23. |
| `incompatible-environment` | Binário/ambiente fora de Windows x64. | `null`, `null` na detecção prévia; se uma API falhar, nome e código reais. | Arquitetura/ambiente observado e ausência de validação nativa. |
| `snapshot-failed` | Falha persistente de snapshot, incluindo `ERROR_BAD_LENGTH`. | `CreateToolhelp32Snapshot` e código efetivo, por exemplo 24. | No máximo dez tentativas e prazo total de dois segundos; não inventar código se nenhuma API foi chamada. |
| `dll-missing` | Caminho absoluto inexistente para a DLL. | `LoadLibraryW` e código efetivo não zero, sem fixar um código universal. | Mensagem stderr do alvo e status 1. |
| `protocol-failed` | ACK inválido, atrasado ou pipe rompido. | `null`, `null` para validação local; API/código reais para falha WinAPI. | Mensagem rejeitada ou prazo esgotado, sem tratar ausência de dados como sucesso. |

`api` e `error` são ambos `null` se não houve falha de API. Não chame `GetLastError` para fabricar informação após sucesso ou após mero término de processo. Um log de erro pode terminar antes da fase 2; ele não substitui os três relatórios da execução normal.

Exemplo sintético, não observado em Windows:

```json
{"session":"example-session","architecture":"x64","phase":1,"category":"error","origin":"inspector","id":"query-limited","attributes":{"kind":"permission-denied","api":"VirtualQueryEx","error":5}}
```

Valide um log de erros com `python tests/check.py --error-report build/errors.jsonl`. O validador verifica estrutura e coerência, não confirma que a falha ocorreu.

## Status do alvo e das ferramentas

| Programa/status | Significado |
| --- | --- |
| `fixture.exe`: 0 | Três fases concluídas e ACK 2 recebido. |
| `fixture.exe`: 1 | Falha de API, protocolo ou liberação; consultar stderr. |
| `fixture.exe`: 2 | Argumentos inválidos: quantidade, sessão ou caminho da DLL; consultar stderr. |
| `fixture.exe`: 23 | Término antecipado intencional do modo `early`, após ACK 0. |
| `fixture.exe`: 77 | Build executado fora da arquitetura x64 suportada. |
| `wininspect.exe` starter: 1 | Implementação pendente. Não é referência funcional. |
| `check.py`: 0 | Somente a operação solicitada passou: estrutura de relatórios ou preparação disponível. Não significa validação integral do inspetor. |
| `check.py`: 1 | Falha de formato, controle ou build. |
| `check.py --prepare`: 77 | Controles independentes passaram, mas Windows não está disponível; `NOT_RUN` para build/execução nativos. |
| `fixtures.py`: 77 | `NOT_RUN` se Windows não está disponível; `INCONCLUSIVO` se a consulta final contém TID didático sem identidade que distinga reúso. |
| `check.py --report`: 77 | `INCONCLUSIVO`: outro identificador lógico reutiliza um TID didático; não é aprovação nem falha comprovada da solução. |

Ainda devem ser executados em Windows: cinco repetições dos três modos, erros de ACK/pipe, limites de espera, inspeção de layouts ctypes e encerramento sem processos pendentes. Não há referência privada do inspetor nem mutantes nativos aprovados.
