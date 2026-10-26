// SPDX-License-Identifier: MIT
use mini_refcell::*;
fn accepts<T: std::ops::Deref<Target = i32>>() {}
fn main() {
    accepts::<MiniRefMut<'static, i32>>();
}
