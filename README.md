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

Use Python 3.10 ou superior em Unix/Linux. Na raiz deste repositório, substitua
`ID_DO_DESAFIO` pelo identificador escolhido:

```sh
python3 ID_DO_DESAFIO/tests/test.py /caminho/para/seu-programa
```

Os executores usam a biblioteca padrão do Python. O programa deve estar
compilado e ter permissão de execução. Consulte o README do desafio para os
comandos de compilação, casos cobertos e opções do executor.

## Como contribuir

Proponha novos desafios, esclarecimentos ou testes por pull request.
Combine o próximo número com os mantenedores e preserve os IDs já publicados.
Execute `make check` antes de enviar alterações; essa verificação requer também
Make e o utilitário Unix `wc`.

Veja [CONTRIBUTING.md](CONTRIBUTING.md) para o processo e
[LICENSE.md](LICENSE.md) para autoria e permissões.

## Licenciamento

Enunciados, explicações e textos educacionais usam CC BY 4.0; fixtures, dados
de entrada e saídas esperadas usam CC0 1.0; scripts de teste, validadores,
geradores e demais códigos executáveis usam MIT. Consulte a
[política de licenciamento](LICENSE.md) e os textos completos em [LICENSES/](LICENSES/).
Materiais de terceiros mantêm suas próprias licenças.
