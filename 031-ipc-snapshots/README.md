# 031-ipc-snapshots — guia local

Leia o [contrato](index.md). Os starters de `target` e `observer` compilam, mas não implementam a sessão. Os fixtures de protocolo, layout e inspeção estão disponíveis. A saída de rascunho foi autorizada pelo responsável, com dispensa do piloto.

## Ambiente e build

Linux x86-64, mesma glibc e ABI nos dois programas; GCC 16.2.1, C11, pthreads e Python 3. Use VM ou sessão própria autorizada, sem privilégios administrativos. O sandbox local bloqueou operações de sessão; a execução externa autorizada passou. Registre kernel, `getconf GNU_LIBC_VERSION` e saída do probe do layout; não transporte bytes de `pthread_mutex_t` entre libcs distintas.

```sh
make all
python3 tests/check.py --prepare
./build/region-probe
python3 tests/check.py ./build/target
python3 tests/observer.py ./build/observer
```

`--prepare` termina com 0 e confirma os starters incompletos; os testes de solução devem falhar enquanto as tarefas não forem implementadas. Complete `starter/target.c` e `starter/observer.c`. O probe sem argumentos publica `sizeof(struct ox_region)`, offset e tamanho do mutex, calculados pelo compilador.

## Interface dos executáveis e região

`target --observer /caminho/absoluto/observer [--test-worker]` cria uma sessão sob `TMPDIR` (ou `/tmp`), inicia o observador com argumentos `<socket-path> <token-fd>` e entrega exatamente 32 bytes aleatórios pelo pipe. O número do descritor não é segredo; seu conteúdo é. O observador fecha o pipe, converte os bytes em 64 hexadecimais minúsculos e autentica. Não publique o token em argumentos, ambiente, JSON ou stderr.

O target retorna 0 quando todos os usuários encerraram e o cleanup terminou, inclusive após uma recusa protocolar esperada pelo observador de teste. Falha de setup, cleanup ou status não zero do filho retorna 1; uso inválido retorna 2. O observador retorna 0 para sua sessão prevista, 1 para sessão inválida e 2 para uso inválido. Esses status auxiliares não substituem os códigos do protocolo.

`materials/region.h` fixa a ordem: `version`, `generation`, `counter`, `counter_xor` (quatro uint64_t), depois mutex. Use o tamanho nativo calculado. Inicialize com `PTHREAD_PROCESS_SHARED` e `PTHREAD_MUTEX_ROBUST`; a versão é 1. Não leia sequer versão/invariantes fora do mutex depois da publicação. Confira `fstat` antes de mapear e a versão sob mutex depois de mapear. Inicialização ocorre antes de publicar o descritor.

## Framing, descritores e prazos

A fronteira de 256 bytes **inclui LF**. A linha não termina num fragmento incompleto. A resposta `OK 0 HELLO <size>\n` carrega exatamente um descritor, anexado aos primeiros bytes dessa resposta. Se `sendmsg` transferir só parte do payload, prossiga sem repetir SCM_RIGHTS. O receptor usa `recvmsg` desde o primeiro byte, acumula o restante até LF e rejeita MSG_CTRUNC, quantidade diferente de um, tamanho ou versão inválidos, fechando todos os descritores recebidos. Não presuma correspondência entre `send` e `recv` em SOCK_STREAM.

Cada operação usa deadline monotônico de dois segundos; retomadas após EINTR e I/O parcial preservam o deadline original. A aquisição pode usar `pthread_mutex_clocklock(CLOCK_MONOTONIC, ...)`. Não reinicie o prazo a cada byte. EOWNERDEAD invalida a sessão com STATE; não é autorização para recuperar estado e continuar. O processo que recebeu ownership deve liberar o mutex sem chamar `pthread_mutex_consistent`, tornando-o irrecuperável. Encerre e aguarde todos os usuários antes de desmontar a região; não destrua um mutex ocupado ou ainda acessível. Um objeto irrecuperável sem usuários pode ser descartado com a região sem tentar recuperá-lo para reutilização.

As três decisões acima e a regra de sequência máxima foram aprovadas pelo responsável nesta preparação: ao esperar UINT64_MAX, somente STOP é aceito; outro comando produz STATE, preserva o estado e invalida. Não há wrap. A aprovação está registrada também no enunciado.

## Verificação funcional e falhas controladas

`tests/peer.py` é um adversário de teste iniciado pelo target. Exercita HELLO fragmentado e token errado seguido de nova tentativa, descritor real, comandos, valor inválido, sequência repetida, limite de linha, mil snapshots com worker, timeout de fragmento, morte do dono do mutex e bloqueio por mais de dois segundos. `region-probe` faz todas as leituras/mutações sob o mutex; os modos de corrupção/injeção só pertencem aos fixtures cooperativos de teste. Esses modos não representam comandos autorizados do protocolo.

O caso `generation-max` coloca geração UINT64_MAX sob mutex e comprova STATE sem modificação. Para alcançar sequência máxima sem executar 2^64 pedidos, ofereça um **build de teste separado**, compilado com `-DOX_TEST_HOOKS`, que aceite `--test-sequence-max`. Apenas esse build inicializa a próxima sequência em UINT64_MAX. O build normal deve recusar essa opção.

```sh
python3 tests/check.py --test-hooks /caminho/target-de-teste
python3 tests/observer.py /caminho/observer
/caminho/target --observer /caminho/observer
/caminho/target --observer /caminho/observer --test-worker
```

O último par é o controle positivo necessário para o observador. A suíte independente do observador envia HELLO sem fd, com dois fds, tamanho incorreto e resposta incorreta; rejeitar tudo sem também passar a sessão válida não é aprovação. A suíte também prepara versão incorreta com mutex válido e um envio de 32 descritores para exercitar excesso/truncamento de ancillary. O supervisor exige testemunho por caso, com nonce novo, escrito pelo peer somente após todas as verificações e fechamento; um target que só retorna 0 é rejeitado. Dez sessões do servidor devem remover seus sockets/diretórios. Revise também a contagem de descritores e usuários, que não é provada somente pela ausência de nomes no filesystem.

Logs do observador podem registrar sequência, geração respondida e geração posterior. Não cole tokens nem bytes do mutex nas evidências. O modelo de ameaças e a revisão de todos os acessos, fechamento e exclusão mútua continuam obrigatórios.

## Origem, revisões e licenças

Código C/Python e receitas originais preparados com assistência de IA: MIT. Fixtures e dados: CC0 1.0; texto: CC BY 4.0. Nenhuma implementação de terceiros foi copiada.

Leitura de produção fixada em [Linux v6.12, net/unix/af_unix.c](https://raw.githubusercontent.com/torvalds/linux/v6.12/net/unix/af_unix.c), GPL-2.0-or-later, consultada em 25/10/2026, somente vinculada. Observe `unix_stream_connect` e associação de credenciais. Pergunta: por que os locks internos do socket não protegem o contador compartilhado da aplicação? Consulte também [robust mutex](https://git.kernel.org/pub/scm/docs/man-pages/man-pages.git/plain/man/man3/pthread_mutexattr_setrobust.3?h=man-pages-6.16) para ownership após EOWNERDEAD.

## Evidências e pendências

Registro local (registro histórico retirado deste repositório): sessões reais, cinco mutantes e limites de cobertura. A revisão independente encontrou lacunas nos testes. A resposta à revisão registra os controles acrescentados; a auditoria de descritores, morte de peer e soluções dos participantes continua necessária. O piloto não foi executado e foi dispensado pelo responsável. Estimativa curricular provisória: 14–20 horas.

## Roteiro de interrupção e registros sem segredos

Execute `python3 tests/check.py /caminho/target`: `disconnect` fecha o peer, `owner-death` termina o dono do mutex e `lock-timeout` mantém o mutex ocupado por três segundos. Os casos devem terminar sem espera infinita, com conexão encerrada após erro fatal e sem socket nem diretório residual sob `TMPDIR`. O teste confere modos 0700/0600 e procura token nos argumentos e ambiente dos dois processos. O supervisor também rejeita token hexadecimal em stdout/stderr usando o digest comunicado pelo peer; os diagnósticos ocultam sequências hexadecimais de 64 caracteres. Revise logs adicionais antes de arquivá-los.

Um registro permitido, ilustrativo, é `{"seq":1,"response_generation":0,"later_generation":0}`. Os logs da suíte registram somente caso e resultado; nunca copie token nem conteúdo do mutex. A checagem do timeout aceita 1,8–2,8 s para acomodar medição e escalonamento; uma implementação com prazo de 1,2 s é rejeitada.

O servidor adversarial mantém a conexão aberta e inicializa região válida em todos os casos que não testam versão ou tamanho. O adaptador `fd_audit.c` verifica fechamento de descritores recebidos no retorno normal de executáveis dinâmicos glibc; syscall direta de saída ou outro runtime exige auditor equivalente e revisão manual. Rejeitar todos os HELLO não substitui o controle positivo com target e observer reais.
