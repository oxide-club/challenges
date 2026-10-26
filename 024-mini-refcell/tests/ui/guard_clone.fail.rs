use mini_refcell::*;
fn main() {
    fn cloned<T: Clone>() {}
    cloned::<MiniRef<'static, i32>>();
}
