use typestate::*;
fn main() {
    let r = Resource::new(FaultPlan::default()).open().unwrap();
    let _ = r.finalize();
    let _ = r.finalize();
}
