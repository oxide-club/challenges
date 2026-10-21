# Vetores binários compartilhados

Os desafios `001`–`021` usam `<id>/tests/cases.json` como fonte única de casos.
Python lê esse arquivo com `tools/vector_runner.py`; Rust o incorpora com
`include_str!`. O binário distribuído continua independente de Python e de
arquivos externos.

```json
{
  "schema_version": 1,
  "cases": [
    {
      "id": "encode-nul",
      "name": "Um byte zero",
      "argv": ["encode"],
      "stdin_hex": "00",
      "stdout_hex": "41413d3d"
    },
    {
      "id": "decode-invalid",
      "name": "Caractere fora do alfabeto",
      "argv": ["decode"],
      "stdin_hex": "21",
      "reject": true
    }
  ]
}
```

Cada caso tem `id`, `name`, `argv` e `stdin_hex`. IDs são únicos na suíte e
usam palavras minúsculas/números separadas por hífen. Hexadecimal é minúsculo,
sem espaços, com dois dígitos por byte; a string vazia representa zero bytes.
Os dados esperados devem vir do contrato ou de um modelo independente da
referência C. Comparar somente ida e volta pode esconder erros complementares.

Use exatamente uma expectativa: `stdout_hex` exige status zero e comparação
exata; `reject: true` exige status diferente de zero e diagnóstico não vazio em
stderr. Diagnósticos apenas com whitespace são rejeitados. `stderr_hex` opcional
exige comparação exata adicional, útil quando o contrato especifica um trace.

`roundtrip_argv` opcional contém os argumentos da segunda invocação. Primeiro,
o runner exige a saída exata de `stdout_hex`; depois, envia essa saída real
à segunda invocação e compara o resultado com `stdin_hex`. Cada invocação tem
seu próprio timeout e limite de saída. A segunda deve terminar com status zero;
`stderr_hex` verifica apenas a primeira. Use uma lista não vazia de strings,
sem NUL ou `{input}`, apenas com saída esperada, E/S normal e sem `input_file`.

Imagens esperadas com cabeçalho P6 canônico também recebem diagnóstico de
pixel e canal quando há diferença nos bytes dos pixels.

`input_file: true` grava os bytes de `stdin_hex` em um arquivo temporário cujo
caminho substitui os argumentos iguais a `{input}`; stdin fica vazio. O arquivo
permanece disponível até o processo terminar e é removido depois. Isso verifica
interfaces que recebem nomes de arquivo, incluindo caminhos com espaços.

`io` opcional aceita `normal` (padrão), `full` (stdout em `/dev/full`),
`directory` (diretório em stdin, Linux) ou `broken_pipe` (stdout sem leitor).
Esses modos verificam tratamento de erros reais de E/S; não combine com
`input_file`. Recursos indisponíveis aparecem como casos ignorados.

O limite de stdout é o tamanho esperado, ou 256 KiB nos casos de rejeição;
stderr tem limite de 64 KiB. Ambos os runners reaproveitam os executores com
timeout e encerramento do grupo de processos. O timeout padrão é cinco segundos
por invocação. Rust permite `--case`, `--fail-fast` e `--json` como antes.

## Acrescentar uma suíte

1. Escreva o contrato em `index.md`, os vetores e os materiais necessários.
2. Crie `tests/test.py` com o mesmo wrapper dos novos desafios.
3. Registre o ID em `tools/oxide-test/src/challenges/mod.rs`.
4. Execute `make check` e a referência pelos dois runners.
5. Verifique que um programa incorreto falha. Nos exercícios de debugging,
   confirme a regressão no starter e na versão corrigida.

APIs C são expostas por adaptadores fornecidos junto aos desafios. Os testes
diretos de API verificam invariantes que a saída do adaptador não demonstra;
o desafio de uso após liberação acrescenta ASan/UBSan. O runner executa um
binário já compilado: ele não compila submissões nem substitui análise de
complexidade, revisão de código ou a explicação da investigação.
