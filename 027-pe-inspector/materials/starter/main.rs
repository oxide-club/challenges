// SPDX-License-Identifier: MIT
#![allow(dead_code)]
// Interfaces sugeridas, sem dependências. Complete as etapas TODO.
// Não use structs repr(C) como representação dos bytes externos.
#[derive(Debug)]
struct Diagnostic {
    code: &'static str,
    field: &'static str,
    offset: u64,
}
struct Query {
    rva: u32,
    size: u32,
}
struct Directory {
    address: u32,
    size: u32,
}
struct Section {
    name: [u8; 8],
    rva: u32,
    virtual_size: u32,
    raw_offset: u32,
    raw_size: u32,
}
struct Image {
    image_base: u64,
    entry_rva: u32,
    size_of_headers: u32,
    directories: Vec<Directory>,
    sections: Vec<Section>,
}
enum Kind {
    Headers,
    SectionRaw,
    ZeroFill,
    CrossRegion,
    Unmapped,
}
struct Classification {
    kind: Kind,
    section_index: Option<usize>,
    file_offset: Option<u64>,
}
fn inspect(_bytes: &[u8]) -> Result<Image, Diagnostic> {
    // TODO: limites, assinaturas, campos, diretórios e intervalos.
    Err(Diagnostic {
        code: "not_implemented",
        field: "parser",
        offset: 0,
    })
}
fn classify(_image: &Image, _query: &Query) -> Classification {
    todo!("classifique o intervalo inteiro; preserve limites exclusivos")
}
fn main() {
    // TODO: argumentos, leitura limitada, inspect, classify e serialização JSON.
    // Preserve os status 0/2/3/4 documentados. Não execute a imagem.
    let error = inspect(&[]).err().expect("starter incompleto");
    eprintln!(
        "{{\"code\":\"{}\",\"field\":\"{}\",\"offset\":\"0x{:x}\"}}",
        error.code, error.field, error.offset
    );
    std::process::exit(3);
}
