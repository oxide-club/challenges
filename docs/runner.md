# Guia de instalação e uso do oxide-test

O `oxide-test` executa os testes públicos de um desafio no seu programa.
O executável inclui todos os testes.

## Escolha seu ambiente

| Sistema | Ambiente de teste |
| --- | --- |
| Linux | Instalação local |
| Windows | WSL 2 com Ubuntu (recomendado) ou Docker |
| macOS | Docker |

Compile e teste sua solução no mesmo ambiente Linux.
O runner usa recursos específicos de Linux e não tem uma versão nativa para Windows.

## Linux

1. Instale Git e as ferramentas de compilação. Em Ubuntu ou Debian, execute:

   ```sh
   sudo apt update
   sudo apt install -y build-essential curl ca-certificates git
   ```

2. Instale Rust pelo [instalador oficial](https://rust-lang.org/tools/install/).
   Abra um novo terminal. Confirme a instalação:

   ```sh
   cargo --version
   ```

3. Clone o repositório. Instale o runner:

   ```sh
   git clone https://github.com/oxide-club/challenges.git
   cd challenges
   cargo install --path . --locked
   ```

   A primeira instalação precisa de acesso à internet para baixar dependências.
   O Cargo instala o executável em `~/.cargo/bin`, salvo configuração diferente.

4. Confirme a instalação:

   ```sh
   oxide-test --version
   oxide-test list
   ```

Rust e Cargo são necessários para compilar o runner. Depois da instalação,
você pode usar o executável sem essas ferramentas.

### Compile e teste sua solução

No diretório do seu código, compile a solução. Passe o caminho do executável ao runner.

Exemplo de WC em C11:

```sh
cc -std=c11 -Wall -Wextra -Wpedantic meu-wc.c -o meu-wc
oxide-test run 001-wc ./meu-wc
```

Exemplo de RLE em Rust:

```sh
rustc --edition=2021 meu-rle.rs -o meu-rle
oxide-test run 003-rle ./meu-rle
```

Use aspas em caminhos com espaços: `oxide-test run 001-wc "./meu programa"`.
Consulte os requisitos de [WC](../001-wc/README.md),
[PPM](../002-ppm/README.md) ou [RLE](../003-rle/README.md).

## Windows com WSL 2 (recomendado)

1. Abra o PowerShell como administrador. Instale Ubuntu:

   ```powershell
   wsl --install -d Ubuntu
   ```

2. Reinicie o Windows se solicitado.
3. Abra Ubuntu. Crie seu usuário Linux.
4. No PowerShell, confira a versão do WSL:

   ```powershell
   wsl --list --verbose
   ```

   Se Ubuntu usar a versão 1, execute `wsl --set-version Ubuntu 2`.

5. No **terminal Ubuntu**, siga as instruções da seção [Linux](#linux).
6. Salve sua solução em um diretório Linux, como `~/minha-solucao`.
7. Compile e teste a solução no terminal Ubuntu.

Instale Rust dentro do Ubuntu. Uma instalação de Rust no Windows não substitui essa etapa.
Consulte o [guia oficial do WSL](https://learn.microsoft.com/en-us/windows/wsl/install)
se precisar de ajuda com a instalação.

## Docker

A imagem inclui o runner e os compiladores C e Rust.
Você não precisa instalar essas ferramentas no computador.

### Prepare a imagem

1. Instale e inicie Docker. No Windows, siga o
   [guia do Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/)
   e use containers Linux.
2. Confirme o acesso ao serviço:

   ```sh
   docker info
   ```

3. Clone este repositório, se necessário. Entre no diretório `challenges`.
4. Crie a imagem local:

   ```sh
   docker build -t oxide-test:local .
   docker run --rm --init oxide-test:local list
   ```

O build precisa de acesso à internet para baixar a imagem base e as dependências.

### Compile e teste sua solução

Entre no diretório que contém `meu-wc.c`.
Execute o comando correspondente ao seu terminal.

**Bash** (Linux, macOS ou WSL):

```sh
docker run --rm --init \
  --mount "type=bind,source=$(pwd),target=/submission,readonly" \
  --entrypoint sh oxide-test:local -ec \
  'cc -std=c11 -Wall -Wextra -Wpedantic /submission/meu-wc.c -o /tmp/meu-wc && oxide-test run 001-wc /tmp/meu-wc'
```

**PowerShell**:

```powershell
docker run --rm --init `
  --mount "type=bind,source=$($PWD.Path),target=/submission,readonly" `
  --entrypoint sh oxide-test:local -ec `
  'cc -std=c11 -Wall -Wextra -Wpedantic /submission/meu-wc.c -o /tmp/meu-wc && oxide-test run 001-wc /tmp/meu-wc'
```

Para testar RLE em Rust, substitua o trecho entre aspas simples por:

```sh
rustc --edition=2021 /submission/meu-rle.rs -o /tmp/meu-rle && oxide-test run 003-rle /tmp/meu-rle
```

Esses comandos leem seu código sem alterar o diretório da solução.
Eles compilam e testam o programa dentro do container.
O Docker remove os arquivos temporários ao encerrar o container.

Acrescente as opções de teste ao comando `oxide-test run`, dentro das aspas.

## Opções de teste

| Objetivo | Comando |
| --- | --- |
| Listar desafios | `oxide-test list` |
| Listar casos | `oxide-test list 001-wc` |
| Executar todos os casos | `oxide-test run 001-wc ./meu-wc` |
| Executar um caso | `oxide-test run 001-wc ./meu-wc --case sem-quebra` |
| Parar na primeira falha | `oxide-test run 001-wc ./meu-wc --fail-fast` |
| Definir o limite de tempo | `oxide-test run 001-wc ./meu-wc --timeout 10` |
| Salvar o relatório JSON | `oxide-test run 001-wc ./meu-wc --json > resultado.json` |

Repita `--case ID` para selecionar vários casos.
O limite padrão é de cinco segundos por execução do programa.
Cada caso de ida e volta de RLE executa o programa duas vezes.

## Leia o resultado

O relatório mostra os casos que passaram, falharam ou foram ignorados.
Em uma falha, ele mostra a causa e um comando para repetir o caso.
Diferenças de saída mostram bytes esperados e recebidos.
Diferenças em pixels PPM também mostram coordenadas.

`Passed all public tests` indica que todos os testes públicos passaram.
Um teste com `--case` verifica apenas os casos selecionados.
Os testes não verificam todos os requisitos, como linguagem e uso de memória.
Esses requisitos precisam de revisão do código.

| Código de saída | Resultado |
| --- | --- |
| `0` | Todos os casos selecionados passaram |
| `1` | Pelo menos um caso falhou |
| `2` | Erro de comando, preparação ou funcionamento do runner |
| `3` | Há casos ignorados e nenhuma falha |

Para consultar o código de saída, use `$?` em Bash ou `$LASTEXITCODE` em PowerShell.

### Relatório JSON

A opção `--json` escreve um documento JSON na saída padrão.
O documento usa `schema_version: 1`.

| Campo | Conteúdo |
| --- | --- |
| `runner_version`, `test_revision` | Versão do runner e revisão dos testes |
| `challenge`, `program` | Desafio e caminho do programa |
| `all_public_tests_passed` | Indica se todos os testes públicos passaram |
| `summary` | Totais de casos disponíveis, selecionados, executados, aprovados, reprovados e ignorados |
| `results` | Resultado, duração, diagnóstico e comando de repetição de cada caso |

Em `summary`, `not_run` conta os casos selecionados que não foram executados após
uma parada por `--fail-fast`. Casos excluídos por `--case` não entram nessa contagem.
Erros de comando ou preparação usam um objeto `error`.

## Problemas comuns

| Problema | Ação |
| --- | --- |
| `oxide-test: command not found` | Abra um novo terminal. Confira se `~/.cargo/bin` está no `PATH` |
| `linker cc not found` | Instale `build-essential` no Ubuntu ou Debian |
| `Exec format error` | Compile sua solução no WSL ou container escolhido. Passe o executável, não o arquivo `.c` ou `.rs` |
| `No such file or directory` | Confira o caminho. Se o arquivo existir, recompile no ambiente de teste para usar as bibliotecas corretas |
| Sem permissão de execução | Execute `chmod +x ./meu-wc` |
| `timeout` | Confira se o programa termina ao receber o fim da entrada |
| `output_limit` | Confira se há mensagens extras ou escrita sem fim na saída |
| Caso ignorado por falta de `/dev/full` | Use um ambiente Linux com esse dispositivo |
| Docker não conecta ao serviço | Inicie Docker Desktop ou Docker Engine. Execute `docker info` |

O runner limita o tempo e a saída do programa. Ele não impede acesso a arquivos
ou à rede. Execute apenas programas nos quais você confia.

## Uso como biblioteca Rust

A biblioteca `oxide_test` contém os módulos `challenges::wc`, `challenges::ppm` e
`challenges::rle`. Os IDs públicos, como `001-wc`, são metadados.
Use `oxide_test::run` para executar uma suíte e obter um relatório.
Consulte a [API no código](../src/lib.rs).

Para alterar o runner, siga o [guia de contribuição](../CONTRIBUTING.md).
