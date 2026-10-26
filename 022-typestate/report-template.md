# Memória técnica

## Contrato

Registre as operações, os estados e a precedência de erros.

## Decisões e invariantes

Relacione cada operação às invariantes que ela preserva. Justifique os campos privados e lifetimes. Quando houver `unsafe`, audite cada bloco e suas pré-condições.

## Falhas e recursos

Explique recuperação, ownership, descarte e unwind quando aplicáveis.

## Verificação

Para cada caso: entrada, esperado, observado, comando, status e evidência. Distinga aprovado, falhou e indisponível (77). Registre as rejeições de compilação e seus controles válidos.

## Ambiente e limitações

Registre versões, target, flags, capacidades ausentes e limites da conclusão. Miri examina as execuções realizadas; não prova soundness geral.
