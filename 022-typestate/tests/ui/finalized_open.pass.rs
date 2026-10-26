// SPDX-License-Identifier: MIT
use typestate::*;
fn main() {
    let resource = Resource::new(FaultPlan::default())
        .open()
        .unwrap()
        .finalize()
        .unwrap();
    let _bytes = resource.bytes();
}
