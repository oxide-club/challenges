// SPDX-License-Identifier: MIT
use typestate::*;
fn main() {
    let original = Resource::new(FaultPlan::default());
    let _replacement: Resource<Closed> = Resource { ..original };
}
