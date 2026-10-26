# 029-minimal-debugger — guia local

Leia o [contrato](index.md). Os alvos e o controlador incompleto estão disponíveis; a saída de rascunho foi autorizada pelo responsável, com dispensa do piloto. Implemente `starter/oxdbg.c`.

## Ambiente e preparação

Linux x86-64; GCC 16.2.1, binutils, glibc e Python 3. O kernel observado foi `7.2.8-9-omarchy`. O sandbox bloqueou `PTRACE_TRACEME` com EPERM; o mesmo probe passou fora dele. Esse contraste é evidência de restrição do sandbox, não aprovação de uma ferramenta que apenas retorna 77.

```sh
make all
python3 tests/check.py --prepare
./build/probe
readelf -h build/arith-exec
readelf -h build/arith-pie
readelf -l build/arith-pie
objdump -d build/arith-exec
```

O preparo verifica ET_EXEC e ET_DYN sem `PT_INTERP`. O probe verifica filho próprio, TRACEME, sincronização, opções TRACEEXEC/EXITKILL e child reaping. Se falhar, preserve stderr, kernel e política observada; não eleve privilégios do programa nem converta falha funcional em 77. Use um ambiente autorizado compatível.

## Transporte e eventos

Comandos ASCII em stdin, um por linha LF, sem argumentos. EOF equivale a encerramento controlado. stdout contém somente JSON Lines; stderr recebe diagnósticos. O alvo didático não usa stdout.

Cada evento contém `seq` (inteiro consecutivo desde 1), `state`, `cause` e `pid` (0 antes de criar o filho). Causas: `new`, `exec`, `step`, `signal_step`, `signal_delivery`, `regs`, `rejected`, `exit`, `quit`, `eof`, `timeout`, `unsupported_stop`, `unavailable` ou erro específico terminado em `_error`. Uma rejeição mantém o estado e o PID. Eventos internos adicionais podem ser registrados, mantendo a sequência.

Paradas incluem `raw_status`, `signal`, `event` e `siginfo`: `null` quando não disponível, ou objeto com `code` e `signo`. `regs` contém objeto `regs` com `RIP`, `RSP`, `RAX`, `RBX`, `RCX`, `RDX`, `RFLAGS`: strings `0x` seguidas de hexadecimais. Término contém exatamente um entre `exit_code` e `term_signal`. O status do alvo nunca substitui o status da ferramenta.

Os campos `signal` e `term_signal` são inteiros JSON. O status da ferramenta é 0 para encerramento controlado, inclusive quando o alvo termina por sinal; 1 para timeout, `unsupported_stop`, alvo inexistente ou outra falha funcional; 2 para uso inválido; 77 somente para indisponibilidade comprovada, acompanhada de operação, erro e evidência no stderr. Complemento aprovado pelo responsável em 25/10/2026.

A entrada do fixture executa `mov $5,%eax`, `add $3,%eax`, `mov %rax,%rbx`. Depois de cada instrução os predicados são RAX=5, RAX=8, RBX=8; RIP avança entre símbolos do mesmo módulo. Nenhum endereço absoluto é fixado.

A entrega de sinal por `step` pode gerar uma parada interna antes do handler: `signal_step`. O predicado exige step pendente com sinal injetado, evento zero, SIGTRAP e si_code=SIGTRAP (5), conforme `signal_delivered` em [Linux v6.12 kernel/signal.c](https://raw.githubusercontent.com/torvalds/linux/v6.12/kernel/signal.c). Esse caminho chama `ptrace_notify`, não representa novo sinal do alvo; não reinjete. Um SIGTRAP produzido pelo alvo, inclusive `int3` (`SI_KERNEL` no ambiente validado; `TRAP_BRKPT` também reconhecido), permanece `signal_delivery` e deve ser reinjetado. Depois dos predicados conhecidos, códigos positivos não reconhecidos recebem `unsupported_stop`, conforme o enunciado. Classifique primeiro eventos ptrace e traps internos comprovados; não descarte sinais apenas porque `si_code` é positivo. Os fixtures ordinários usam SI_TKILL; a suíte verifica entrega tanto por step quanto por continue.

No kernel observado, dar SINGLESTEP imediatamente após o evento exec produz um trap de saída da syscall com `TRAP_BRKPT`, ainda em `_start`. A preparação privada drenou essa saída com PTRACE_SYSCALL e TRACESYSGOOD antes de expor o estado de entrada. O participante deve identificar a fronteira de exec sem suprimir traps arbitrários nem apresentar esse trap como instrução executada. Registre também paradas internas e sua classificação; essa observação não altera a entrega obrigatória de SIGTRAP do alvo.

## Executar e verificar

```sh
printf 'run\nstep\nregs\nstep\nregs\nstep\nregs\ncontinue\n' | ./build/oxdbg -- ./build/arith-exec
python3 tests/check.py build/oxdbg
```

O starter termina com 1 e diagnóstico de implementação ausente. A referência privada passou os mesmos predicados nos dois ELF, sinais USR1/TRAP/TERM, estados inválidos, EOF, quit, timeout e erro de exec. O executor observa `/proc` para verificar que os filhos registrados não permanecem vivos após a ferramenta terminar.

`build/signals` aceita `usr1`, `trap`, `term`, `unknown-trap`, `group` e `timeout`. Os handlers retornam 7 somente quando chamados uma vez; 91/92 indicam entrega incorreta. O caso `group` é para revisão de `unsupported_stop`. O executor adicional `tests/lifecycle.py` injeta EINTR em `waitpid` com testemunho independente, verifica retry, mata o tracer próprio e recolhe o tracee por subreaper para conferir EXITKILL. O comando `tests/check.py` executa as suítes funcional, de ciclo de vida e de indisponibilidade. A injeção usa LD_PRELOAD em glibc; uma implementação que use syscall direta deve oferecer adaptador equivalente, sem converter ausência da injeção em aprovação.

## Origem, revisões e licenças

Assembly, C, Python e receitas originais preparados para o clube com assistência de IA: MIT; dados de teste: CC0 1.0; textos: CC BY 4.0. Não foram copiadas soluções externas.

[ptrace(2)](https://git.kernel.org/pub/scm/docs/man-pages/man-pages.git/plain/man/man2/ptrace.2?h=man-pages-6.16), consultado em 25/10/2026, orienta a classificação e as opções. A leitura curricular [commit GDB 6a534f85cbdb065a307aa96fbbb670948ee135c8](https://sourceware.org/pipermail/gdb-cvs/2023-November/057012.html) foi conferida em 25/10/2026 no arquivo primário do projeto: `linux_handle_extended_wait` elimina LWPs anteriores ao exec; `threads-after-exec.exp` verifica a lista e o encerramento. O patch é GPL-3.0-or-later e está apenas vinculado. A consulta não executou os testes do GDB. Consulte [fontes e limitações](references.md).

## Evidências e pendências

Registro da preparação (registro histórico retirado deste repositório): probe real, testes e controles negativos. A suíte não aceita um 77 fictício como aprovação. Revisão independente final executada; piloto dispensado pelo responsável, sem execução. Estimativa curricular provisória: 12–18 horas.

`tests/unavailable.py` primeiro exige que o probe funcione, depois instala seccomp num filho para fazer `ptrace` retornar EPERM. O probe confirma o bloqueio antes de exigir 77 e diagnóstico da ferramenta. `tests/check.py` executa os casos funcionais primeiro: uma ferramenta que sempre retorna 77 falha. `unknown-trap` executa `int3` no alvo, deve gerar `signal_delivery` e terminar por SIGTRAP após a reinjeção. Eventos internos adicionais no fim da sessão são permitidos.

## Indisponibilidade verificável

Antes de avaliar o candidato, `tests/check.py` executa o probe fornecido pelo clube. Falha de permissão de `PTRACE_TRACEME` nesse probe produz `NOT_RUN` e status 77; não é falha funcional do candidato nem aprovação. Outros erros do probe retornam 1. O modo `--prepare` continua separado: compila os apoios e confirma o starter incompleto.

Em ambiente disponível, `unavailable.py` confirma que um filtro seccomp que só nega `acct` permite a execução normal. Depois confirma um filtro que nega `ptrace`, observa a tentativa do filho e exige o evento `unavailable` definido no enunciado. O supervisor `tests/notify_ptrace.c` recebe uma notificação do kernel para cada tentativa de `PTRACE_TRACEME` e responde EPERM. Compara PID, PPID e resposta aplicada com o evento JSON do candidato. Essa observação funciona com libc, `syscall` direta e assembly, sem protocolo adicional do participante.

`build/step-trap` executa `int3` enquanto a ferramenta executa `step`; esse sinal do próprio alvo deve ser observado e reinjetado. Em outro caso, o supervisor envia SIGTRAP com `tgkill` ao filho parado, antes do comando `step`, para exercitar também `SI_TKILL` nessa retomada. O alvo sem permissão de execução (`chmod 644`) verifica que `exec` com EACCES produz falha funcional/status 1, nunca indisponibilidade.

## Observação no kernel — terceira revisão

`make all` compila `build/notify-ptrace`. `make check` agora chama `tests/check.py`, incluindo probe, ciclo de vida e indisponibilidade. Execute os comandos na raiz do pacote. O script retorna 77/NOT_RUN se o probe comprovar indisponibilidade; `make` conserva o diagnóstico, mas representa uma receita não zero pelo seu próprio status de erro.

O supervisor instala `SECCOMP_RET_USER_NOTIF` antes de criar o candidato. O filtro é herdado pelo filho didático, e o listener permanece somente no supervisor. O kernel fornece PID e argumentos da tentativa; o supervisor confere o PPID enquanto a chamada está bloqueada, aplica EPERM e registra o testemunho fora de stdout. Não usa `LD_PRELOAD` nem `OX_PTRACE_WITNESS` nesse teste. `ptrace_attempt.c` permanece como apoio histórico, sem uso pelo verificador atual. A injeção separada de EINTR em waitpid continua usando seu adaptador de libc; a mudança não amplia a cobertura dessa outra técnica.

Uma sonda independente precisa produzir uma notificação antes de testar o candidato. A ausência comprovada do mecanismo na preparação do supervisor resulta em 77; erro do instrumento resulta em falha. O supervisor tem prazo de sete segundos, encerra somente o grupo que criou e registra filhos órfãos recolhidos, que causam reprovação. A implementação do participante mantém os mesmos eventos e status do contrato.

A interface de notificação e a herança de filtros seguem a [documentação Linux v6.12 de seccomp](https://www.kernel.org/doc/html/v6.12/userspace-api/seccomp_filter.html#userspace-notification), consultada em 25/10/2026. O código do apoio é original, MIT; a documentação externa foi apenas consultada. Validação local: kernel 7.2.8-9-omarchy, x86-64, GCC 16.2.1, headers Linux disponíveis no host. Não foram executados outros kernels. O mecanismo verifica estas soluções cooperativas e não constitui isolamento contra um candidato hostil.

## Instalação do supervisor

Se as consultas seccomp fixas não estiverem disponíveis (`EINVAL`) ou a instalação de `NEW_LISTENER` encontrar outro listener (`EBUSY`), a suíte registra 77/`NOT_RUN`. Isso não aprova a solução. Outros erros de preparação, como `ENOMEM`, e falhas posteriores à instalação continuam sendo erros do instrumento. Execute `python3 tests/setup_controls.py` neste diretório para conferir essa classificação; `--prepare` também executa esses controles. Os testes de classificação não substituem uma sessão real.

Depois que as consultas de capacidade passam, `EINVAL` ao instalar `SET_MODE_FILTER` é erro do instrumento (125), não indisponibilidade. Essa distinção detecta, por exemplo, um salto inválido no filtro BPF. A suíte converte a falha do instrumento em falha de verificação (1).
