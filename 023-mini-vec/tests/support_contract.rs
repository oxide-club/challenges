use mini_vec::Allocator;
use std::alloc::Layout;
#[test]
fn refusal_and_allocation_observation() {
    let a = Allocator::default();
    a.fail_next();
    let l = Layout::from_size_align(16, 16).unwrap();
    assert!(a.allocate(l).is_none());
    assert_eq!(a.stats(), (1, 0, 0));
    let p = a.allocate(l).unwrap();
    assert_eq!(a.stats(), (2, 1, 0)); /* SAFETY: exact live allocation/layout, freed once. */
    unsafe { a.deallocate(p, l) };
    assert_eq!(a.stats(), (2, 1, 1));
}
