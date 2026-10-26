use mini_refcell::*;
fn main() {
    let g;
    {
        let c = MiniRefCell::new(1);
        g = c.try_borrow().unwrap();
    }
    println!("{}", *g);
}
