# Auditoria do suporte no_std

## Stub e ABI

A referência é System V AMD64 ABI 1.0, PDF datado de 12/03/2025, seções 3.2.2 e 3.4.1.
PDF oficial consultado: https://gitlab.com/x86-psABIs/x86-64-ABI/-/jobs/artifacts/master/raw/x86-64-ABI/abi.pdf?job=build
SHA-256: `19f346cc723dbeb6ad80494614291f4e85aba3caca48dcfd537d33f82af6d6ac`.
A URL é móvel; o hash identifica exatamente a edição renderizada auditada.
O commit consultado da árvore foi `e1ce098331da5dbd66e1ffc74162380bcc213236`; não se atribui esse commit ao PDF de artefatos.
O download do fonte nessa revisão retornou HTTP 403. A auditoria usou o PDF renderizado; fonte fixado permanece pendente.

`_start` recebe a stack inicial do processo. `and rsp,-16` estabelece alinhamento antes do `call`.
O `call` empilha oito bytes; `club_main` recebe `rsp mod 16 = 8`.
O stub não usa argumentos ou ambiente. Zera `ebp` e limpa DF. `club_main` não retorna; `ud2` detecta retorno indevido.
`tests/stack.S` é um cliente independente: verifica alinhamento e DF antes de terminar por syscall.
A inspeção do disassembly real está no registro de evidências do repositório.

## Rotinas de memória

`memory.S` fornece implementações reais de `memcpy`, `memmove`, `memset`, `memcmp`, `bcmp` e `strlen`.
`memmove` escolhe direção e restaura DF depois da cópia regressiva. Nenhuma rotina modifica registradores callee-saved.
Comprimento zero não acessa ponteiros nas cinco rotinas com comprimento. `strlen` exige string válida terminada em NUL.
`memcpy` exige regiões sem sobreposição; `memcmp` compara bytes sem sinal.
Os testes C usam bytes literais, sobreposição nas duas direções, retornos e casos vazios, com `-fno-builtin`.
Não há funções vazias para satisfazer o linker.

## Linking e inventário

O build usa Rust 1.98.1, target GNU Linux x86-64, `panic=abort`, `opt-level=3`, `relocation-model=static` e LTO fat.
O driver é GCC 16.2.1. Nesta toolchain, o driver Rust selecionou rust-lld/LLVM 22.1.8.
As flags adicionais são `-nostdlib -static -no-pie -Wl,-e,_start -Wl,-z,noexecstack`.
O layout de seções é o padrão do linker; não há linker script próprio.

LTO foi necessário nesta configuração para remover a referência não utilizada a `rust_eh_personality` do core pré-compilado.
Sem LTO, o caminho de panic apresentou erro de linking. Não se ignorou símbolo ausente e não se criou personality fictícia.
Entram no link `core` e `compiler_builtins` da toolchain fixada. Não entram `std`, `alloc` ou libc.
No artefato mínimo validado, a coleta de seções removeu as rotinas de memória não usadas.
O inventário real contém `_start`, `club_main`, política de escrita e auxiliares de panic/indexação de `core`.
Essas observações não garantem o mesmo inventário após mudanças na solução; repita `nm` e `readelf`.

## Wrappers do participante

Syscall Linux x86-64: número em `rax`; argumentos em `rdi`, `rsi`, `rdx`; retorno em `rax`; `rcx` e `r11` são alterados.
`write` usa número 1; `exit`, 60. O wrapper de escrita precisa declarar os efeitos de memória corretamente.
Não marque essa syscall como `nomem`, `pure` ou `readonly`. A validade do slice precisa durar até o retorno.
O suporte não implementa os wrappers do participante. A referência reservada os executou nos três caminhos de término.

## Limites confirmados na revisão de 25/10/2026

O teste `stack.S` observa alinhamento e DF na entrada de `club_main`. Ele não demonstra isoladamente a necessidade de `and rsp,-16` ou `cld`: o kernel já pode fornecer o estado esperado. A preservação do stub fornecido e sua revisão continuam obrigatórias.

A ausência de símbolos de alocação no artefato é somente uma triagem. Revise fontes, dependências e disassembly para a proibição de `alloc`/allocator global e os efeitos de memória dos wrappers. O mutante com `nomem` pode passar nos testes finitos.

A cópia histórica do PDF foi arquivada em armazenamento privado durável durante a resposta à revisão, com o hash acima. Não se redistribui o PDF neste pacote: a licença e o fonte correspondente ainda não foram obtidos. Em 25/10/2026, o fonte correto `x86-64-ABI/low-level-sys-info.tex` na revisão fixada foi consultado pela ferramenta de navegação. O download direto com curl retornou HTTP 403, e a consulta ao COPYING falhou. Um caminho sem o prefixo `x86-64-ABI/` retornou 404 e não é a referência canônica. Esta pendência bloqueia a publicação e não fica resolvida apenas por fixar uma URL.

## Instrumentação da escrita na segunda revisão

O tracer altera `rdx` somente entre a parada de entrada e a execução de `write(1, …)`. Depois da parada de saída, restaura o valor de entrada e mantém `rax`, retornado pelo kernel. Sem essa restauração, código Rust otimizado poderia reutilizar uma contagem alterada e encerrar o laço prematuramente, mesmo estando conforme à ABI original. A sonda do clube compara o registrador depois da syscall; um tracer de controle sem restauração foi rejeitado.

A instrumentação não altera código, nomes de módulos ou interface do candidato. Ela não simula o retorno de escrita nem fabrica bytes. O kernel grava cada byte no descritor real. O limite de um byte exercita avanços repetidos até o sucesso; não demonstra o tratamento de todos os sinais ou erros de I/O. Esses casos continuam cobertos pelos demais testes e pela revisão.
