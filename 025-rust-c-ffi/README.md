# 025-rust-c-ffi — guia local

Leia o [contrato](index.md). O pacote está disponível para implementação pelo participante.

## Ambiente e linguagens

Validação: Linux x86-64, Rust 1.98.1 (48a229cea), edição 2021, GCC 16.2.1, GNU binutils 2.47, glibc 2.44 e Python 3.14.8.
Target Rust: `x86_64-unknown-linux-gnu`. Não há dependências Cargo.
Rust usa `-C panic=unwind -C opt-level=1`; C usa `-std=c11 -O1 -g -Wall -Wextra -Werror`.
O linking usa `-ldl -lpthread -lm`. O script imprime todos os comandos.

## Preparar e executar

Execute a partir de `challenges/025-rust-c-ffi`:

```sh
python3 materials/generate.py --check
python3 tests/check.py --prepare --build-dir /tmp/oxide-ffi-build
python3 tests/check.py --build-dir /tmp/oxide-ffi-build
```

A preparação deve terminar com status 0: compila Rust, C e os dois clientes; verifica layout e símbolos exportados.
O último comando retorna 1 no starter: o helper ainda não implementa a rotação. Isso não é falha de build.
O cliente C também exige criação, transformação, descarte e contenção de panic ainda não implementados.

Edite `materials/starter/rust/lib.rs` e `materials/starter/rotate.c`.
Complete a documentação de pré-condições em `materials/starter/oxide.h`.
O cabeçalho já oferece as assinaturas e o layout para permitir compilar os clientes.
Preserve o suporte de testes `rust/hooks.rs`.

O gancho `oc_test_panic_next` existe somente no build `--cfg test_hooks`.
Ele arma uma falha por thread. Chame `hooks::checkpoint()` dentro da região que captura panic, após validar argumentos, poison e capacidade.
O build de distribuição deve omitir `test_hooks` e `OC_TEST_HOOKS`.

## Verificar

`tests/client.c` verifica o layout LP64 nos dois lados, erros escalares, precedência, sentinelas, contexto envenenado e 512 transformações.
`tests/helper.rs` testa a chamada Rust → C com valores literais.
`tests/layout.rs` confere tamanho 24, alinhamento 8 e offsets 0/8/16.
Os testes nunca fabricam handles expirados, aleatórios ou regiões inválidas como se fossem entradas seguras.

Para inspecionar o build já preparado:

```sh
nm --defined-only /tmp/oxide-ffi-build/client
readelf -hW /tmp/oxide-ffi-build/client
```

No starter, `oc_rotate` pode desaparecer do cliente C por não haver chamada implementada.
A referência completa foi conferida com o símbolo presente e o caminho C → Rust → C executado.
Ausência de diagnóstico não prova validade geral da ABI. Revise cada bloco `unsafe`, o descarte do payload de panic e o ownership do contexto.

## Evidências e limites

A referência reservada passou. Oito mutantes foram rejeitados. Os cinco iniciais cobrem: rotação incorreta, `required` incorreto, `written` incorreto, ausência de poison e chave ignorada.
A revisão acrescentou helper ignorado, exports seguros indevidos e precedência escalar após poison.
Registros: evidências FFI (registro histórico retirado deste repositório).
A reprodução do participante usa uma cópia independente do diretório inteiro. Não usa `solutions/` nem referência privada.
Não se declara execução de Miri para esta FFI nativa. O piloto não foi executado e foi dispensado pelo responsável.

## Licenças

Consulte [origem e licenças](materials/ORIGIN.md). Código MIT; documentação CC BY 4.0; fixtures CC0 1.0.

## Retificação de 25/10/2026

O cliente informa a linha da chamada e os campos observados quando um resultado diverge. O caso `dst == NULL`, capacidade zero e entrada não vazia exige `BufferTooSmall`.

A suíte completa compila também a biblioteca de distribuição sem `test_hooks` e executa `tests/destroy.c` com LeakSanitizer (`cc -fsanitize=leak`). O cliente cria, usa e destrói 32 contextos sem provocar panic; o verificador exige ausência de vazamentos detectados e ausência do símbolo do gancho. É necessário o runtime LSan do compilador C. Esse controle detecta o mutante com destruição vazia sem confundir a retenção de payload de panic da referência histórica com vazamento de contexto. Não é uma prova geral de ausência de vazamentos nem audita o descarte de payloads.

Os clientes são fornecidos pelo clube. O participante completa a biblioteca, o helper e a documentação de ponteiros e justifica os testes; escrever clientes adicionais é opcional.

Os registros anteriores são históricos. A saída de rascunho foi autorizada pelo responsável, com dispensa do piloto.

## Retificação da segunda revisão — 25/10/2026

Além do cliente de distribuição sem panic, a suíte executa `tests/destroy_poison.c` no build `test_hooks`. Ele cria oito contextos vivos, provoca `InternalPanic`, confirma `Poisoned` e destrói cada contexto uma única vez. O LSan deve detectar contextos vazados também nesse estado.

A referência histórica retém o payload do panic estático fornecido pelo clube. A supressão deste teste é restrita ao símbolo exato de `StaticStrPayload::take_box` do runtime Rust identificado por uma sonda independente. Não há supressão de `malloc`, `alloc`, `oc_create`, `oc_transform` ou de um frame genérico de panic. Usa-se `fast_unwind_on_malloc=0` para registrar a stack completa da alocação. Esse controle foi validado com Rust 1.98.1; mudanças no runtime exigem repetir a validação da supressão.

Antes de testar o candidato, a sonda do clube confirma duas propriedades: o payload conhecido não reprova o caso sem outro vazamento; uma alocação independente de 37 bytes continua detectada. O cliente de distribuição roda sem supressão. Apenas a sonda independente pode determinar indisponibilidade de LSan e status 77; texto impresso pelo candidato não transforma falha em ambiente indisponível.

A resposta à segunda revisão (registro histórico retirado deste repositório) registra a matriz, os controles conformes, as supressões utilizadas e os limites. A supressão específica não demonstra ausência geral de vazamentos de payloads nem substitui a revisão de `unsafe` e dos caminhos de unwind.
