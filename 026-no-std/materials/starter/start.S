# SPDX-License-Identifier: MIT
# GNU assembler, sintaxe Intel. _start recebe a stack do processo.
.intel_syntax noprefix
.section .text.start,"ax",@progbits
.global _start
.type _start,@function
_start:
    xor ebp, ebp
    cld
    and rsp, -16
    call club_main
    ud2
.size _start, .-_start
.section .note.GNU-stack,"",@progbits
