# Materiais previstos — Tracing por interposição de funções

**Situação: materiais de preparação disponíveis; validação parcial documentada.** Consulte o [guia operacional](../README.md) para inventário, comandos, falhas intencionais e limitações. A relação curricular abaixo preserva as obrigações do clube; itens sem evidência não são considerados concluídos.

## Arquivos preparados

`calc.h`: API e callback de sink. `cases.json`: seis vetores independentes. `../starter/`: três componentes incompletos. `../tests/`: cliente concorrente, consumidor JSON, substituto opaco e falha de resolução. `../Makefile`: builds dinâmico e direto.

## O que o clube deve fornecer

O clube deverá fornecer contrato da API, tabela de casos, receita de build sem otimizações que eliminem a chamada observada e protocolo dos sinks de teste. Também deverá disponibilizar uma receita explícita para a variante com chamada direta e um consumidor que valide o JSON. A aplicação e as bibliotecas são construídas pelos alunos; a ficha não promete scaffolding já pronto.

O ambiente deve usar aplicação comum, sem privilégios especiais. As restrições do loader em secure-execution mode são assunto de leitura, não algo a contornar.

## Responsabilidade do participante

Implemente interposição de uma função própria preservando retorno, saída e errno.

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

Especificação curricular: atividade editorial 30 do caderno `Oxide_Club_Desafios_e_Laboratorios_Rust_Seguranca_Terminologia_Revisada_2026-10-25.md`. Redação orientada por `portugues-tecnico-claro.md`, versão 1.1.

Documentação original: CC BY 4.0. Identifique separadamente autoria, origem e licença de cada fonte ou fixture acrescentado. Não distribua soluções completas junto aos materiais iniciais.
