# Materiais previstos — Debugger mínimo para execução controlada

**Situação: materiais de preparação disponíveis; validação parcial documentada.** Consulte o [guia operacional](../README.md) para inventário, comandos, falhas intencionais e limitações. A relação curricular abaixo preserva as obrigações do clube; itens sem evidência não são considerados concluídos.

## Arquivos preparados

`arithmetic.S`: trecho ET_EXEC/PIE; `signals.c`: handlers e modos de término; `probe.c`: probe ptrace real. `../starter/oxdbg.c`: controlador incompleto. `../tests/`: consumidor de eventos e verificações. `../Makefile`: receitas sem PT_INTERP.

## O que o clube deve fornecer

Preparar fonte e build fixado: versões ET_EXEC e PIE do trecho aritmético, handler de `SIGUSR1`, `SIGTRAP` ordinário e término por `SIGTERM`. Fornecer predicados de transição, símbolos e instruções de ambiente autorizado. Validar previamente uma máquina com `ptrace` disponível.

## Responsabilidade do participante

Controle um filho didático com ptrace, classifique paradas e preserve sinais e ciclo de vida.

O [enunciado](../index.md) define o que o participante deve construir, investigar e entregar. Os apoios atribuídos ao clube não devem ser transferidos ao participante para compensar um pacote incompleto.

## Condições para disponibilizar o pacote

- Fixe e registre toolchains, dependências, target, flags e capacidades de execução efetivamente validados.
- Documente arquivos, comandos, resultados esperados e falhas intencionais do starter.
- Confira fixtures por um meio independente e mantenha origem e licença identificadas.
- Demonstre que os controles negativos detectam violações relevantes, pelo motivo esperado.
- Preserve as restrições, os casos mínimos e os limites de interpretação do enunciado.
- Registre separadamente aprovado, falhou e não executado.
- A saída de rascunho foi autorizada pelo responsável com dispensa do piloto; isso não substitui a validação das soluções dos participantes.

## Origem e licenças

Especificação curricular: atividade editorial 31 do caderno `Oxide_Club_Desafios_e_Laboratorios_Rust_Seguranca_Terminologia_Revisada_2026-10-25.md`. Redação orientada por `portugues-tecnico-claro.md`, versão 1.1.

Documentação original: CC BY 4.0. Identifique separadamente autoria, origem e licença de cada fonte ou fixture acrescentado. Não distribua soluções completas junto aos materiais iniciais.

O apoio `step-trap.S` executa `int3` durante single-step. O supervisor também testa SIGTRAP/SI_TKILL pendente antes de step. `tests/neutral_seccomp.c` mantém ptrace disponível; `tests/deny_ptrace.c` o nega. `tests/notify_ptrace.c` observa e nega a tentativa no kernel, sem depender da forma usada pelo participante para invocar a syscall. `tests/ptrace_attempt.c` é histórico e não integra a verificação atual. O evento estruturado de indisponibilidade está no enunciado.
