# Investigar alinhamento e invariantes

Este roteiro aprofunda o diagrama e a justificativa já pedidos no desafio.
Use sua implementação e o adaptador existentes; nenhuma função adicional é
necessária. Os offsets abaixo são relativos à base emprestada, alinhada a 16.

## Prever, executar e localizar a divergência

Antes de executar o exemplo de `index.md`, monte uma tabela com pedido,
`used` anterior, padding, offset entregue e `used` posterior. Distinga os
bytes úteis dos bytes de preenchimento, inclusive os que antecedem a terceira
alocação. Compare sua previsão com os comandos `a` e `s` do adaptador.

Como contraste, numa região de 16 bytes, reserve `(1,1)` e peça `(9,8)`.
Há quinze bytes restantes, mas o segundo pedido precisa de sete bytes de
padding mais nove úteis: ele falha e `used` continua em um. Um pedido seguinte
`(8,8)` cabe exatamente, no offset oito. Por que olhar somente `n` e a
capacidade restante daria a resposta errada? Registre o primeiro pedido que
divergir da previsão, com o estado antes e depois.

## Justificar antes de somar

Para cada solicitação válida, parta de `used <= capacity`. Calcule o padding
necessário (entre zero e `alignment - 1`) e verifique primeiro se ele cabe em
`capacity - used`. Só então forme o offset. Verifique se `n` cabe em
`capacity - offset` antes de calcular o novo `used` ou formar o ponteiro.
Explique por que essas subtrações são válidas e por que testar a soma depois
de um wraparound não recupera o valor original. Confirme com `o` que um pedido
de `SIZE_MAX` falha sem consumir espaço.

O novo trecho começa em um offset pelo menos igual ao `used` anterior e termina
no novo `used`, que não ultrapassa a capacidade. Relacione esses fatos à
não sobreposição dos blocos vivos. O teste de alguns offsets não substitui
esse argumento sobre todas as solicitações válidas.

## Separar endereço, tipo e tempo de vida

Alinhar o offset só alinha o endereço porque a base já atende a todos os
alinhamentos aceitos. Aqui são 1, 2, 4, 8 e 16; não substitua essa lista por
`_Alignof(max_align_t)`. Se consultar `sizeof(long double)` e
`_Alignof(long double)` em seu ambiente, preveja o padding após um byte e
verifique primeiro se o alinhamento do tipo pertence à lista aceita. Esses
valores do host não mudam o contrato.

Alinhamento não garante, por si só, que qualquer acesso por tipo seja válido.
O adaptador oferece armazenamento de bytes: inspecione offsets, endereços e
bytes, sem convertê-lo em objetos arbitrários para testar o alinhamento.
O teste direto da API já verifica endereços reais.

Após `r`, compare uma nova sequência de alocações com a previsão a partir de
zero. Não leia ponteiros antigos para tentar provar a invalidação: ela é uma
regra de uso da arena, mesmo que os bytes permaneçam e um sanitizador não
acuse erro. Reset não libera a região do chamador e não precisa apagá-la.

Para quem vem do laboratório 004, o [guia de migração](../../docs/labs-migration.md)
explica como reaproveitar implementação, diagrama e evidências.
