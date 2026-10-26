# Contribuir com desafios

Proponha uma definição, correção ou teste por pull request. Se preferir,
converse primeiro no [Discord](https://discord.gg/cgFWUkgRfX). Não é necessário
concluir um desafio para participar.

## Estrutura e identidade

Combine o próximo número com os mantenedores para evitar colisões entre PRs.
Use um ID como `003-short-name`: número positivo de três dígitos, seguido
de palavras em minúsculas separadas por hífens. Não renumere desafios existentes.
O mesmo ID identifica a definição, a solução e a futura rota no site.

Cada diretório contém:

- `index.md`: definição em Markdown com frontmatter; copie a estrutura de um desafio existente.
- `README.md`: requisitos e comandos para testar um programa do participante.
- `tests/test.py`: executor público que recebe o caminho do programa.
- `materials/`: entradas e resultados quando úteis; preserve bytes e quebras de linha.

As suítes de executáveis aceitas pelo runner usam `tests/cases.json` como fonte comum para os executores
Python e Rust. Registre o ID e o título na macro `roadmap!` de
`tools/oxide-test/src/challenges/mod.rs`: ela incorpora os vetores no binário.
Mantenha IDs de casos estáveis para `--case` e JSON.
Consulte [o formato dos vetores](docs/vectors.md) para acrescentar casos.

Use datas reais e mantenha o `slug` igual ao nome do diretório. Categorias
descrevem atividades (`build`, `investigate`, `debug`, `optimize`, `experiment`)
e são independentes da dificuldade (`beginner`, `intermediate`, `advanced`).
Defina objetivo, escopo, requisitos, verificação e extensões opcionais.

## Metadados para descoberta no site

Use `title` sem o prefixo numérico: `Arena de memória alinhada`, por exemplo.
O número continua no ID e no slug. Declare uma única área principal em `area`,
como `area: memory`, conforme o objetivo principal do exercício. Os IDs, slugs,
nomes e descrições das áreas ficam em `areas.json`; a ordem da lista define sua
apresentação no site. Novas áreas precisam de ID e slug únicos e textos não vazios.
Áreas são agrupamentos por interesse, sem sequência obrigatória de estudo.

Declare `acceptedLanguages` como uma lista não vazia das linguagens permitidas
pelo enunciado (por exemplo, `[C, Rust]`). `recommendedLanguage` é a sugestão
para começar e deve pertencer à lista quando ambos forem declarados. Entradas
antigas sem `acceptedLanguages` continuam usando a linguagem recomendada.

Mantenha todos os assuntos de pesquisa em `topics`. Opcionalmente, use
`cardTopics` para destacar até três conceitos no card sem reduzir o índice de
busca. Use o nível de dificuldade sem qualificadores de calendário.

Marque `featured: true` somente nos exercícios trabalhados no mês atual.
Use `featured: false` nos demais. O campo `participation: flagship` identifica
o principal de cada livestream e não determina o destaque atual.

## Correções e testes

Explique o problema e mostre um caso que falha antes da correção. Mudanças
substantivas na definição devem atualizar `updatedAt` e registrar
esclarecimentos, preservando o ID. Não transforme uma extensão opcional em
exigência silenciosa dos testes.

Execute `make check`. Se modificar um contrato público, execute também a suíte
contra a referência correspondente no checkout local de `solutions`; esse
repositório mantém a revisão de testes adotada em `challenges.lock.json`.

`make check` inclui testes Python e Rust, formatação e clippy; `make build` gera
o executável otimizado. Os testes Rust de integração compilam candidatos C11 e
comparam seus veredictos com os executores Python. Ao alterar um caso durante a
migração, mantenha ambas as suítes consistentes. As entradas aleatórias de RLE
usam geradores distintos, determinísticos, cobrindo os mesmos tamanhos.

`make check-packages`, incluído em `make check` e na CI, executa a preparação e as falhas específicas dos starters em cópias temporárias. Consulte `build/package-checks/results.json`: `not_verified` indica ambiente indisponível, não aprovação. A avaliação completa da solução e dos mutantes continua separada da preparação do participante.

Nesta rodada de correções, o responsável autorizou referências e sondas em armazenamento privado persistente fora deste repositório, substituindo a dependência volátil de `/tmp`. Essa exceção não autoriza publicá-las nem alterar `solutions/`. Registre origem, hashes, comandos e revisão dos testes; mantenha fontes privadas fora de relatórios e arquivos distribuídos. A política e os limites dessa preservação estão no registro de resposta de 25/10/2026.

Os testes são executados em programas reais. Use limites de tempo, entradas
reproduzíveis e mensagens úteis. Não adicione dependências sem necessidade.
O validador local cobre IDs; a validação completa dos metadados Astro continua
no repositório do site.

## Autoria e permissões

Ao contribuir, confirme que possui os direitos necessários para disponibilizar
os materiais nos termos da [política de licenciamento](LICENSE.md):

- Enunciados, explicações e textos educacionais: CC BY 4.0.
- Fixtures, dados de entrada e saídas esperadas: CC0 1.0.
- Scripts de teste, validadores, geradores e demais códigos executáveis: MIT.

Informe a atribuição desejada e preserve os créditos e avisos existentes.
Não se exige cessão de direitos. Identifique materiais de terceiros, suas
fontes e licenças; eles não recebem automaticamente as licenças do repositório.
Registre explicitamente qualquer exceção junto ao material afetado.

Soluções dos participantes ficam em seus próprios repositórios. Para indicar
uma solução, adicione a entrada em `<id>/community.yaml` no repositório
`solutions`, por pull request. O contrato está em `community.schema.json`
desse repositório. Não inclua credenciais,
conversas privadas ou material sem permissão.

## Recursos do desafio no GitHub

Declare os recursos disponíveis no frontmatter de `<id>/index.md`, junto aos
outros metadados do desafio. Por exemplo, `001-wc/index.md` contém:

```yaml
github:
  challenge: true
  solutions: [c]
  community: true
```

- `challenge`: habilita o link para o diretório deste desafio em `challenges`.
- `solutions`: lista apenas os identificadores de linguagens com implementações
  publicadas em `solutions/<id>/<linguagem>`. Não presuma que a linguagem
  recomendada é a única disponível, nem que existe uma implementação em C.
- `community`: habilita o link para o índice de implementações externas deste
  desafio em `solutions/<id>/community.yaml`.

Verifique os destinos publicados antes de habilitar qualquer recurso. Campos
omitidos equivalem a `false` ou a uma lista vazia; omita `github` quando não
houver recursos a apresentar. Não armazene URLs completas nem outro identificador
nesses metadados: o site deriva os caminhos do ID canônico e centraliza a
organização, os repositórios e suas branches.

Para uma nova implementação, adicione a linguagem à lista somente depois da
publicação do diretório correspondente. Se a linguagem ainda não estiver
registrada, adicione seu identificador e nome de exibição ao registro
`languageLabels` em `src/lib/challenge-resources.mjs` no site. A validação completa
continua no schema Astro; linguagens desconhecidas ou repetidas são rejeitadas.

O site busca estes metadados com a definição no build. Ao migrar configurações
antes mantidas no site, publique primeiro a alteração neste repositório e depois
atualize o site, evitando um intervalo sem os links de recursos.

## Origem das definições iniciais

As definições `001-wc` e `002-ppm` foram fornecidas pelo responsável pelo
Oxide Club e copiadas do repositório do site, alterando apenas seus slugs para
os IDs padronizados. O registro de origem do site informa que, em 19 de outubro
de 2026, o responsável declarou que os textos e o logo fornecidos para o
lançamento foram gerados por LLM e autorizou sua publicação, sem identificar
o fornecedor/modelo ou seus termos. Esse registro não certifica origem
individual de textos posteriores, exclusividade ou titularidade.

## Notificações no Discord

PRs prontos para revisão que adicionam `<id>/index.md` são divulgados em
`#contribuicoes`, com título e link apontando para o PR. Drafts aguardam
a passagem para pronto; atualizações e reaberturas não repetem um aviso
já confirmado. Edições, anexos isolados e renomeações não são novas propostas.

Depois do merge e da publicação bem-sucedida pelo site, páginas publicadas
pela primeira vez aparecem em `#novidades`, com link de `oxideclub.dev`.
Conteúdo com `draft: true` aguarda publicação.

Mantenedores devem configurar `DISCORD_CONTRIBUTIONS_WEBHOOK_URL` como Actions
Secret deste repositório antes de habilitar o workflow de contribuições.
O registro permanente fica em `state.json` na branch `discord-state`.
Veja a [configuração e recuperação das notificações](https://github.com/oxide-club/oxideclub.dev/blob/main/docs/DISCORD-NOTIFICATIONS.md).
Para executar os testes sem enviar mensagens: `node --test tools/tests/discord-*.test.mjs`
com Node.js 24. Mantenha os módulos de `scripts/discord/` sincronizados com os
correspondentes no repositório do site.

## Cobertura por mecanismo

Registre toda definição em `docs/verification-policy.json`. Siga a [política de cobertura](docs/verification-policy.md). Bibliotecas usam testes de API e compilação; sessões usam seus supervisores. Não crie uma CLI artificial nem vetores vazios. Um rascunho só pode ficar sem verificador com motivo explícito no modo `preparing`. Esse estado não representa validação.
