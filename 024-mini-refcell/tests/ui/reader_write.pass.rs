use mini_refcell::*;
fn main() {
    let c = MiniRefCell::new(1);
    let mut g = c.try_borrow_mut().unwrap();
    *g = 2;
}
