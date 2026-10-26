use mini_refcell::*;
fn main() {
    fn sync<T: Sync>() {}
    sync::<MiniRefMut<'static, i32>>();
}
