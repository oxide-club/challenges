// SPDX-License-Identifier: MIT
// Integração isolada: observa o allocator global, não o contador do adaptador.
use std::alloc::{GlobalAlloc, Layout, System};
use std::cell::Cell;

thread_local! {
    // Constante, sem alocação e sem destructor de TLS. Conta somente a thread do teste.
    static ATTEMPTS: Cell<Option<usize>> = const { Cell::new(None) };
}
struct ObservedSystem;
fn record_attempt() {
    let _ = ATTEMPTS.try_with(|count| {
        if let Some(n) = count.get() {
            count.set(Some(n.saturating_add(1)));
        }
    });
}
unsafe impl GlobalAlloc for ObservedSystem {
    unsafe fn alloc(&self, layout: Layout) -> *mut u8 {
        record_attempt();
        // SAFETY: mesmos argumentos e contrato recebidos de GlobalAlloc.
        unsafe { System.alloc(layout) }
    }
    unsafe fn alloc_zeroed(&self, layout: Layout) -> *mut u8 {
        record_attempt();
        // SAFETY: mesmos argumentos e contrato recebidos de GlobalAlloc.
        unsafe { System.alloc_zeroed(layout) }
    }
    unsafe fn realloc(&self, ptr: *mut u8, layout: Layout, size: usize) -> *mut u8 {
        record_attempt();
        // SAFETY: ponteiro, layout e novo tamanho delegados sem alteração.
        unsafe { System.realloc(ptr, layout, size) }
    }
    unsafe fn dealloc(&self, ptr: *mut u8, layout: Layout) {
        // SAFETY: corresponde à alocação System; contador não altera ownership.
        unsafe { System.dealloc(ptr, layout) }
    }
}
#[global_allocator]
static ALLOCATOR: ObservedSystem = ObservedSystem;

#[test]
fn zst_rejection_does_not_allocate_bookkeeping_or_buffer() {
    ATTEMPTS.with(|n| n.set(Some(0)));
    let result = mini_vec::MiniVec::<()>::new();
    let attempts = ATTEMPTS.with(|n| n.replace(None).unwrap());
    assert!(matches!(result, Err(mini_vec::CreateError::UnsupportedZst)));
    assert_eq!(
        attempts, 0,
        "rejeite ZST antes de criar o adaptador alocante"
    );
}
