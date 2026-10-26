# SPDX-License-Identifier: MIT. Cliente da ABI do stub, sem runtime C.
.intel_syntax noprefix
.text
.global club_main
.type club_main,@function
club_main:
    mov rax, rsp
    and eax, 15
    cmp eax, 8
    jne .Lbad
    pushfq
    pop rax
    test eax, 0x400
    jne .Lbad
    xor edi, edi
    jmp .Lexit
.Lbad:
    mov edi, 1
.Lexit:
    mov eax, 60
    syscall
    ud2
.section .note.GNU-stack,"",@progbits
