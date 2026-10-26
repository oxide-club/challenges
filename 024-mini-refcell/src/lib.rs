// SPDX-License-Identifier: MIT
#![allow(dead_code, unused_variables)]
use std::cell::{Cell, UnsafeCell};
use std::ops::{Deref, DerefMut};
#[derive(Debug, PartialEq, Eq)]
pub enum BorrowError {
    WriterActive,
    ReadersActive,
    ReaderLimitReached,
}
pub struct MiniRefCell<T> {
    value: UnsafeCell<T>,
    state: Cell<i16>,
}
pub struct MiniRef<'a, T> {
    cell: &'a MiniRefCell<T>,
}
pub struct MiniRefMut<'a, T> {
    cell: &'a MiniRefCell<T>,
}
impl<T> MiniRefCell<T> {
    pub fn new(value: T) -> Self {
        todo!("participant: new")
    }
    pub fn try_borrow(&self) -> Result<MiniRef<'_, T>, BorrowError> {
        todo!("participant: read acquire")
    }
    pub fn try_borrow_mut(&self) -> Result<MiniRefMut<'_, T>, BorrowError> {
        todo!("participant: write acquire")
    }
}
impl<T> Deref for MiniRef<'_, T> {
    type Target = T;
    fn deref(&self) -> &T {
        todo!("participant: read reference")
    }
}
impl<T> Deref for MiniRefMut<'_, T> {
    type Target = T;
    fn deref(&self) -> &T {
        todo!("participant: write reference")
    }
}
impl<T> DerefMut for MiniRefMut<'_, T> {
    fn deref_mut(&mut self) -> &mut T {
        todo!("participant: exclusive reference")
    }
}
impl<T> Drop for MiniRef<'_, T> {
    fn drop(&mut self) { /* participant: release reader */
    }
}
impl<T> Drop for MiniRefMut<'_, T> {
    fn drop(&mut self) { /* participant: release writer */
    }
}
