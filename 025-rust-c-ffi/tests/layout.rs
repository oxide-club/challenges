// SPDX-License-Identifier: MIT
extern crate oxide_ffi;
use oxide_ffi::OcResult;
fn main() {
    assert_eq!(std::mem::size_of::<OcResult>(), 24);
    assert_eq!(std::mem::align_of::<OcResult>(), 8);
    assert_eq!(std::mem::offset_of!(OcResult, status), 0);
    assert_eq!(std::mem::offset_of!(OcResult, written), 8);
    assert_eq!(std::mem::offset_of!(OcResult, required), 16);
    println!("Layout Rust: 24/8/0/8/16");
}
