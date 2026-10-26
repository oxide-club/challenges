// SPDX-License-Identifier: MIT
use mini_refcell::*;
fn accepts<T: Sized>() {}
fn main() {
    accepts::<MiniRefCell<i32>>();
}
