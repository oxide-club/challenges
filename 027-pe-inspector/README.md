# 027-pe-inspector — guia local

Leia a [definição](index.md). O pacote passou pela revisão técnica e teve a saída de rascunho autorizada pelo responsável, com dispensa do piloto.

## Ambiente e linguagens

Starter mantido: Rust 2021 com biblioteca padrão, sem crates externas.
C continua aceito pelo contrato. Os checks recebem um executável de qualquer uma dessas linguagens.
Validação realizada em Linux x86-64, Rust 1.98.1 e Python 3.14.8.
Windows não foi executado nesta preparação; não há validação de runtime dessa plataforma.

## Preparar e executar

Execute a partir deste diretório. Os arquivos PE gerados são dados sintéticos; não os execute.

```sh
python3 tests/check.py --prepare
python3 materials/generate.py /tmp/pe-fixtures
rustc --edition 2021 -D warnings materials/starter/main.rs -o /tmp/peinspect
python3 tests/check.py /tmp/peinspect
```

O primeiro comando deve terminar com `OK preparação` e status 0.
O starter compila, mas a suíte retorna 1: `not_implemented` é uma falha intencional.
Complete leitura, CLI, parsing, validação de intervalos, classificação e serialização.
As estruturas sugeridas não impõem a arquitetura interna da solução.

Depois de implementar, execute:

```sh
/tmp/peinspect /tmp/pe-fixtures/base.bin --rva 0x1010 --size 1
python3 tests/test.py /tmp/peinspect
```

A consulta deve indicar `section_raw` e `file_offset="0x210"`.
A suíte exige os 76 casos; cada execução tem prazo de cinco segundos.
Os testes criam arquivos temporários, incluindo limites de 64 MiB, e os removem ao terminar.
Reserve pelo menos 140 MiB livres para os dois arquivos de fronteira, mesmo onde arquivos esparsos não existam.

## Verificar

[Materiais](materials/README.md) documentam fixtures, offsets, saída e diagnósticos.
[Casos independentes](tests/cases.json) contêm o inventário e as consultas esperadas.
A suíte compara JSON completo, tipos, campos, status e ausência de inventário parcial.
Casos com violações simultâneas aceitam um conjunto explícito de códigos, sem fixar precedência global. Opções repetidas não têm comportamento exigido por esta suíte.
A revisão de invariantes e de aritmética continua necessária: passar nos casos não prova segurança geral.

Para uma comparação complementar:

```sh
llvm-readobj --file-headers --sections /tmp/pe-fixtures/base.bin
od -Ax -tx1 -N 304 /tmp/pe-fixtures/base.bin
```

LLVM 23.1.3 confirmou os campos da base durante a preparação.
O leitor de produção não estabelece a política de classificação deste desafio.
O fixture omite requisitos de um loader, como alinhamentos executáveis.

## Entrega

Entregue os artefatos e a justificativa da [seção Requisitos](index.md#requisitos).
Registre o ambiente, as invariantes, os resultados e as limitações.
Estimativa provisória: 10–14 horas; o piloto ainda deve recalibrá-la.
As evidências da preparação (registro histórico retirado deste repositório) registram a preparação histórica.

## Licenças

Documentação original: CC BY 4.0. Código original: MIT. Fixtures e saídas esperadas originais: CC0 1.0.
Os materiais foram preparados para o Oxide Club em 25/10/2026. Não incluem código de terceiros.

## Retificação da terceira revisão — 25/10/2026

O arquivo `too-large` agora começa com `base.bin` e recebe zeros até 64 MiB + 1 byte. O overlay preserva o formato válido e isola o limite de tamanho. Em `e-lfanew-huge`, a suíte aceita `truncated_pe` ou `truncated_optional`, conforme o critério existente de admissibilidade. A suíte mantém 76 casos; as variantes que verificam formato antes de tamanho ou a parte fixa do optional header antes de COFF passam. Um controle que ignora o limite de tamanho continua rejeitado.
