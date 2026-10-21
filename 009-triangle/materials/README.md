# Materiais iniciais

`sample.txt` e `expected.bin` são entrada e saída exatas do vetor `triangle0`: um canvas preto 3×3 sem triângulos. `triangle.txt` e `triangle.ppm` correspondem ao vetor `triangle1`, com cores interpoladas. Compare arquivos binários com `cmp`; não use operações de texto nos pixels.

`oracle.py` gera uma imagem de referência usando frações exatas para entradas válidas pequenas:

```sh
python3 materials/oracle.py < materials/triangle.txt > /tmp/reference.ppm
cmp /tmp/reference.ppm materials/triangle.ppm
```

Os pixels são RGB em ordem de linhas. O contrato de cabeçalho está no enunciado; `ppm.h` fornece a gravação P6. `../tests/cases.json` contém também clipping, bordas compartilhadas, limites de coordenadas e entradas inválidas.
