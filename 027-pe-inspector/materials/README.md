# Materiais — Inspetor de executáveis PE

Pacote revisão 2, preparado em 25/10/2026. Mantenha o desafio em revisão.

## Inventário

| Arquivo | Responsabilidade |
| --- | --- |
| `starter/main.rs` | Tipos sugeridos e funções incompletas; implemente o leitor e a CLI. |
| `generate.py` | Gera fixtures sintéticas; não contém parser nem classificador de RVA. |
| `offsets.json` | Campos e intervalos calculados da base, em offsets absolutos. |
| `fixture-manifest.json` | Tamanho e SHA-256 de cada fixture gerada na revisão 2. |
| `../tests/cases.json` | Resultados independentes: inventários, consultas, diagnósticos e status. |
| `../tests/check.py` | Verifica fixtures e contrato JSON; executa o programa sob prazo. |
| `../tests/test.py` | Entrada convencional para a mesma suíte pública. |

O gerador usa `struct.pack_into`; os resultados foram calculados separadamente por campos e intervalos.
O verificador usa `int.from_bytes` e bytes literais para conferir o manifesto de offsets.
`llvm-readobj` forneceu uma terceira conferência dos campos de `base`.
A referência privada e os mutantes não fazem parte da distribuição.

## Layout conhecido e hexdump anotado

Todos os intervalos são semiabertos. Os inteiros são little-endian.

| Offset | Bytes da base | Interpretação |
| --- | --- | --- |
| `0x00` | `4d 5a` | Assinatura MZ. |
| `0x3c` | `80 00 00 00` | PE começa em `0x80`. |
| `0x80` | `50 45 00 00 64 86 01 00` | Assinatura, AMD64 e uma seção. |
| `0x94` | `70 00` | Optional header ocupa 112 bytes. |
| `0x98` | `0b 02` | PE32+. |
| `0xa8` | `10 10 00 00` | Entry RVA `0x1010`. |
| `0xb0` | `00 00 00 40 01 00 00 00` | Image base `0x140000000`. |
| `0xd4` | `00 02 00 00` | Headers terminam em `0x200`. |
| `0x104` | `00 00 00 00` | Nenhum diretório na base. |
| `0x108` | `2e 74 65 78 74 00 00 00` | Nome de oito bytes. |
| `0x110` | `00 03 00 00 00 10 00 00` | VirtualSize `0x300`, RVA `0x1000`. |
| `0x118` | `00 02 00 00 00 02 00 00` | RawSize e RawPointer `0x200`. |

A tabela termina em `0x130`. Headers ocupam `[0,0x200)`; raw ocupa `[0x200,0x400)`.
O prefixo virtual raw ocupa `[0x1000,0x1200)`; zero-fill ocupa `[0x1200,0x1300)`.
O arquivo contém 1024 bytes. Os bytes não especificados são zero.

`padding` reduz VirtualSize para `0x100`: bytes raw posteriores continuam listados, sem RVA consultável.
`empty` mantém ambos os tamanhos zero e usa raw offset arbitrário, que não deve ser acessado.
`zero-fill-only` mantém VirtualSize positivo e RawSize zero.
`directories` declara 16 diretórios e oito bytes adicionais no optional header.
Os endereços deliberadamente altos continuam opacos, inclusive no índice 4 de certificados.
`count-96` ocupa 4608 bytes de headers e começa suas seções virtuais em `0x2000`.
`top-boundary` termina exatamente em `2^32`; `rva-overflow` ultrapassa esse limite.
`binary-name` exige preservar oito bytes arbitrários, incluindo zero e bytes não ASCII.
Os demais nomes identificam a alteração introduzida. Um truncamento pode violar vários limites ao mesmo tempo; consulte os conjuntos aceitos abaixo.
`max-size`, `too-large` e arquivo ausente são preparados pela suíte, sem arquivos grandes no repositório.

## Interface de diagnóstico

Complemento de contrato aprovado em 25/10/2026: sucesso escreve um objeto JSON em stdout, sem stderr.
Uma falha deixa stdout vazio e escreve em stderr um objeto com `code`, `field` e `offset`.
`field` é um nome não vazio; `offset` usa a mesma notação hexadecimal do inventário.
Não se exige uma mensagem textual nem um nome de campo específico.
A suíte verifica o código nos casos isolados e a existência da localização.
Para uso e I/O, `field` pode ser `arguments` ou `file`, com offset `0x0`.

| Código | Condição isolada |
| --- | --- |
| `unsupported_format` | Assinatura, máquina ou magic fora do formato aceito. |
| `unsupported_layout` | Raw invade headers; RVA não vazio invade headers; VirtualSize zero com raw. |
| `too_large` | Arquivo ultrapassa 64 MiB. |
| `truncated_dos` | Menos de 64 bytes para DOS header. |
| `truncated_pe` | Assinatura e COFF header não cabem no offset declarado. |
| `truncated_optional` | Parte fixa de 112 bytes ou tamanho declarado não cabe. |
| `truncated_sections` | A section table declarada não cabe. |
| `truncated_raw` | Intervalo raw não vazio ultrapassa o arquivo. |
| `invalid_count` | Quantidade de seções fora de 1–96. |
| `invalid_directories` | Mais de 16 diretórios ou espaço declarado insuficiente. |
| `invalid_headers` | SizeOfHeaders não cobre a tabela ou ultrapassa o arquivo. |
| `raw_overlap`, `virtual_overlap` | Intervalos não vazios de seções se sobrepõem. |
| `rva_overflow` | Limite exclusivo virtual ultrapassa `2^32`. |
| `usage`, `io` | Respectivamente status 2 e 4. |

Os códigos estruturais retornam status 3. Classificações retornam status 0, inclusive `unmapped` e `cross_region`.
Violações simultâneas não têm precedência global imposta pela suíte. O catálogo normativo contém 16 códigos (14 estruturais, mais `usage` e `io`); a contagem “15” usada na revisão era inexata.

Os conjuntos de `expected` em `cases.json` são derivados das condições do catálogo, usando somente campos inteiramente presentes no arquivo e aritmética sem overflow. Os offsets seguem os valores declarados na entrada; não se exige validar semanticamente uma estrutura anterior para diagnosticar outra cujo intervalo de leitura cabe fisicamente. Isso não autoriza ler campos ausentes ou reposicionar estruturas por tamanho presumido. `sections-short` aceita `truncated_sections`, `invalid_headers` ou `truncated_raw`: a tabela, os headers declarados e o raw declarado excedem o arquivo. `optional-short` aceita `truncated_optional`, `truncated_sections` ou `invalid_headers`. `pe-short` aceita `truncated_pe`, `truncated_optional` ou `truncated_sections`; os campos de contagem e tamanho ainda estão presentes. `optional-small` aceita `truncated_optional`, `invalid_directories` ou `truncated_raw`. O tamanho declarado é 111, menor que os 112 bytes fixos. Pela posição declarada da tabela, os campos raw presentes também descrevem um intervalo além do arquivo. `optional-declared-truncated` aceita `truncated_optional`, `truncated_sections` ou `invalid_headers`.

`count-97` agora contém a tabela completa, sem conflito com headers. `headers-large` usa seção vazia para isolar `SizeOfHeaders` além do arquivo. `headers-exact` é válido e termina os headers exatamente no fim da tabela. Não se exige uma política para opções repetidas.
Na CLI, aceite RVA hexadecimal com ou sem `0x`; size usa dígitos decimais.
Os exemplos obrigatórios usam a ordem `--rva HEX --size DEC`.

## Responsabilidade do participante

Implemente a validação antes do inventário. Verifique aritmética antes de converter offsets para índices.
Classifique o intervalo inteiro; não leia conteúdo de diretórios e não execute imagens.
Justifique cada acesso e cada fronteira. Produza seu próprio hexdump anotado e memória técnica.
Os checks são instrumentos do clube; a solução continua incompleta no starter.

## Origem, revisões e licenças

Fixtures e resultados: originais do Oxide Club, revisão 2, CC0 1.0; sem arquivos executáveis obtidos de terceiros.
Código de suporte e starter: original, MIT. Documentação: CC BY 4.0.
Contrato: atividade editorial 29 do currículo de 25/10/2026; redação conforme Português Técnico Claro 1.1.

A especificação [Microsoft PE Format](https://learn.microsoft.com/en-us/windows/win32/debug/pe-format) foi consultada em 25/10/2026.
Ela orienta offsets e representações; o contrato do desafio define o subconjunto aceito.
O documento Microsoft é móvel; a data de consulta identifica a leitura, sem alegar uma revisão imutável.

O código [COFFObjectFile.cpp, llvmorg-20.1.8](https://raw.githubusercontent.com/llvm/llvm-project/llvmorg-20.1.8/llvm/lib/Object/COFFObjectFile.cpp) foi consultado na mesma data.
Observe `getObject`, que encaminha limites a `Binary::checkOffset`, e `getRvaPtr`.
Pergunta: quais verificações pertencem à representação da imagem e quais pertencem à consulta?
LLVM atende formatos e tolerâncias além deste exercício. Seu código tem licença Apache-2.0 WITH LLVM-exception e não foi copiado.
O [manual de llvm-readobj 20.1.0](https://releases.llvm.org/20.1.0/docs/CommandGuide/llvm-readobj.html) documenta as opções usadas.
O binário efetivamente executado foi 23.1.3; não confunda versão da referência com versão da ferramenta local.

## Ampliação após revisão

As fixtures `reverse-table` e `virtual-touch` cobrem múltiplas seções em ordem não crescente, consulta à segunda seção e intervalos virtuais adjacentes. A suíte atual tem 76 casos. Os resultados esperados preservam os índices da tabela original; tocar um limite exclusivo não é sobreposição.

A nova consulta de 25/10/2026 confirmou `getObject` chamando `Binary::checkOffset` em `COFFObjectFile.cpp` (linha 56). A implementação de [`Binary::checkOffset`, na mesma revisão](https://github.com/llvm/llvm-project/blob/llvmorg-20.1.8/llvm/include/llvm/Object/Binary.h) verifica overflow e os limites do buffer (linhas 163–170). Os dois arquivos declaram Apache-2.0 WITH LLVM-exception. Nenhum trecho foi incorporado ao starter.

## Derivação de `optional-small`

O arquivo tem 1024 bytes. `e_lfanew=128`, o optional header começa em 152 e `SizeOfOptionalHeader=111`. Assim, a tabela declarada começa em 263; seus 40 bytes estão presentes. Os campos lidos nessa posição são `VirtualSize=196608`, `VirtualAddress=1048576`, `SizeOfRawData=131072` e `PointerToRawData=131072`. O fim raw é 262144, maior que 1024: `truncated_raw` é admissível, além dos dois diagnósticos de tamanho do optional header. Esses valores foram lidos independentemente do parser candidato. Não se desloca a tabela para 264 por conveniência.

A ausência de precedência significa que `truncated_optional` e `truncated_sections` podem nunca ser escolhidos por uma implementação conforme. A obrigação observável é rejeitar a entrada com um código cuja condição se verifica; não é exercer todos os nomes do catálogo.

## Derivações conferidas na terceira revisão

`too-large` tem 67.108.865 bytes: os primeiros 1024 são exatamente `base.bin`; os demais são zero. O overlay é permitido, os campos originais continuam válidos e somente `too_large` é admissível. Um arquivo inteiramente zerado acrescentava outras violações e não isolava esse limite. A suíte cria esse arquivo temporariamente; o gerador de fixtures pequenas e seu manifesto não mudaram.

Em `e-lfanew-huge`, o offset PE é `0xffffffff`. Nem o intervalo PE/COFF de 24 bytes nem a parte fixa do optional header, situada 24 bytes adiante e com 112 bytes, cabem no arquivo. As somas cabem em aritmética de 64 bits. Assim, `truncated_pe` e `truncated_optional` são admissíveis, sem ler campos ausentes. O oráculo independente da revisão foi repetido nos 26 casos estruturais e não encontrou divergências após estas correções.
