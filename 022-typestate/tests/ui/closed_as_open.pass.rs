// SPDX-License-Identifier: MIT
use typestate::*;
fn main() {
    let _resource: Resource<Open> = Resource::new(FaultPlan::default()).open().unwrap();
}
