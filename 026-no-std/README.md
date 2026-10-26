# 026-no-std — guia local

Leia o [contrato](index.md) e a [auditoria do suporte](materials/AUDIT.md). O pacote permanece em revisão.

## Ambiente

Validado em Linux x86-64, Rust 1.98.1 (48a229cea), target `x86_64-unknown-linux-gnu`, GCC 16.2.1, binutils 2.47 e Python 3.14.8.
O linking efetivo usou rust-lld/LLVM 22.1.8 por meio do driver `cc`. Não há dependências Cargo.
Rust: edição 2021, `opt-level=3`, LTO fat, `embed-bitcode=yes`, `panic=abort` e `relocation-model=static`.
Flags adicionais e limitações estão na auditoria. Cada comando de build é impresso pelo script.

## Preparar e executar

Execute a partir de `challenges/026-no-std`:

```sh
python3 tests/check.py --prepare --build-dir /tmp/oxide-nostd-build
python3 tests/check.py --build-dir /tmp/oxide-nostd-build
```

A preparação retorna 0: compila os dois executáveis, verifica ELF e testa stub e rotinas de memória.
O comando completo retorna 1 no starter: quatro testes da política de escrita falham por implementação pendente.
O starter compila, mas `raw_exit` contém `ud2`; executar seu binário termina por `SIGILL`, não pelo status contratual.
Essa é uma falha esperada do núcleo incompleto, não uma evidência de conformidade.

Edite `materials/starter/main.rs` e `materials/starter/policy.rs`.
Complete os wrappers e a política de escrita. O clube fornece a mensagem, a seleção de status 0/74 e o panic handler com status 101; preserve esses comportamentos. Preserve os apoios `start.S` e `memory.S`.
A opção de teste `--cfg test_panic` provoca panic antes da saída; o script constrói essa variante separadamente.

## Verificar

O adaptador `write_all_with` recebe o slice ainda pendente e retorna uma contagem ou `-errno`.
Ele deve simular somente retornos possíveis de `write`: contagem não superior ao slice ou errno Linux negativo.
A interface pública `write_all` permanece a do enunciado.

A suíte verifica vazio, avanços sem repetição, EINTR, WriteZero e errno positivo.
Depois, exige 19 bytes/status 0, stdout fechado/status 74 e panic sem saída/status 101.
Status de sinal e timeout são falhas, nunca substitutos para esses resultados.
A inspeção verifica ELF64 ET_EXEC, entry point igual a `_start`, ausência de PT_INTERP, DT_NEEDED e símbolos indefinidos.

```sh
readelf -hW -lW -dW /tmp/oxide-nostd-build/normal
nm -u /tmp/oxide-nostd-build/normal
objdump -d /tmp/oxide-nostd-build/normal
```

Os arquivos `/tmp/oxide-nostd-build/elf.txt` e `panic-elf.txt` registram o inventário dos dois builds.
A revisão de assembly e ABI continua obrigatória. Miri não foi usado para syscalls ou processos nativos.

## Evidências e limites

A referência reservada passou. Sete mutantes foram rejeitados. Os seis iniciais cobrem: avanço incorreto, EINTR como erro, zero aceito, status 74 incorreto, LF ausente e panic com status errado.
A revisão acrescentou o controle de `bcmp` que sempre retorna zero.

Os comandos foram executados em cópia do pacote. O piloto editorial e o download do fonte psABI fixado continuam pendentes.

## Licenças

Consulte [origem e licenças](materials/ORIGIN.md). As fontes externas preservam suas licenças próprias.

## Retificação de 25/10/2026

A suíte agora executa o caminho nativo com `RLIMIT_FSIZE=10` e `SIGXFSZ` ignorado somente no subprocesso. Exige exatamente `Oxide Club` (10 bytes) e status 74. O limite provoca escrita parcial seguida de erro; o teste isolado de `write_all_with` não cobria esse caminho.

A inspeção com `nm -C` rejeita símbolos remanescentes de `alloc` e das funções usuais do allocator Rust nos dois builds. Essa triagem não comprova ausência de alocação: LTO, remoção de símbolos, nomes próprios e assembly podem ocultá-la. A revisão das fontes, dependências, allocator global e disassembly continua obrigatória, inclusive para wrappers com `nomem` indevido. O controle com `alloc` é rejeitado; sua ausência em `nm` não aprova a composição por si só.

Os registros anteriores são históricos. A resposta à revisão (registro histórico retirado deste repositório) registra comandos, resultados e limites. Piloto, aprovação editorial e obtenção/licença do fonte psABI continuam pendentes; `draft: true` permanece.

## Retificação da segunda revisão — 25/10/2026

A triagem de símbolos reconhece a raiz da crate `alloc` e os nomes completos dos pontos de entrada conhecidos do allocator. Nomes como `main::noalloc::msg` e tipos de `core::alloc` não são proibidos por coincidência textual. A inspeção continua parcial: LTO pode incorporar uma alocação sem deixar esses símbolos; fontes, dependências e assembly ainda precisam de revisão.

O teste nativo acrescenta escrita parcial seguida de sucesso. `tests/write_limit.c` acompanha somente o próprio subprocesso com `ptrace` em Linux x86-64. Na entrada de cada `write` para stdout, limita a contagem passada ao kernel a um byte. Na saída, restaura `rdx`, preservado pela ABI, e mantém o retorno real do kernel. O candidato deve completar os 19 bytes e terminar com status zero. Não há opção de teste nem nova função a implementar na solução.

Duas sondas do clube verificam a instrumentação: uma escrita única produz um byte; um laço completa 12 bytes. Ambas conferem a preservação de `rdx`. A preparação compila o tracer e a sonda sem executar `ptrace`; a verificação completa exige a execução real. Se a sonda independente não puder usar `ptrace`, o verificador retorna 77 e registra a etapa como não executada. Um status 77 do candidato não é aceito como sucesso nem como prova de indisponibilidade.

O caso anterior de `RLIMIT_FSIZE=10` permanece: ele verifica escrita parcial seguida de erro. O novo caso verifica continuação até o sucesso. Os dois caminhos são necessários e não substituem os controles do adaptador para `EINTR` e retorno zero.

 Fonte/licença/correspondência do psABI, piloto e aprovação editorial continuam pendentes; `draft: true` permanece.

## Retificação da terceira revisão — 25/10/2026

O tracer cobre `write` e `writev` em stdout, sem exigir uma syscall específica no contrato de `raw_write`. Para `writev`, encontra o primeiro iovec não vazio, limita seu comprimento a um byte e apresenta somente esse elemento ao kernel. Antes de retomar o filho, restaura `iov_len`, `rsi` e `rdx`; o retorno em `rax` continua sendo o retorno real da syscall. O recorte é Linux x86-64, processo de uma thread e até 1024 iovecs; contagens inválidas e vetores vazios seguem sem alteração para o kernel.

`tests/writev_limit_probe.c` verifica escrita única, repetição até completar 13 bytes, elementos vazios, preservação do vetor e dos registradores, EFAULT e contagem inválida. O controle do instrumento que não restaura o vetor falha nessa sonda. A variante conforme com laço de `writev` passa; uma única escrita seguida de status 74 falha, pois não completa a saída após o retorno parcial.

Execute os mesmos comandos de preparação e verificação deste guia. A preparação também compila a sonda de `writev`. Na verificação completa, saída normal, panic, stdout fechado e limite de arquivo são conferidos antes de exigir ptrace. Assim, uma saída incorreta continua sendo falha (1) mesmo se ptrace estiver indisponível. Se a saída aparecer sem nenhuma chamada write/writev observada, o tracer não demonstrou a política: o resultado é 77, não aprovação. Outros mecanismos e composição de syscalls exigem auditoria; essa instrumentação não prova conformidade geral.
