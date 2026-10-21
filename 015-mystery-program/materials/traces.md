# Observações do alvo

| stdin hex | stdout hex |
|---|---|
| (vazio) | (vazio) |
| 00 | 5a |
| 000000 | 5c5b5a |
| 414243 | 1b191b |
| 0001020304050607 | 646264625c5a5c5a |

Validação separada: consulte o binário com um impulso em cada posição e registre os resultados.

## Disassembly do binário distribuído

O ELF distribuído é PIE e foi removido de símbolos locais: `nm mystery-linux-x86_64` informa `no symbols`. O nome `main` aparece na listagem `mystery.asm`, produzida antes dessa remoção, mas não está disponível para o debugger do binário distribuído.

No diretório `materials`, esta consulta estática funciona sem executar o alvo:

```sh
gdb -nx -q -batch -iex 'set debuginfod enabled off' \
  -ex 'set disassembly-flavor intel' \
  -ex 'disassemble 0x1288,0x135a' ./mystery-linux-x86_64
```

O intervalo corresponde ao corpo identificado como `main` na listagem fornecida. Antes da execução, GDB usa os endereços virtuais do ELF; ASLR não participa desta consulta estática.

## Breakpoint com ASLR habilitado

```sh
gdb -nx -q ./mystery-linux-x86_64
```

No GDB:

```gdb
set debuginfod enabled off
set disable-randomization off
set disassembly-flavor intel
starti
info files
```

`starti` pode parar primeiro no carregador dinâmico. Em `info files`, copie o valor de `Entry point` do executável (não o PC do carregador). Por exemplo, se aparecer `Entry point: 0x559c075870a0`:

```gdb
set $base = 0x559c075870a0 - 0x10a0
break *($base + 0x1288)
continue
x/6i $pc
print/x $pc - $base
```

O último comando deve mostrar `0x1288`. Substitua o endereço do exemplo pelo observado em sua execução. O ponto de entrada original do ELF é `0x10a0`; subtraí-lo calcula a base PIE atual. Recalcule a base após cada nova execução, pois ASLR pode mudá-la. Para não copiar o endereço, em um GDB com Python, use esta linha logo após `starti`:

```gdb
python import re; gdb.execute('set $base = ' + re.search(r'Entry point: (0x[0-9a-f]+)', gdb.execute('info files', to_string=True))[1] + ' - 0x10a0')
```

A consulta estática e o breakpoint com ASLR foram conferidos contra o binário distribuído. Para observar a transformação com dados, crie um arquivo e use `starti < entrada.bin`; depois aplique o mesmo cálculo e breakpoint. Os offsets são específicos deste artefato: ao reconstruir com outro compilador, consulte novamente o cabeçalho ELF e a listagem.
