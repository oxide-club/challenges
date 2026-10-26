# Materiais fornecidos e pendentes — Inspetor de recursos de um processo Windows

**Situação: materiais de preparação disponíveis; validação parcial documentada.** Consulte o [guia operacional](../README.md) para inventário, comandos, falhas intencionais e limitações. A relação curricular abaixo preserva as obrigações do clube; itens sem evidência não são considerados concluídos.

## Arquivos preparados

`fixture.cpp`: alvo cooperativo com três fases; `benign.cpp`: DLL; `build.ps1`: build MSVC; `report-template.json`: molde vazio de registro; `errors.md`: catálogo e estados de saída. `../starter/wininspect.cpp`: inspetor incompleto. `../tests/fixtures.py`: inspeção independente prevista para Windows. `../tests/observations.py`: regras puras compartilhadas com o runner nativo; `../tests/report_controls.py` e `fixture_controls.py`: controles sintéticos executáveis no Linux. Execução nativa ainda bloqueada.

## O que o clube deve fornecer

Especificação de VM e toolchain; alvo cooperativo e DLL benigna prontos para uso, com fontes e instruções de build; protocolo documentado das três fases; esquema vazio do relatório e catálogo de erros a exercitar. O alvo e a DLL fornecidos deverão cumprir integralmente os comportamentos do contrato do núcleo, inclusive workers, recursos selecionados, regiões de memória, prontidão, confirmações e encerramento coordenado.

As fixtures devem permitir exercitar o caminho de DLL inexistente e o encerramento antecipado; o catálogo também deve orientar o caso de handle de consulta insuficiente. A disponibilização deverá incluir um roteiro de configuração sem privilégios administrativos e critérios para registrar limitações do ambiente. Não se pressupõe runner Windows ou pipeline já implementado. Produzir substitutos para o alvo e a DLL é extensão opcional, sem transferir ao participante a obrigação de preparar as fixtures do núcleo.

## Responsabilidade do participante

Inspecione um alvo Windows cooperativo em três fases e identifique a origem de cada informação.

O [enunciado](../index.md) define o que o participante deve construir, investigar e entregar. Os apoios atribuídos ao clube não devem ser transferidos ao participante para compensar um pacote incompleto.

## Condições para disponibilizar o pacote

- Fixe e registre toolchains, dependências, target, flags e capacidades de execução efetivamente validados.
- Documente arquivos, comandos, resultados esperados e falhas intencionais do starter.
- Confira fixtures por um meio independente e mantenha origem e licença identificadas.
- Demonstre que os controles negativos detectam violações relevantes, pelo motivo esperado.
- Preserve as restrições, os casos mínimos e os limites de interpretação do enunciado.
- Registre separadamente aprovado, falhou e não executado.
- Mantenha `draft: true` até a revisão e o piloto; os textos não comprovam validação executável.

## Origem e licenças

Especificação curricular: atividade editorial 34 do caderno `Oxide_Club_Desafios_e_Laboratorios_Rust_Seguranca_Terminologia_Revisada_2026-10-25.md`. Redação orientada por `portugues-tecnico-claro.md`, versão 1.1.

Documentação original: CC BY 4.0. Identifique separadamente autoria, origem e licença de cada fonte ou fixture acrescentado. Não distribua soluções completas junto aos materiais iniciais.

### Retificação após a segunda revisão

`python3 tests/report_controls.py`, executado na raiz do desafio, verifica quatro conjuntos conformes, seis classes de erro e 26 relatórios inválidos. A fase final não pode conservar workers ou DLL da fase ativa, mesmo renomeados; intervalos das páginas didáticas só podem aparecer como `MEM_FREE`. Regiões comprometidas sem relação com essas páginas continuam permitidas. Estes controles sintéticos verificam coerência do relatório; a inspeção nativa permanece não verificada sem Windows x64.

### Retificação após a terceira revisão

A comparação de TIDs não distingue continuidade de reúso. A decisão aprovada no enunciado substitui a rejeição automática de um TID repetido por 77/`INCONCLUSIVO` quando o identificador lógico é outro. Os controles agora separam esse caso de um worker explicitamente presente e verificam que a colisão não encobre outros erros. Consulte os comandos e contagens atuais no guia local. A restrição sobre memória descrita na retificação anterior continua sujeita à hipótese de não reúso do intervalo.
