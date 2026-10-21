# Materiais de WC

Os arquivos `*.in` contêm entradas em bytes; cada `*.out` contém a resposta
exata correspondente. Há arquivos vazios e separadores ASCII de controle.
`generate.py` preserva esses exemplos e acrescenta os vetores de uma palavra de
128 KiB e 32768 linhas em `../tests/cases.json`.

Na raiz do repositório, regenere com:

```sh
python3 001-wc/materials/generate.py
```

Os 13 vetores são usados pelos runners Python e Rust. As contagens publicadas
podem ser conferidas com `LC_ALL=C wc -l -w -c`, desconsiderando o alinhamento.
O gerador e os testes não executam a solução de referência.

Para verificar a reprodução sem alterar arquivos, acrescente `--check` ao comando.
