# Materiais iniciais

`sample.bin` e `expected.bin` são entrada e saída exatas do primeiro vetor público não vazio. Veja o argumento necessário em `../tests/cases.json`. Use `cmp` para comparar os arquivos e `od -An -tx1` para inspecionar bytes.

`generate.py TAMANHO` escreve bytes 0..255 cíclicos em stdout sem carregar a entrada inteira na memória; limite 0..16777216. Exemplo: `python3 materials/generate.py 1000000 > /tmp/bytes.bin`. O gerador inclui zero e 0xff.
