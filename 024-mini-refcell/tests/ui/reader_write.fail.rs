use mini_refcell::*;
fn main() {
    let c = MiniRefCell::new(1);
    let mut g = c.try_borrow().unwrap();
    *g = 2;
}
