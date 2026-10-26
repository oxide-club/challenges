/* SPDX-License-Identifier: MIT */
/* SIGTRAP do próprio alvo, sem syscall antes do trap. */
.global _start
.text
_start:
    int3
    mov $95, %edi
    mov $60, %eax
    syscall
.section .note.GNU-stack,"",@progbits
