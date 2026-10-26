# Materiais previstos — IPC e snapshots consistentes entre processos

**Situação: materiais de preparação disponíveis; validação parcial documentada.** Consulte o [guia operacional](../README.md) para inventário, comandos, falhas intencionais e limitações. A relação curricular abaixo preserva as obrigações do clube; itens sem evidência não são considerados concluídos.

## Arquivos preparados

`region.h`: ABI da região; `region_probe.c`: layout e acessos controlados sob mutex. `../starter/`: target/observer incompletos. `../tests/peer.py`: cliente adversarial; `../tests/observer.py`: servidor malformado independente; `../Makefile`: build.

## O que o clube deve fornecer

Fixtures do protocolo e região, registros sem segredos, VM/libc e roteiro de interrupção/cleanup. Usuário adicional poderá apoiar a extensão de permissões; não é requisito do núcleo.

## Responsabilidade do participante

Construa um protocolo local autenticado com memória compartilhada, mutex e snapshots consistentes.

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

Especificação curricular: atividade editorial 36 do caderno `Oxide_Club_Desafios_e_Laboratorios_Rust_Seguranca_Terminologia_Revisada_2026-10-25.md`. Redação orientada por `portugues-tecnico-claro.md`, versão 1.1.

Documentação original: CC BY 4.0. Identifique separadamente autoria, origem e licença de cada fonte ou fixture acrescentado. Não distribua soluções completas junto aos materiais iniciais.

### Isolamento do controle de tamanho

Em `tests/observer.py`, `wrong-size` entrega um descritor com mutex inicializado e versão 1 válida, mas extensão de `sizeof(ox_region) + 8`. A conexão permanece aberta. Assim, um observador que ignora `fstat` não pode ser rejeitado incidentalmente por versão ou mutex inválido. O controle `wrong-version` conserva tamanho e mutex válidos e altera somente a versão.
