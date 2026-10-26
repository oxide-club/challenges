// SPDX-License-Identifier: MIT
// Sonda do clube: não contém código do candidato.
#[no_mangle]
pub extern "C" fn club_payload_probe() {
    // A supressão cobre somente a alocação do payload desta classe de panic.
    if let Err(payload) = std::panic::catch_unwind(|| panic!("payload estático da sonda LSan")) {
        std::mem::forget(payload);
    }
}
