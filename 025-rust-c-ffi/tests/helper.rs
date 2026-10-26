// SPDX-License-Identifier: MIT
extern "C" {
    fn oc_rotate(value: u8) -> u8;
}
fn main() {
    for (value, expected) in [(0, 0), (1, 2), (0x80, 1), (0xff, 0xff), (0x5a, 0xb4)] {
        // SAFETY: helper C aceita qualquer byte e não retém memória.
        assert_eq!(unsafe { oc_rotate(value) }, expected);
    }
    println!("Cliente Rust → helper C: OK");
}
