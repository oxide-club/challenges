# SPDX-License-Identifier: MIT
# Rotinas reais do clube; n=0 não acessa os ponteiros. Sem chamadas externas.
.intel_syntax noprefix
.text
.global memcpy
.type memcpy,@function
memcpy:
    mov rax, rdi
    mov rcx, rdx
    rep movsb
    ret
.size memcpy, .-memcpy
.global memmove
.type memmove,@function
memmove:
    mov rax, rdi
    test rdx, rdx
    jz .Ldone
    cmp rdi, rsi
    jbe .Lforward
    lea rdi, [rdi+rdx-1]
    lea rsi, [rsi+rdx-1]
    mov rcx, rdx
    std
    rep movsb
    cld
    ret
.Lforward:
    mov rcx, rdx
    rep movsb
.Ldone:
    ret
.size memmove, .-memmove
.global memset
.type memset,@function
memset:
    mov r8, rdi
    mov eax, esi
    mov rcx, rdx
    rep stosb
    mov rax, r8
    ret
.size memset, .-memset
.global memcmp
.type memcmp,@function
memcmp:
    xor ecx, ecx
.Lcompare:
    cmp rcx, rdx
    je .Lequal
    movzx eax, byte ptr [rdi+rcx]
    movzx r8d, byte ptr [rsi+rcx]
    sub eax, r8d
    jne .Lreturn
    inc rcx
    jmp .Lcompare
.Lequal:
    xor eax, eax
.Lreturn:
    ret
.size memcmp, .-memcmp
.global bcmp
.set bcmp, memcmp
.global strlen
.type strlen,@function
strlen:
    xor eax, eax
.Llength:
    cmp byte ptr [rdi+rax], 0
    je .Lreturn_length
    inc rax
    jmp .Llength
.Lreturn_length:
    ret
.size strlen, .-strlen
.section .note.GNU-stack,"",@progbits
