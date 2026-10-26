// SPDX-License-Identifier: MIT
#![allow(dead_code)]
mod hooks;
#[repr(C)]
pub struct OcResult {
    pub status: i32,
    pub written: usize,
    pub required: usize,
}
pub struct OcContext {
    _private: (),
}
extern "C" {
    pub fn oc_rotate(value: u8) -> u8;
}
/// TODO: documente e implemente as pré-condições do cabeçalho.
#[no_mangle]
pub unsafe extern "C" fn oc_create(_key: u8, out: *mut *mut OcContext) -> i32 {
    if !out.is_null() {
        // SAFETY: o contrato exige um slot válido quando out não é nulo.
        unsafe {
            *out = std::ptr::null_mut();
        }
    }
    1 // TODO: criação e contenção de unwind.
}
/// TODO: libere um contexto vivo exatamente uma vez; NULL não faz nada.
#[no_mangle]
pub unsafe extern "C" fn oc_destroy(_ctx: *mut OcContext) {}
/// TODO: validação, capacidade, helper C, checkpoint capturado e poison.
#[no_mangle]
pub unsafe extern "C" fn oc_transform(
    _ctx: *mut OcContext,
    _src: *const u8,
    _src_len: usize,
    _dst: *mut u8,
    _dst_cap: usize,
) -> OcResult {
    OcResult {
        status: 1,
        written: 0,
        required: 0,
    }
}
