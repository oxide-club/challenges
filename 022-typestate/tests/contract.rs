use typestate::*;
#[test]
fn ordered_bytes_and_empty() {
    let mut r = Resource::new(FaultPlan::default()).open().unwrap();
    r.write(b"ab").unwrap();
    r.write(b"cd").unwrap();
    assert_eq!(
        r.finalize().unwrap().bytes(),
        include_bytes!("../materials/bytes.bin")
    );
    assert_eq!(
        Resource::new(FaultPlan::default())
            .open()
            .unwrap()
            .finalize()
            .unwrap()
            .bytes(),
        b""
    );
}
#[test]
fn independent_failures_preserve_resource() {
    let e = Resource::new(FaultPlan {
        open: true,
        write: true,
        finalize: true,
    })
    .open()
    .unwrap_err();
    assert_eq!(e.reason, TransitionReason::Injected);
    let mut r = e.resource.open().unwrap();
    assert_eq!(r.write(b"ab"), Err(WriteError::Injected));
    r.write(b"ab").unwrap();
    let e = r.finalize().unwrap_err();
    assert_eq!(e.reason, TransitionReason::Injected);
    assert_eq!(e.resource.finalize().unwrap().bytes(), b"ab");
}
#[test]
fn capacity_precedes_injection_and_empty_preserves_trigger() {
    let mut r = Resource::new(FaultPlan {
        write: true,
        ..Default::default()
    })
    .open()
    .unwrap();
    assert_eq!(r.write(&[7; 4097]), Err(WriteError::CapacityExceeded));
    r.write(b"").unwrap();
    assert_eq!(r.write(b"x"), Err(WriteError::Injected));
    r.write(&[7; 4096]).unwrap();
    r.write(b"").unwrap();
    assert_eq!(r.write(b"x"), Err(WriteError::CapacityExceeded));
    assert_eq!(r.finalize().unwrap().bytes(), &[7; 4096]);
}
#[test]
fn failed_write_is_atomic() {
    let mut r = Resource::new(FaultPlan::default()).open().unwrap();
    r.write(&[3; 4095]).unwrap();
    assert_eq!(r.write(b"xy"), Err(WriteError::CapacityExceeded));
    r.write(b"z").unwrap();
    let r = r.finalize().unwrap();
    assert_eq!(&r.bytes()[..4095], &[3; 4095]);
    assert_eq!(r.bytes()[4095], b'z');
}
