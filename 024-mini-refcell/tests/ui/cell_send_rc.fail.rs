// SPDX-License-Identifier: MIT
use mini_refcell::*;
use std::rc::Rc;
fn accepts<T: Send>() {}
fn main() {
    accepts::<MiniRefCell<Rc<i32>>>();
}
