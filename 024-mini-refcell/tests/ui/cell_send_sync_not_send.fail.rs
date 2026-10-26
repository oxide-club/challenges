// SPDX-License-Identifier: MIT
use mini_refcell::MiniRefCell;
use std::sync::MutexGuard;
fn accepts<T: Send>() {}
fn main() {
    accepts::<MiniRefCell<MutexGuard<'static, i32>>>();
}
