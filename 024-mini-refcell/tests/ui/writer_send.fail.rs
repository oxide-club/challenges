use mini_refcell::*;
fn main() {
    fn send<T: Send>() {}
    send::<MiniRefMut<'static, i32>>();
}
