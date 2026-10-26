use mini_vec::*;
fn main() {
    let r;
    {
        let mut v = MiniVec::new().unwrap();
        v.push(1).unwrap();
        r = v.get(0).unwrap();
    }
    println!("{}", r);
}
