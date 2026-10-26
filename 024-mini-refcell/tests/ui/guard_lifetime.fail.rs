use mini_refcell::*;
fn main() {
    let c = MiniRefCell::new(1);
    let r;
    {
        let g = c.try_borrow().unwrap();
        r = &*g;
    }
    println!("{}", r);
}
