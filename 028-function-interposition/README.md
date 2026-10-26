# 028-function-interposition — guia local

Pacote tecnicamente validado; saída de rascunho autorizada pelo responsável, com dispensa do piloto. Leia o [contrato](index.md). A aplicação, `libcalc.so` e `libtrace.so` são trabalho do participante: os três arquivos em `starter/` compilam, mas retornam uma falha intencional.

## Ambiente e build

Linux x86-64, ELF, glibc, GCC 16.2.1, Python 3 e binutils. O pacote usa C11, `-O0 -g -fno-lto`, `-fPIC` nas bibliotecas, `-rdynamic` na aplicação e rpath relativo `$ORIGIN`. Não use executáveis privilegiados.

A partir deste diretório, numa cópia própria:

```sh
make all
python3 tests/check.py --prepare
make check
```

`all` e `--prepare` devem terminar com 0; `make check` deve falhar enquanto `calc.c` não implementar a API. O erro inicial identifica o caso `positive`, retorno −1 e `ENOSYS`. Complete `starter/calc.c`, `starter/trace.c` e `starter/app.c`. A verificação não fornece a implementação dessas tarefas.

## Protocolo auxiliar

`materials/calc.h` fixa `int ox_trace_sink(const char *, size_t)`, exportado pelo cliente e resolvido após a função real. O callback recebe exatamente um objeto JSON completo com LF, sem NUL contado. Retorna 0 ou −1; pode modificar `errno` e reentrar uma vez. O wrapper deve delimitar reentrancy antes de chamar o sink. O callback de teste serializa as escritas; nenhuma ordem global é exigida.

JSON: `call_id` inteiro positivo único na execução; `thread_id` inteiro positivo, TID Linux da thread chamadora; `a`, `b`, `return`, `errno_before`, `errno_after` inteiros; `value` inteiro no sucesso e `null` no erro. Campos adicionais são permitidos. As linhas vão para stderr via sink; stdout pertence aos resultados da aplicação. O consumidor em `tests/test.py` interpreta JSON e compara valores, contagem e IDs. Não compara texto JSON literal nem ordem de threads.

`materials/cases.json` contém seis casos com sentinela inicial de saída 123. Os errno numéricos 22, 33 e 34 são da ABI Linux fixada; `NULL` tem precedência. O cliente independente repete esses casos em quatro threads, mil chamadas em cada uma, depois de seis chamadas iniciais.

## Executar e verificar

```sh
./build/app
LD_PRELOAD="$PWD/build/libtrace.so" ./build/app
LD_PRELOAD="$PWD/build/libtrace.so" ./build/direct
readelf -Ws build/libcalc.so
readelf -Ws build/app
objdump -d build/direct
python3 tests/check.py build
```

`build/direct` incorpora `starter/calc.c` no executável. Deve preservar a saída da aplicação sem produzir eventos do wrapper. O teste também carrega o wrapper sem definição posterior de `calc_div`: exige status 125 e diagnóstico. O substituto opaco `tests/opaque.c` não implementa divisão; seu contador independente detecta delegação omitida ou duplicada.

A suíte compila seu próprio cliente para exercitar as bibliotecas. Isso não dispensa entregar a aplicação, mapa de símbolos e explicações. As fontes, saídas e contagens dos testes não provam ausência universal de data races: revise inicialização, publicação e lifetime do sink. Referências corretas e mutantes de preparação ficam fora da distribuição.

## Origem, revisão e licenças

Fontes e scripts novos: implementação original preparada para o Oxide Club com assistência de IA, MIT. Casos originais: CC0 1.0. Texto: CC BY 4.0. Não houve cópia de implementações de terceiros.

Leitura consultada em 25/10/2026: [patch glibc 68608ef426b88e73e0e3178497bcfe34dd8a66ef](https://sourceware.org/pipermail/glibc-cvs/2020q1/068675.html), que separa o processamento de símbolos e a identificação do chamador; código externo LGPL-2.1-or-later, apenas vinculado. Pergunta: por que a identidade do objeto chamador muda o significado de `RTLD_NEXT`? O loader completo possui requisitos ausentes neste exercício.

## Evidências e pendências

 Foram executados build, referência privada e seis mutantes relevantes. Revisão independente executada; piloto dispensado pelo responsável, sem execução; estimativa curricular provisória: 10–16 horas.

A variante direta é executada primeiro sem `LD_PRELOAD`, para conferir a saída funcional, e depois com o wrapper. No segundo caso, aceita-se status 0 com a mesma saída e nenhum evento, ou status 125 com diagnóstico de resolução em constructor. Uma cópia da aplicação dinâmica como `direct` emite eventos e é rejeitada. O cliente independente da suíte usa `DT_RUNPATH` explicitamente para permitir substituição opaca por `LD_LIBRARY_PATH`; isso não impõe `DT_RUNPATH` à aplicação entregue. A suíte confirma que cada chamada ao substituto opaco conserva `errno = 42` na baseline antes de conferir a delegação. O mapa de símbolos e a explicação dos cenários exigidos continuam sujeitos à revisão humana.
