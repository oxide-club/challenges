// SPDX-License-Identifier: MIT
#![no_std]
#![no_main]
#![allow(bad_asm_style, dead_code)]
mod policy;
use policy::WriteError;
core::arch::global_asm!(include_str!("start.S"), options(raw));
core::arch::global_asm!(include_str!("memory.S"), options(raw));
/// # Safety
/// ptr deve designar len bytes legíveis durante toda a syscall.
pub unsafe fn raw_write(_fd: i32, _ptr: *const u8, _len: usize) -> isize {
    -38 // TODO: wrapper syscall; ENOSYS mantém o starter determinístico.
}
pub fn raw_exit(_status: u8) -> ! {
    // TODO: syscall exit. UD2 identifica o caminho ainda não implementado.
    unsafe {
        core::arch::asm!("ud2", options(noreturn));
    }
}
pub fn write_all(bytes: &[u8]) -> Result<(), WriteError> {
    policy::write_all_with(bytes, |part| {
        // SAFETY: part permanece válido durante a chamada.
        unsafe { raw_write(1, part.as_ptr(), part.len()) }
    })
}
#[no_mangle]
pub extern "C" fn club_main() -> ! {
    #[cfg(test_panic)]
    panic!("panic controlado antes da saída");
    #[cfg(not(test_panic))]
    {
        // TODO: produza a saída exata e escolha status normal ou 74.
        raw_exit(if write_all(b"").is_ok() { 0 } else { 74 });
    }
}
#[panic_handler]
fn panic(_info: &core::panic::PanicInfo) -> ! {
    raw_exit(101)
}
