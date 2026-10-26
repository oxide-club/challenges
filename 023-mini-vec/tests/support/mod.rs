// SPDX-License-Identifier: MIT
use std::cell::RefCell;
/// Borrows external storage; skipped destructors do not leak owned allocations.
#[derive(Debug)]
pub struct DropSpy<'a> {
    pub id: u8,
    pub events: &'a RefCell<Vec<u8>>,
}
impl Drop for DropSpy<'_> {
    fn drop(&mut self) {
        self.events.borrow_mut().push(self.id)
    }
}
#[derive(Debug)]
pub struct DropBomb<'a> {
    pub id: u8,
    pub explode: bool,
    pub events: &'a RefCell<Vec<u8>>,
}
impl Drop for DropBomb<'_> {
    fn drop(&mut self) {
        self.events.borrow_mut().push(self.id);
        if self.explode {
            panic!("controlled DropBomb")
        }
    }
}
