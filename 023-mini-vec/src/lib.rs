// SPDX-License-Identifier: MIT
#![allow(dead_code, unused_variables)]
pub mod support;
use std::{alloc::Layout, marker::PhantomData, ptr::NonNull};
pub use support::Allocator;
#[derive(Debug, PartialEq, Eq)]
pub enum CreateError {
    UnsupportedZst,
}
#[derive(Debug, PartialEq, Eq)]
pub enum PushReason {
    CapacityOverflow,
    AllocFailed,
}
#[derive(Debug)]
pub struct PushError<T> {
    pub reason: PushReason,
    pub value: T,
}
pub struct MiniVec<T> {
    ptr: NonNull<T>,
    len: usize,
    cap: usize,
    allocator: Allocator,
    owner: PhantomData<T>,
}
/// Pure layout boundary: must reject invalid arrays without calling the allocator.
pub fn layout_for<T>(capacity: usize) -> Result<Layout, PushReason> {
    todo!("participant: layout")
}
impl<T> MiniVec<T> {
    pub fn new() -> Result<Self, CreateError> {
        // participant: rejeite ZST antes de criar o allocator padrão.
        Self::with_allocator(Allocator::default())
    }
    pub fn with_allocator(allocator: Allocator) -> Result<Self, CreateError> {
        todo!("participant: new")
    }
    pub fn push(&mut self, value: T) -> Result<(), PushError<T>> {
        todo!("participant: push")
    }
    pub fn pop(&mut self) -> Option<T> {
        todo!("participant: pop")
    }
    pub fn get(&self, index: usize) -> Option<&T> {
        todo!("participant: get")
    }
    pub fn len(&self) -> usize {
        todo!("participant: len")
    }
    pub fn capacity(&self) -> usize {
        todo!("participant: capacity")
    }
}
impl<T> Drop for MiniVec<T> {
    fn drop(&mut self) { /* participant: elements and raw buffer, including unwind */
    }
}
