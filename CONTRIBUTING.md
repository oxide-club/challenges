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

Contribuições de código destinadas à incorporação devem usar MIT. Ao enviar
texto, confirme que pode autorizar sua publicação pelo Oxide Club e informe
a atribuição desejada. Registre separadamente eventual licença de reutilização;
não se exige cessão de direitos. Veja [LICENSING.md](LICENSING.md).

Soluções dos participantes ficam em seus próprios repositórios e podem ser
indicadas no `COMMUNITY.md` do repositório `solutions`. Não inclua credenciais,
conversas privadas ou material sem permissão.

Quando houver uma implementação comentada publicada pelo clube, inclua
`referenceUrl` apontando para seu diretório em `solutions/<id>/<linguagem>`.
O site usa esse campo opcional para oferecer um link de estudo ao final da
página. Omita o campo enquanto não existir uma implementação publicada.
