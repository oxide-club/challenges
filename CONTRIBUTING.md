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
- `fixtures/`: entradas e resultados quando úteis; preserve bytes e quebras de linha.

Use datas reais e mantenha o `slug` igual ao nome do diretório. Categorias
descrevem atividades (`build`, `investigate`, `debug`, `optimize`, `experiment`)
e são independentes da dificuldade (`beginner`, `intermediate`, `advanced`).
Defina objetivo, escopo, requisitos, verificação e extensões opcionais.

## Correções e testes

Explique o problema e mostre um caso que falha antes da correção. Mudanças
substantivas na definição devem atualizar `updatedAt` e registrar
esclarecimentos, preservando o ID. Não transforme uma extensão opcional em
exigência silenciosa dos testes.

Execute `make check`. Se modificar um contrato público, execute também a suíte
contra a referência correspondente no checkout local de `solutions`; esse
repositório mantém a revisão de testes adotada em `challenges.lock.json`.

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

Soluções dos participantes ficam em seus próprios repositórios e podem ser
indicadas no `COMMUNITY.md` do repositório `solutions`. Não inclua credenciais,
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
- `community`: habilita o link para a seção deste desafio no índice existente
  `solutions/COMMUNITY.md#<id>`.

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
