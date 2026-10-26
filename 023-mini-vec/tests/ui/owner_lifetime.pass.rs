use mini_vec::*;
fn main() {
    let mut v = MiniVec::new().unwrap();
    v.push(1).unwrap();
    let r = v.get(0).unwrap();
    println!("{}", r);
}
