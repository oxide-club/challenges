use mini_refcell::*;
fn main() {
    fn sync<T: Sync>() {}
    sync::<MiniRefCell<i32>>();
}
