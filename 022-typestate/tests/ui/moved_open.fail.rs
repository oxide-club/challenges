use typestate::*;
fn main() {
    let r = Resource::new(FaultPlan::default());
    let _ = r.open();
    let _ = r.open();
}
