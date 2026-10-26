# Recibos de validação e decisão editorial

Em 25/10/2026, o responsável autorizou `draft: false` para os oito pacotes tecnicamente validados e dispensou explicitamente o piloto. A decisão mantém `026-no-std` em rascunho pela proveniência/licença do psABI e `030-windows-inspector` pela ausência de validação nativa Windows x64.

Os recibos registram `pilot: waived_by_owner`, nunca `pilot: approved`. Referência e controles remetem à validação técnica anterior, confirmada no resultado da revisão independente 6 informado pelo responsável. Nesta alteração, a preparação local foi repetida após formatar o código; não houve nova execução integral das referências privadas, Miri, Windows ou CI remota.

Cada recibo identifica exatamente os arquivos atuais do pacote por SHA-256. A política confere o hash do próprio recibo e o inventário público. Os hashes detectam mudanças posteriores; não autenticam por si sós uma aprovação. Consulte a [política](../verification-policy.md).

Estes arquivos são metadados necessários à verificação da saída de rascunho. Não contêm soluções, mutantes, logs privados nem recriam os diretórios de evidências e revisões removidos. A mudança de draft não executa publicação, push ou deploy.
