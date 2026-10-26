use typestate::*;
fn main() {
    let mut r = Resource::new(FaultPlan::default())
        .open()
        .unwrap()
        .finalize()
        .unwrap();
    r.write(b"x");
}
