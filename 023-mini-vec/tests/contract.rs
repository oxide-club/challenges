use mini_vec::*;
mod support;
use std::cell::RefCell;
use support::*;
#[test]
fn order_growth_and_empty() {
    let allocator = Allocator::default();
    let mut v = MiniVec::with_allocator(allocator.clone()).unwrap();
    assert_eq!((v.len(), v.capacity()), (0, 0));
    assert_eq!(v.get(0), None);
    assert_eq!(v.pop(), None);
    for (n, cap) in [(10, 1), (20, 2), (30, 4), (40, 4), (50, 8)] {
        v.push(n).unwrap();
        assert_eq!(v.capacity(), cap);
    }
    assert_eq!(v.len(), 5);
    for (i, n) in [10, 20, 30, 40, 50].iter().enumerate() {
        assert_eq!(v.get(i), Some(n));
    }
    assert_eq!(v.get(5), None);
    for n in [50, 40, 30, 20, 10] {
        assert_eq!(v.pop(), Some(n));
    }
    assert_eq!(v.pop(), None);
    drop(v);
    let (_, allocated, freed) = allocator.stats();
    assert_eq!(
        allocated, freed,
        "buffer deve ser liberado após todos os pops"
    );
}
#[test]
fn zst_and_layout_overflow() {
    assert!(matches!(
        MiniVec::<()>::new(),
        Err(CreateError::UnsupportedZst)
    ));
    assert_eq!(
        layout_for::<u16>(usize::MAX),
        Err(PushReason::CapacityOverflow)
    );
    assert_eq!(
        layout_for::<u16>(isize::MAX as usize / 2 + 1),
        Err(PushReason::CapacityOverflow)
    );
    let l = layout_for::<u16>(4).unwrap();
    assert_eq!((l.size(), l.align()), (8, 2));
}
#[test]
fn allocation_refusal_preserves_identity() {
    let a = Allocator::default();
    let mut v = MiniVec::with_allocator(a.clone()).unwrap();
    a.fail_next();
    let value = Box::new(7);
    let address = &*value as *const i32;
    let e = v.push(value).unwrap_err();
    assert_eq!(e.reason, PushReason::AllocFailed);
    assert_eq!(&*e.value as *const i32, address);
    assert_eq!((v.len(), v.capacity()), (0, 0));
    v.push(e.value).unwrap();
    a.fail_next();
    let e = v.push(Box::new(9)).unwrap_err();
    assert_eq!(e.reason, PushReason::AllocFailed);
    assert_eq!(*e.value, 9);
    assert_eq!((v.len(), v.capacity()), (1, 1));
    assert_eq!(**v.get(0).unwrap(), 7);
    drop(v);
    let (_, alloc, free) = a.stats();
    assert_eq!((alloc, free), (1, 1));
}
#[test]
fn drop_order_and_pop_ownership() {
    let events = RefCell::new(Vec::new());
    let a = Allocator::default();
    let mut v = MiniVec::with_allocator(a.clone()).unwrap();
    for id in 0..5 {
        v.push(DropSpy {
            id,
            events: &events,
        })
        .unwrap();
    }
    let item = v.pop().unwrap();
    assert!(events.borrow().is_empty());
    drop(v);
    assert_eq!(*events.borrow(), vec![3, 2, 1, 0]);
    drop(item);
    assert_eq!(*events.borrow(), vec![3, 2, 1, 0, 4]);
    let (_, allocated, freed) = a.stats();
    assert_eq!(allocated, freed);
}
#[test]
fn aligned_elements() {
    #[repr(align(256))]
    #[derive(Debug)]
    struct Aligned(u8);
    let mut v = MiniVec::new().unwrap();
    for n in 0..5 {
        v.push(Aligned(n)).unwrap();
    }
    for n in 0..5 {
        let p = v.get(n).unwrap();
        assert_eq!(p as *const Aligned as usize % 256, 0);
        assert_eq!(p.0, n as u8);
    }
}
#[test]
fn unwind_frees_raw_buffer_once() {
    let cases: &[(u8, u8, &[u8])] = &[
        (3, 1, &[2, 1]),
        (4, 0, &[3, 2, 1, 0]),
        (4, 1, &[3, 2, 1]),
        (4, 2, &[3, 2]),
        (4, 3, &[3]),
    ];
    for &(count, bomb, prefix) in cases {
        let events = RefCell::new(Vec::new());
        let a = Allocator::default();
        let result = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
            let mut v = MiniVec::with_allocator(a.clone()).unwrap();
            for id in 0..count {
                v.push(DropBomb {
                    id,
                    explode: id == bomb,
                    events: &events,
                })
                .unwrap();
            }
            drop(v);
        }));
        assert!(result.is_err(), "bomba {bomb} deve panicar");
        let e = events.borrow();
        assert!(e.starts_with(prefix), "ordem antes da bomba {bomb}: {e:?}");
        assert_eq!(e.iter().filter(|&&id| id == bomb).count(), 1);
        for id in 0..count {
            assert!(
                e.iter().filter(|&&x| x == id).count() <= 1,
                "double drop: {id}; bomba: {bomb}"
            );
        }
        let (_, allocated, freed) = a.stats();
        assert_eq!(allocated, freed, "buffer após bomba {bomb}");
    }
}

#[test]
fn empty_drop_does_not_deallocate() {
    drop(MiniVec::<u16>::new().unwrap());
    let a = Allocator::default();
    drop(MiniVec::<u16>::with_allocator(a.clone()).unwrap());
    assert_eq!(a.stats(), (0, 0, 0));
}
#[test]
fn drop_after_first_allocation_refusal_does_not_deallocate() {
    let a = Allocator::default();
    let mut v = MiniVec::with_allocator(a.clone()).unwrap();
    a.fail_next();
    let error = v.push(Box::new(7)).unwrap_err();
    assert_eq!(error.reason, PushReason::AllocFailed);
    assert_eq!(*error.value, 7);
    assert_eq!((v.len(), v.capacity()), (0, 0));
    drop(v);
    assert_eq!(a.stats(), (1, 0, 0));
}
