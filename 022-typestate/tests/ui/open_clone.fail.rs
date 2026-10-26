// SPDX-License-Identifier: MIT
use typestate::*;
fn main() {
    let resource = Resource::new(FaultPlan::default()).open().unwrap();
    let _cloned = resource.clone();
}
