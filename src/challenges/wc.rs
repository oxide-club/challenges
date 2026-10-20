//! Public WC contract, including embedded byte fixtures.
use super::{Case, Check, Suite};

pub fn suite() -> Suite {
    let mut cases = Vec::new();
    macro_rules! fixture {
        ($name:literal) => {{
            let mut case = Case::exact(
                $name,
                $name,
                include_bytes!(concat!("../../001-wc/fixtures/", $name, ".in")).to_vec(),
                include_bytes!(concat!("../../001-wc/fixtures/", $name, ".out")).to_vec(),
                &[],
            );
            if let Check::Exact { limit, .. } = &mut case.check {
                *limit = 1024;
            }
            cases.push(case);
        }};
    }
    fixture!("bordas");
    fixture!("crlf");
    fixture!("duas-palavras");
    fixture!("espacos");
    fixture!("exemplo");
    fixture!("sem-quebra");
    fixture!("separadores");
    fixture!("todos-separadores");
    fixture!("ultima-linha");
    fixture!("uma-linha");
    fixture!("vazio");
    for (id, name, data, expected) in [
        (
            "palavra-longa",
            "128 KiB word",
            vec![b'x'; 131072],
            b"0 1 131072\n".to_vec(),
        ),
        (
            "muitas-linhas",
            "32768 lines",
            b"a b\n".repeat(32768),
            b"32768 65536 131072\n".to_vec(),
        ),
    ] {
        let mut case = Case::exact(id, name, data, expected, &[]);
        if let Check::Exact { limit, .. } = &mut case.check {
            *limit = 1024;
        }
        cases.push(case);
    }
    Suite {
        id: "001-wc",
        cases,
    }
}
