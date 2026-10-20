//! Exact PPM image and write-error contract.
use super::{Case, Check, Suite};
use crate::process::IoMode;

pub fn suite() -> Suite {
    let mut image = b"P6\n256 256\n255\n".to_vec();
    for y in 0..=255 {
        for x in 0..=255 {
            image.extend_from_slice(&[x, y, 0]);
        }
    }
    let mut exact = Case::exact(
        "image",
        "Header, length and all 65536 pixels",
        vec![],
        image,
        &[],
    );
    if let Check::Exact { ppm, .. } = &mut exact.check {
        *ppm = true;
    }
    Suite {
        id: "002-ppm",
        cases: vec![
            exact,
            Case::rejected(
                "write-error",
                "Write error on /dev/full",
                vec![],
                &[],
                IoMode::Full,
            ),
        ],
    }
}
