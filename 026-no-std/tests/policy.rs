// SPDX-License-Identifier: MIT
#[path = "../materials/starter/policy.rs"]
mod policy;
use policy::{write_all_with, WriteError};
#[test]
fn vazio_nao_chama() {
    assert_eq!(write_all_with(b"", |_| panic!("não deve chamar")), Ok(()));
}
#[test]
fn parcial_nao_repete_prefixo() {
    let mut calls = 0;
    let r = write_all_with(b"abcde", |b| {
        calls += 1;
        match calls {
            1 => {
                assert_eq!(b, b"abcde");
                2
            }
            2 => {
                assert_eq!(b, b"cde");
                1
            }
            3 => {
                assert_eq!(b, b"de");
                2
            }
            _ => panic!("chamada excedente"),
        }
    });
    assert_eq!(r, Ok(()));
    assert_eq!(calls, 3);
}
#[test]
fn eintr_repete_somente_pendente() {
    let mut calls = 0;
    assert_eq!(
        write_all_with(b"ab", |b| {
            calls += 1;
            match calls {
                1 => {
                    assert_eq!(b, b"ab");
                    1
                }
                2 => {
                    assert_eq!(b, b"b");
                    -4
                }
                3 => {
                    assert_eq!(b, b"b");
                    1
                }
                _ => panic!("excesso"),
            }
        }),
        Ok(())
    );
    assert_eq!(calls, 3);
}
#[test]
fn zero_e_erro() {
    assert_eq!(write_all_with(b"x", |_| 0), Err(WriteError::WriteZero));
    assert_eq!(write_all_with(b"x", |_| -9), Err(WriteError::Syscall(9)));
}
