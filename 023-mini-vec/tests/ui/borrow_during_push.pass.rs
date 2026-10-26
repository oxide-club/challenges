use mini_vec::*;
fn main() {
    let mut v = MiniVec::new().unwrap();
    v.push(1).unwrap();
    println!("{}", v.get(0).unwrap());
    v.push(2).unwrap();
}
