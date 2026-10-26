use mini_refcell::*;
fn main() {
    fn sync<T: Sync>() {}
    sync::<MiniRef<'static, i32>>();
}
