use mini_refcell::*;
fn main() {
    let c = MiniRefCell::new(1);
    let g = c.try_borrow().unwrap();
    println!("{}", *g);
}
