use typestate::*;
fn main() {
    let mut r = Resource::new(FaultPlan::default()).open().unwrap();
    r.write(b"x").unwrap();
}
