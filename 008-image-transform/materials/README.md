# Materiais iniciais

`sample` e `expected.bin` são entrada e saída exatas do primeiro vetor público não vazio. Confira o campo `argv` correspondente em `../tests/cases.json`; a saída pode ser binária, portanto compare com `cmp`, e não com operações de texto. Os vetores têm casos maiores e erros adicionais.

Imagens são RGB em ordem de linhas, sem interpretação dos bytes como texto. O contrato estrito de cabeçalho está no enunciado. O helper PPM faz leitura/gravação e libera o estudante para trabalhar as coordenadas.
