use typestate::FaultPlan;
#[test]
fn one_shot_faults_are_independent() {
    let mut p = FaultPlan {
        open: true,
        write: true,
        finalize: true,
    };
    assert!(p.take_open());
    assert!(!p.take_open());
    assert!(p.take_write());
    assert!(!p.take_write());
    assert!(p.take_finalize());
    assert!(!p.take_finalize());
}
