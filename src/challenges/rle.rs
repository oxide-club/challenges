//! Binary RLE vectors, independent oracle, and I/O failures.
use super::{Case, Check, Context, Suite, success};
use crate::process::IoMode;
use crate::report::{Category, Failure, compare};

pub fn suite() -> Suite {
    let mut cases = Vec::new();
    let vectors = vec![
        ("empty", vec![], vec![]),
        ("single", b"A".to_vec(), b"\x01A".to_vec()),
        ("triple", b"AAA".to_vec(), b"\x03A".to_vec()),
        ("mixed", b"AAAAABBBCC".to_vec(), b"\x05A\x03B\x02C".to_vec()),
        (
            "alternating",
            b"ABAB".to_vec(),
            b"\x01A\x01B\x01A\x01B".to_vec(),
        ),
        ("run-255", vec![b'A'; 255], b"\xffA".to_vec()),
        ("run-256", vec![b'A'; 256], b"\xffA\x01A".to_vec()),
        ("run-510", vec![b'A'; 510], b"\xffA\xffA".to_vec()),
        (
            "run-511",
            [vec![b'A'; 511], vec![b'B']].concat(),
            b"\xffA\xffA\x01A\x01B".to_vec(),
        ),
        ("binary", vec![0, 0, 255], vec![2, 0, 1, 255]),
        (
            "all-bytes",
            (0..=255).collect(),
            (0..=255).flat_map(|n| [1, n]).collect(),
        ),
        (
            "run-65536",
            vec![0; 65536],
            [b"\xff\x00".repeat(257), vec![1, 0]].concat(),
        ),
    ];
    for (id, original, encoded) in vectors {
        cases.push(Case::exact(
            &format!("encode-{id}"),
            &format!("Encode {id}"),
            original.clone(),
            encoded.clone(),
            &["encode"],
        ));
        cases.push(Case::exact(
            &format!("decode-{id}"),
            &format!("Decode {id}"),
            encoded,
            original,
            &["decode"],
        ));
    }
    cases.push(Case::exact(
        "decode-adjacent",
        "Adjacent equal values",
        b"\x01A\x02A\xffA\x01A".to_vec(),
        vec![b'A'; 259],
        &["decode"],
    ));
    cases.push(Case::exact(
        "decode-all-counts",
        "Every valid count",
        (1..=255).flat_map(|n| [n, 255]).collect(),
        vec![255; 32640],
        &["decode"],
    ));
    for (id, input) in [
        ("zero-count", vec![0, b'A']),
        ("incomplete", vec![3]),
        ("zero-incomplete", vec![0]),
        ("incomplete-after-prefix", vec![1, b'A', 3]),
        ("zero-after-prefix", vec![1, b'A', 0, b'B']),
    ] {
        cases.push(Case::rejected(
            &format!("decode-{id}"),
            &format!("Reject {id}"),
            input,
            &["decode"],
            IoMode::Normal,
        ));
    }
    for (id, argv) in [
        ("missing", vec![]),
        ("uppercase", vec!["ENCODE"]),
        ("empty", vec![""]),
        ("unknown", vec!["other"]),
        ("encode-extra", vec!["encode", "extra"]),
        ("decode-extra", vec!["decode", "extra"]),
    ] {
        cases.push(Case::rejected(
            &format!("args-{id}"),
            &format!("Reject {id} argument"),
            vec![],
            &argv,
            IoMode::Normal,
        ));
    }
    // Fixed xorshift sequence, independent of any platform RNG.
    let mut state = 3u64;
    for size in [0, 1, 254, 255, 256, 8191, 8192, 8193, 131072] {
        let input = (0..size)
            .map(|_| {
                state ^= state << 13;
                state ^= state >> 7;
                state ^= state << 17;
                state as u8
            })
            .collect();
        cases.push(Case {
            id: format!("roundtrip-{size}"),
            name: format!("Round trip {size} deterministic bytes"),
            check: Check::RoundTrip(input),
        });
    }
    for (mode, small, large) in [
        (
            "encode",
            vec![b'A'],
            (0..=255).cycle().take(262144).collect(),
        ),
        ("decode", vec![1, b'A'], b"\xffA".repeat(1024)),
    ] {
        for (label, data) in [("small", small.clone()), ("large", large)] {
            cases.push(Case::rejected(
                &format!("{mode}-write-{label}"),
                &format!("{mode}: /dev/full, {label} input"),
                data,
                &[mode],
                IoMode::Full,
            ));
        }
        cases.push(Case::rejected(
            &format!("{mode}-read-error"),
            &format!("{mode}: directory stdin"),
            vec![],
            &[mode],
            IoMode::Directory,
        ));
        cases.push(Case::rejected(
            &format!("{mode}-broken-pipe"),
            &format!("{mode}: pipe without reader"),
            small,
            &[mode],
            IoMode::BrokenPipe,
        ));
    }
    Suite {
        id: "003-rle",
        cases,
    }
}

pub(crate) fn round_trip(context: &Context<'_>, input: &[u8]) -> Result<(), Failure> {
    let encoded = context.execute(input, &["encode".into()], input.len() * 2, IoMode::Normal)?;
    success(&encoded)?;
    let invalid = |message| Failure::new(Category::WrongOutput, message);
    if encoded.stdout.len() % 2 != 0 {
        return Err(invalid("encode produced an incomplete pair"));
    }
    let mut position = 0usize;
    let mut previous = None;
    for pair in encoded.stdout.chunks_exact(2) {
        let count = pair[0] as usize;
        let value = pair[1];
        if count == 0 {
            return Err(invalid("encode produced count zero"));
        }
        if let Some((last_count, last_value)) = previous {
            if last_value == value && last_count != 255 {
                return Err(invalid("encode split a run before 255"));
            }
        }
        // Validate directly against the original without allocating decoded output.
        let end = position + count;
        if end > input.len() || input[position..end].iter().any(|&b| b != value) {
            return Err(invalid("encode did not preserve the input bytes"));
        }
        position = end;
        previous = Some((count, value));
    }
    if position != input.len() {
        return Err(invalid("encode truncated the input"));
    }
    let decoded = context.execute(
        &encoded.stdout,
        &["decode".into()],
        input.len(),
        IoMode::Normal,
    )?;
    success(&decoded)?;
    compare(input, &decoded.stdout)
}
