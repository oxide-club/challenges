// SPDX-License-Identifier: MIT
#![forbid(unsafe_code)]
#![allow(dead_code, unused_variables)]
pub mod support;
use std::marker::PhantomData;
pub use support::FaultPlan;
#[derive(Debug)]
pub struct Closed;
#[derive(Debug)]
pub struct Open;
#[derive(Debug)]
pub struct Finalized;
#[derive(Debug)]
pub struct Resource<S> {
    data: Vec<u8>,
    plan: FaultPlan,
    state: PhantomData<S>,
}
#[derive(Debug, PartialEq, Eq)]
pub enum TransitionReason {
    Injected,
}
#[derive(Debug)]
pub struct TransitionError<S> {
    pub reason: TransitionReason,
    pub resource: Resource<S>,
}
#[derive(Debug, PartialEq, Eq)]
pub enum WriteError {
    CapacityExceeded,
    Injected,
}
impl Resource<Closed> {
    pub fn new(plan: FaultPlan) -> Self {
        todo!("participant: new")
    }
    pub fn open(self) -> Result<Resource<Open>, TransitionError<Closed>> {
        todo!("participant: open")
    }
}
impl Resource<Open> {
    pub fn write(&mut self, bytes: &[u8]) -> Result<(), WriteError> {
        todo!("participant: write")
    }
    pub fn finalize(self) -> Result<Resource<Finalized>, TransitionError<Open>> {
        todo!("participant: finalize")
    }
}
impl Resource<Finalized> {
    pub fn bytes(&self) -> &[u8] {
        todo!("participant: bytes")
    }
}
