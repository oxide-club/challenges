# Política de cobertura das verificações

Cada definição tem exatamente um registro em `verification-policy.json`, mesmo quando `draft: true`.

- `embedded`: suíte real e não vazia em `oxide-test`, com IDs iguais aos vetores Python.
- `package`: verificador próprio existente, indicado por `check`, e guia operacional. Use para APIs, compilação, FFI e sessões. Esse registro identifica o mecanismo; não declara aprovação.
- `preparing`: somente rascunho explícito, com `reason` não vazio e guia existente. Não há aprovação funcional nem suíte fictícia.

`make check` confere identidade, cobertura total, correspondência do catálogo embutido e executa `make check-packages`. Cada pacote é copiado para um diretório temporário, sem builds/cache. O verificador roda com `--prepare`; em seguida, comandos separados verificam as falhas específicas do starter. Status 1 por erro de sintaxe, por exemplo, não substitui o diagnóstico previsto de núcleo incompleto.

`tools/package_worker.py` registra os processos e funções realmente executados na preparação. O supervisor exige as etapas adequadas ao mecanismo, além dos status e diagnósticos: Cargo para bibliotecas, compiladores e clientes para FFI/no_std, gerador/validador para PE e builds/sondas para sessões. Um verificador vazio ou que apenas imprime uma mensagem de aprovação é rejeitado. Essa instrumentação detecta regressões e verificadores sem trabalho; não é isolamento contra um programa deliberadamente hostil que tente forjar o supervisor.

Status 77 exige evidência independente: host não Windows para 030 ou executável necessário ausente no PATH para os demais preparos. O resultado fica `not_verified`, nunca `passed`. A integração pode terminar com 0 mesmo com plataforma não verificada, pois comprova que o bloqueio foi registrado corretamente; isso não valida o pacote. Consulte `build/package-checks/results.json` e os logs por etapa. A CI executa o mesmo `make check` e preserva esses registros como artefato. A execução remota da CI deve ser conferida separadamente; um teste local não a substitui.

O modo `package` com `draft: false` exige `validation: {path, sha256}` na política. O JSON identificado deve declarar `package`, `status: validated`, `reference: passed`, `mutants: rejected`, `pilot: approved` (ou a dispensa explícita descrita abaixo), `editorial: approved` e `public_sha256` com inventário exato de todos os arquivos do pacote (exceto builds/cache). Esses dados precisam corresponder a evidências reais revisadas pelo mantenedor; o hash detecta mudança posterior, não autentica uma aprovação inventada. Em 25/10/2026, o responsável autorizou a saída de rascunho de oito pacotes tecnicamente validados, dispensando o piloto. `026-no-std` e `030-windows-inspector` continuam em rascunho.

A dispensa usa `pilot: waived_by_owner` e `pilot_waiver: {approved_by: "responsavel", date, reason, request}`. A data deve ser ISO válida; motivo e identificação da solicitação devem ser não vazios. Esse registro declara uma decisão do responsável, não a execução de um piloto. A dispensa não elimina referência, controles, aprovação editorial ou inventário exato dos materiais. Os recibos desta decisão ficam em `docs/validation/`; seus hashes continuam sendo conferidos pela política. A autorização de saída de rascunho não executa deploy, push ou publicação externa.

Os testes negativos rejeitam definição omitida, publicação sem evidência completa, hashes divergentes, modo desconhecido, motivo vazio, verificador ausente/vazio, mensagens de aprovação sem execução, falha arbitrária do starter e status 77 sem indisponibilidade comprovada.

O teste Rust `catalog_and_embedded_vectors_cover_every_definition` continua cobrindo todas as definições. Ele exige a partição explícita e conserva as comparações de casos de cada suíte embutida. `oxide-test list` lista somente suítes executáveis embutidas; não promete avaliar bibliotecas ou sessões. Consulte o README de cada pacote para executar seu verificador.

Aprovação de preparação, falha esperada do starter, falha funcional, ambiente indisponível e verificação não executada são resultados distintos. Evidências de referência e controles acompanham cada pacote. Preparação isolada não autoriza publicação; a decisão editorial e o piloto aprovado ou explicitamente dispensado são registrados separadamente.
