//! Stable IDs are decoupled from Rust module names.
mod vectors;

use crate::process::{self, IoMode, ProcessResult, Request};
use crate::report::{Category, Failure};
use serde::Serialize;
use std::path::Path;
use std::time::Duration;

#[derive(Serialize)]
pub struct ChallengeInfo {
    pub id: &'static str,
    pub name: &'static str,
}

// One registration adds both discovery and an embedded suite. The JSON files
// are shared with Python, never loaded from the user's machine at runtime.
macro_rules! roadmap {
    ($($id:literal => $name:literal),+ $(,)?) => {
        pub const CATALOG: &[ChallengeInfo] = &[
            $(ChallengeInfo { id: $id, name: $name },)+
        ];

        fn suite_impl(id: &str) -> Option<Suite> {
            match id {
                $($id => Some(Suite {
                    id: $id,
                    cases: vectors::parse(include_str!(concat!("../../../../", $id, "/tests/cases.json")))
                        .expect(concat!("invalid embedded suite: ", $id)),
                }),)+
                _ => None,
            }
        }
    };
}

roadmap! {
    "001-wc" => "Word count",
    "002-ppm" => "PPM image",
    "003-rle" => "RLE compressor",
    "004-hexdump" => "Hexdump",
    "005-base64" => "Base64 de ida e volta",
    "006-stream-search" => "Busca de sequência em stream",
    "007-image-bug" => "Pixels fora do lugar",
    "008-image-transform" => "Recorte e gire uma imagem",
    "009-triangle" => "Rasterizador de triângulos 2D",
    "010-fixed-buffer" => "Array fixo",
    "011-dynamic-buffer" => "Array dinâmico",
    "012-hash-table" => "Uma tabela hash que cresce",
    "013-record-inspector" => "Inspetor de um formato documentado",
    "014-mystery-image" => "Que arquivo é este?",
    "015-mystery-program" => "O que este executável faz?",
    "016-use-after-free" => "Quem liberou este buffer?",
    "017-arena" => "Arena de memória alinhada",
    "018-free-list" => "Um alocador com liberação individual",
    "019-rpn" => "Calculadora RPN",
    "020-expressions" => "Interpretador de expressões",
    "021-bytecode" => "Uma VM de bytecode",
}

pub struct Suite {
    pub id: &'static str,
    pub cases: Vec<Case>,
}

pub fn suite(id: &str) -> Option<Suite> {
    suite_impl(id)
}

pub struct Context<'a> {
    pub program: &'a Path,
    pub timeout: Duration,
}

pub struct Case {
    pub id: String,
    pub name: String,
    pub(crate) check: Check,
}

pub(crate) enum Check {
    Vector(Box<vectors::VectorCase>),
}

impl Context<'_> {
    pub(crate) fn execute(
        &self,
        input: &[u8],
        argv: &[String],
        limit: usize,
        io: IoMode,
    ) -> Result<ProcessResult, Failure> {
        process::execute(
            self.program,
            Request {
                input,
                argv,
                timeout: self.timeout,
                output_limit: limit,
                io,
            },
        )
    }
}

pub(crate) fn success(result: &ProcessResult) -> Result<(), Failure> {
    if !result.status.success() {
        return Err(Failure::new(
            Category::UnexpectedExit,
            format!(
                "Program exited with {}; stderr: {:?}",
                result.status,
                String::from_utf8_lossy(&result.stderr[..result.stderr.len().min(512)])
            ),
        ));
    }
    Ok(())
}

impl Case {
    pub fn check(&self, context: &Context<'_>) -> Result<(), Failure> {
        match &self.check {
            Check::Vector(case) => case.check(context),
        }
    }
}
