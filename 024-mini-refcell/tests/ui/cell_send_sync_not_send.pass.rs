// SPDX-License-Identifier: MIT
use mini_refcell::MiniRefCell;
use std::sync::MutexGuard;
fn accepts<T: Sized>() {}
fn main() {
    accepts::<MiniRefCell<MutexGuard<'static, i32>>>();
}
