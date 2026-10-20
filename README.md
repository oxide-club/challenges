# Desafios do Oxide Club

Definições e testes públicos dos desafios do [Oxide Club](https://oxideclub.dev).
Nosso método é **Explorar → Experimentar → Explicar**: desenvolver uma solução,
investigar seu comportamento e compartilhar o que você aprendeu.

## Estrutura

Cada desafio tem um identificador estável no formato `NNN-name`, usado também
no site e no repositório de soluções.

```text
NNN-name/
  index.md       # Definição do desafio
  README.md      # Ambiente, comandos e orientações de teste
  tests/         # Testes públicos
  fixtures/      # Entradas e saídas de teste, quando necessárias
```

O `index.md` é a especificação canônica. O README do desafio explica como
executar os testes e quais requisitos precisam de revisão do código.

## Índice de desafios

| ID        | Desafio                                 | Guia de testes            |
| --------- | --------------------------------------- | ------------------------- |
| `001-wc`  | [Construa seu wc](001-wc/index.md)      | [Guia](001-wc/README.md)  |
| `002-ppm` | [Gere uma imagem PPM](002-ppm/index.md) | [Guia](002-ppm/README.md) |
| `003-rle` | [Construa um compressor RLE](003-rle/index.md) | [Guia](003-rle/README.md) |

## Como participar

1. Escolha um desafio e leia sua definição.
2. Desenvolva sua implementação em seu próprio repositório.
3. Execute os testes e investigue os resultados.
4. Compartilhe descobertas e dúvidas no tópico do Discord indicado no desafio.

Não é necessário concluir o desafio para participar. Experimentos e soluções
parciais também são bem-vindos. Para compartilhar seu repositório, envie um PR
para o [índice da comunidade](https://github.com/oxide-club/solutions/blob/main/COMMUNITY.md).
As referências comentadas do clube ficam em [solutions](https://github.com/oxide-club/solutions).

## Como testar seu programa

O `oxide-test` é um executor independente para Linux. Recebe o caminho do seu
programa compilado e executa os testes públicos do desafio. As suítes e fixtures
ficam incorporadas no executável: após compilá-lo, você não precisa de Python
nem de um checkout deste repositório para usá-lo.

**Primeira execução?** Siga o [guia de instalação e uso](docs/runner.md):
[Linux](docs/runner.md#linux), [Windows com WSL-2](docs/runner.md#windows-com-wsl-2-recomendado)
ou [Docker](docs/runner.md#docker). No Windows, compile e execute seu programa no
ambiente Linux escolhido; o runner não tem uma versão nativa para Windows.

Para compilar, use Rust estável e Cargo na raiz deste repositório:

```sh
cargo build --release --locked
./target/release/oxide-test list
./target/release/oxide-test run 001-wc /caminho/para/seu-programa
```

O executável fica em `target/release/oxide-test`. Você pode copiá-lo para um
diretório do seu `PATH`. Ele precisa ser compatível com a arquitetura e o runtime
Linux da máquina; as mesmas condições se aplicam ao programa submetido.

Depois de instalar o executável:

```sh
oxide-test list 001-wc
oxide-test run 001-wc ./meu-wc --case sem-quebra
oxide-test run 003-rle ./meu-rle --fail-fast --timeout 10
oxide-test run 002-ppm ./meu-ppm --json
```

Use `--case ID` mais de uma vez para selecionar vários casos. Sem esse filtro,
todos os casos são executados. O limite padrão é de cinco segundos por invocação
do programa. Falhas mostram a categoria, uma comparação limitada dos bytes e um
comando para repetir o caso. Em PPM, diferenças nos pixels incluem coordenadas.

| Status de saída | Significado |
| --- | --- |
| `0` | Todos os casos selecionados passaram |
| `1` | Pelo menos um caso falhou |
| `2` | Erro de uso, preparação ou execução do próprio teste |
| `3` | Execução incompleta, com casos ignorados |

Um filtro de casos não representa a suíte completa. O resumo informa os totais
disponível, selecionado e executado; “Passed all public tests” aparece somente
quando toda a suíte passou sem ignorar casos. Os testes verificam comportamento;
linguagem, bibliotecas permitidas e processamento incremental exigem revisão do
código. O executor limita tempo e saídas capturadas, mas não isola o programa do
sistema: execute submissões locais com os mesmos cuidados de qualquer executável.

O JSON usa `schema_version: 1`, com versão do runner, revisão dos testes,
resultados por caso, durações e resumo. Consulte [o guia do runner](docs/runner.md)
para a API Rust, categorias de falha e detalhes do formato.

### Compatibilidade com os executores Python

Os comandos anteriores continuam disponíveis com Python 3.10 ou superior em
Unix/Linux. Na raiz deste repositório:

```sh
python3 ID_DO_DESAFIO/tests/test.py /caminho/para/seu-programa
```

Esses executores usam apenas a biblioteca padrão do Python. Em ambas as opções,
o programa deve estar compilado e ter permissão de execução. Consulte o README
do desafio para os comandos de compilação e os casos cobertos.

## Como contribuir

Proponha novos desafios, esclarecimentos ou testes por pull request.
Combine o próximo número com os mantenedores e preserve os IDs já publicados.
Execute `make check` antes de enviar alterações; essa verificação requer Rust
estável com rustfmt/clippy, Python 3.10+, Make, um compilador C11 e os utilitários
Unix usados nos testes (`wc`, `sh`, `cat`, `printf`, `sleep`, `touch` e `yes`).

Veja [CONTRIBUTING.md](CONTRIBUTING.md) para o processo e
[LICENSE.md](LICENSE.md) para autoria e permissões.

## Publicação no site

Pushes em `main` que adicionam, alteram, removem ou renomeiam `*/index.md`
disparam o workflow **Deploy production** no repositório do site, que valida
o conteúdo antes de publicar. Alterações em READMEs, testes e fixtures não
disparam esse deploy. PRs e outras branches também não publicam.

O workflow **Publish website content** precisa do secret `WEBSITE_DEPLOY_TOKEN`.
Consulte a [configuração no repositório do site](https://github.com/oxide-club/oxideclub.dev#one-time-trigger-setup).
Seu sucesso confirma o envio da solicitação; acompanhe **Deploy production**
no repositório do site para verificar o resultado da publicação.

## Licenciamento

Enunciados, explicações e textos educacionais usam CC BY 4.0; fixtures, dados
de entrada e saídas esperadas usam CC0 1.0; scripts de teste, validadores,
geradores e demais códigos executáveis usam MIT. Consulte a
[política de licenciamento](LICENSE.md) e os textos completos em [LICENSES/](LICENSES/).
Materiais de terceiros mantêm suas próprias licenças.

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
Para executar os testes sem enviar mensagens: `node --test tests/discord-*.test.mjs`
com Node.js 24. Mantenha os módulos de `scripts/discord/` sincronizados com os
correspondentes no repositório do site.
