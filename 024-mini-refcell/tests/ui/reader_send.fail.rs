use mini_refcell::*;
fn main() {
    fn send<T: Send>() {}
    send::<MiniRef<'static, i32>>();
}
