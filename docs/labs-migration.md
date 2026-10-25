# Dos laboratórios de arena e VM aos desafios

Os percursos de implementação dos laboratórios **004 — Alocação de Memória**
e **009 — Máquinas Virtuais** foram consolidados, respectivamente, em
[017 — Arena](../017-arena/index.md) e [021 — Bytecode](../021-bytecode/index.md).
Os materiais anteriores permanecem arquivados no repositório `labs`, com
seus contratos históricos. Os números dos desafios não mudam.

## Se você já começou ou concluiu um laboratório

Não é necessário concluir uma segunda implementação para aproveitar esse
percurso. Preserve seu código, testes e relato anteriores e identifique a
variante utilizada. Reaproveite o diagrama da arena ou o trace da VM; acrescente
uma explicação das diferenças abaixo e das invariantes que continuam válidas.
Se ainda está no começo, pode continuar o material histórico ou escolher o
contrato atual, sem completar ambos.

Uma solução histórica não é automaticamente compatível com o runner do
desafio. Só se quiser submetê-la a esse runner, adapte o mesmo projeto ao
contrato canônico e execute os testes do README correspondente. Os testes
históricos continuam evidências da variante histórica, não da API atual.

## Arena: algoritmo compartilhado, ownership diferente

| Aspecto | Laboratório 004 arquivado | Desafio 017 |
| --- | --- | --- |
| Região | Obtida por `malloc` na inicialização | Emprestada pelo chamador, base alinhada a 16 |
| Alinhamentos | Potências de dois até `_Alignof(max_align_t)` | Somente 1, 2, 4, 8 e 16 |
| Inicialização | Pode falhar; capacidade zero é rejeitada | Recebe região válida e capacidade; zero é aceito |
| Destruição | `arena_destroy` libera e zera estado | Não há destruição na API; a memória pertence ao chamador |
| Reset | Invalida referências e conserva a região | Mesma regra; não libera nem precisa apagar bytes |

Reaproveite o cálculo de padding, a verificação de espaço antes das somas e
a demonstração de não sobreposição. Para adaptar ao desafio, use seu `api.h`
e adaptador; remova a aquisição/liberação de memória da arena e reveja os
limites aceitos. Não adicione `arena_destroy` nem testes de falha de `malloc`
aos requisitos do desafio. O [roteiro de invariantes](../017-arena/materials/investigation.md)
ajuda a revisar o diagrama existente sem montar outra arena.

A extensão opcional de pool corresponde ao
[018 — Free-list](../018-free-list/index.md). Quem já a fez pode comparar
first-fit, split e coalescência no próprio mapa: no laboratório, metadados
consomem capacidade e o alinhamento segue `max_align_t`; no desafio, os
metadados ficam fora da região, em até 1024 descritores, e os blocos têm
alinhamento de oito bytes. Não transplante a contabilidade de capacidade.
Essa extensão continua opcional para concluir o percurso de arena.

## VM: transições compartilhadas, representação diferente

| Aspecto | Laboratório 009 arquivado | Desafio 021 |
| --- | --- | --- |
| Programa e PC | Texto; índice de instrução | Binário; offset em bytes |
| Estado | Pilha de 32; oito variáveis | Pilha de 64; 16 posições de memória |
| ISA | Inclui POP | Inclui MUL e DUP; não inclui POP |
| HALT | Pode deixar qualquer quantidade na pilha | Exige exatamente um valor e imprime-o com LF |
| Orçamento | Parâmetro de `run`, padrão 1000 | Fixo em 1000, incluindo HALT |
| Resultado | Estado, códigos de erro e trace em estrutura retornada | Resultado em `stdout`; falha por status e diagnóstico em `stderr` |
| Trace fornecido | Pilha antes da tentativa de instrução | Pilha e memória depois da instrução |

Reaproveite a separação entre validação e execução, a ordem dos operandos,
a análise dos saltos condicionais e a proteção contra overflow. Ao adaptar,
recalcule fronteiras e alvos após codificar instruções de comprimentos
variáveis: um índice textual não é um offset binário. Valide inclusive código
inalcançável. Não importe a API `run`, os códigos de erro, a atomicidade do
estado retornado ou o formato JSON como novas obrigações do desafio.

Use o [trace comentado](../021-bytecode/materials/trace.md) para relacionar
previsão, primeiro estado divergente e orçamento. Você pode fazer essa
comparação com seu trace histórico e explicar a mudança de unidade do PC,
sem escrever outro interpretador. A intervenção opcional no salto aprofunda
a distinção entre programa bem formado e execução que termina.
