use mini_refcell::*;
use std::panic::{catch_unwind, AssertUnwindSafe};
#[test]
fn conflicts_and_recovery() {
    let c = MiniRefCell::new(7);
    let a = c.try_borrow().unwrap();
    let b = c.try_borrow().unwrap();
    assert_eq!((*a, *b), (7, 7));
    assert_eq!(c.try_borrow_mut().err(), Some(BorrowError::ReadersActive));
    drop(a);
    assert_eq!(c.try_borrow_mut().err(), Some(BorrowError::ReadersActive));
    assert_eq!(*b, 7);
    drop(b);
    {
        let mut w = c.try_borrow_mut().unwrap();
        *w = 9;
        assert_eq!(c.try_borrow().err(), Some(BorrowError::WriterActive));
        assert_eq!(c.try_borrow_mut().err(), Some(BorrowError::WriterActive));
    }
    assert_eq!(*c.try_borrow().unwrap(), 9);
}
#[test]
fn reader_limit_preserves_count() {
    let c = MiniRefCell::new(1);
    let mut readers = Vec::new();
    for _ in 0..255 {
        readers.push(c.try_borrow().unwrap());
    }
    for _ in 0..2 {
        assert_eq!(c.try_borrow().err(), Some(BorrowError::ReaderLimitReached));
    }
    assert_eq!(c.try_borrow_mut().err(), Some(BorrowError::ReadersActive));
    readers.pop();
    readers.push(c.try_borrow().unwrap());
    while readers.len() > 1 {
        readers.pop();
        assert_eq!(
            c.try_borrow_mut().err(),
            Some(BorrowError::ReadersActive),
            "leitores vivos: {}",
            readers.len()
        );
    }
    assert_eq!(**readers.first().unwrap(), 1);
    drop(readers);
    assert!(c.try_borrow_mut().is_ok());
}
#[test]
fn unwind_and_early_return() {
    let c = MiniRefCell::new(5);
    fn early(c: &MiniRefCell<i32>) -> Result<(), ()> {
        let _g = c.try_borrow().unwrap();
        Err(())
    }
    assert_eq!(early(&c), Err(()));
    assert!(c.try_borrow_mut().is_ok());
    assert!(catch_unwind(AssertUnwindSafe(|| {
        let _g = c.try_borrow_mut().unwrap();
        panic!("controlled")
    }))
    .is_err());
    assert!(c.try_borrow().is_ok());
    assert!(catch_unwind(AssertUnwindSafe(|| {
        let _g = c.try_borrow().unwrap();
        panic!("controlled")
    }))
    .is_err());
    assert!(c.try_borrow_mut().is_ok());
}
#[test]
fn forgotten_guards_keep_permission_occupied() {
    let c = MiniRefCell::new(1);
    std::mem::forget(c.try_borrow().unwrap());
    assert_eq!(c.try_borrow_mut().err(), Some(BorrowError::ReadersActive));
    assert!(c.try_borrow().is_ok());
    let c = MiniRefCell::new(2);
    std::mem::forget(c.try_borrow_mut().unwrap());
    assert_eq!(c.try_borrow().err(), Some(BorrowError::WriterActive));
    assert_eq!(c.try_borrow_mut().err(), Some(BorrowError::WriterActive));
}
#[test]
fn value_drops_once_even_after_forget() {
    struct Spy<'a>(&'a std::cell::Cell<usize>);
    impl Drop for Spy<'_> {
        fn drop(&mut self) {
            self.0.set(self.0.get() + 1)
        }
    }
    let n = std::cell::Cell::new(0);
    {
        let c = MiniRefCell::new(Spy(&n));
        std::mem::forget(c.try_borrow_mut().unwrap());
    }
    assert_eq!(n.get(), 1);
}
