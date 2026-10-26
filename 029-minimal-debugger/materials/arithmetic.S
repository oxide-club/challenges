/* SPDX-License-Identifier: MIT */
.section .text
.global _start, after_first, after_second, after_third
_start:
    mov $5, %eax
after_first:
    add $3, %eax
after_second:
    mov %rax, %rbx
after_third:
    mov $60, %eax
    mov $7, %edi
    syscall
.section .note.GNU-stack,"",@progbits
