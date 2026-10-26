use typestate::*;
fn main() {
    let mut r = Resource::new(FaultPlan::default());
    r.write(b"x");
}
