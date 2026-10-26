use mini_refcell::*;
fn cloned<T: Clone>() {}
fn main() {
    cloned::<MiniRefMut<'static, i32>>();
}
