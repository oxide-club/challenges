//! Stable IDs are decoupled from Rust module names.
pub mod ppm;
pub mod rle;
pub mod wc;

use crate::process::{self, IoMode, ProcessResult, Request};
use crate::report::{self, Category, Failure};
use serde::Serialize;
use std::path::Path;
use std::time::Duration;

#[derive(Serialize)]
pub struct ChallengeInfo {
    pub id: &'static str,
    pub name: &'static str,
}

pub const CATALOG: &[ChallengeInfo] = &[
    ChallengeInfo {
        id: "001-wc",
        name: "Word count",
    },
    ChallengeInfo {
        id: "002-ppm",
        name: "PPM image",
    },
    ChallengeInfo {
        id: "003-rle",
        name: "RLE compressor",
    },
];

pub struct Suite {
    pub id: &'static str,
    pub cases: Vec<Case>,
}

pub fn suite(id: &str) -> Option<Suite> {
    match id {
        "001-wc" => Some(wc::suite()),
        "002-ppm" => Some(ppm::suite()),
        "003-rle" => Some(rle::suite()),
        _ => None,
    }
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
    Exact {
        input: Vec<u8>,
        expected: Vec<u8>,
        argv: Vec<String>,
        limit: usize,
        ppm: bool,
    },
    Rejected {
        input: Vec<u8>,
        argv: Vec<String>,
        io: IoMode,
    },
    RoundTrip(Vec<u8>),
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
    pub(crate) fn exact(
        id: &str,
        name: &str,
        input: Vec<u8>,
        expected: Vec<u8>,
        argv: &[&str],
    ) -> Self {
        let limit = expected.len();
        Self {
            id: id.into(),
            name: name.into(),
            check: Check::Exact {
                input,
                expected,
                argv: argv.iter().map(|s| (*s).into()).collect(),
                limit,
                ppm: false,
            },
        }
    }
    pub(crate) fn rejected(
        id: &str,
        name: &str,
        input: Vec<u8>,
        argv: &[&str],
        io: IoMode,
    ) -> Self {
        Self {
            id: id.into(),
            name: name.into(),
            check: Check::Rejected {
                input,
                argv: argv.iter().map(|s| (*s).into()).collect(),
                io,
            },
        }
    }
    pub fn check(&self, context: &Context<'_>) -> Result<(), Failure> {
        match &self.check {
            Check::Exact {
                input,
                expected,
                argv,
                limit,
                ppm,
            } => {
                let result = context.execute(input, argv, *limit, IoMode::Normal)?;
                success(&result)?;
                report::compare(expected, &result.stdout).map_err(|mut failure| {
                    if *ppm {
                        if let Some(offset) = expected
                            .iter()
                            .zip(&result.stdout)
                            .position(|(a, b)| a != b)
                        {
                            if offset >= 15 {
                                let pixel = (offset - 15) / 3;
                                failure.message.push_str(&format!(
                                    "\nPixel ({}, {}), channel {}",
                                    pixel % 256,
                                    pixel / 256,
                                    ["R", "G", "B"][(offset - 15) % 3]
                                ));
                            }
                        }
                    }
                    failure
                })
            }
            Check::Rejected { input, argv, io } => {
                let result = context.execute(input, argv, 262144, *io)?;
                if result.status.success() {
                    return Err(Failure::new(
                        Category::UnexpectedExit,
                        "Invalid input or I/O error returned success",
                    ));
                }
                // Match Python bytes.strip(), including vertical tab, which
                // Rust's is_ascii_whitespace intentionally excludes.
                if !result
                    .stderr
                    .iter()
                    .any(|b| !matches!(*b, b' ' | b'\t' | b'\n' | b'\r' | 0x0b | 0x0c))
                {
                    return Err(Failure::new(
                        Category::WrongOutput,
                        "Error was not diagnosed on stderr",
                    ));
                }
                Ok(())
            }
            Check::RoundTrip(input) => rle::round_trip(context, input),
        }
    }
}
