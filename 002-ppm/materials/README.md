# Materiais de PPM

`gradient.ppm` é a imagem P6 de 256 × 256 pixels especificada no desafio,
com 196623 bytes. Abra-a em um visualizador compatível com PPM.

Na raiz do repositório, regenere a imagem e `../tests/cases.json` com:

```sh
python3 002-ppm/materials/generate.py
```

O gerador calcula os canais diretamente das coordenadas, sem executar a solução
de referência. Os dois casos comuns aos runners Python e Rust verificam todos os
pixels e a falha de escrita em `/dev/full`.

Para verificar a reprodução sem alterar arquivos, acrescente `--check` ao comando.
