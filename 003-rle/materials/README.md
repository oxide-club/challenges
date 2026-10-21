# Materiais de RLE

Cada `*.bin` contém bytes originais e o `*.rle` correspondente contém a
codificação canônica: contagem de 1 a 255 seguida do valor. Os exemplos incluem
entrada vazia, todos os valores de byte e sequências longas. Use `od -An -tx1`
para inspecionar os bytes sem interpretá-los como texto.

Na raiz do repositório, regenere as amostras e `../tests/cases.json` com:

```sh
python3 003-rle/materials/generate.py
```

O gerador usa um oráculo independente baseado em grupos de bytes iguais, sem
importar ou executar a solução de referência. Os 54 vetores comuns aos runners
Python e Rust incluem casos inválidos e erros reais de E/S. Os nove casos
`roundtrip-*` usam xorshift de 64 bits com estado inicial 3, mantido entre os
tamanhos. Comparam o encode com bytes canônicos e executam o decode da saída
real do programa, comparando-a à entrada original.

Para verificar a reprodução sem alterar arquivos, acrescente `--check` ao comando.
