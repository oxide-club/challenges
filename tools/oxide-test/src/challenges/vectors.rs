//! Binary vectors shared with the Python runner, embedded at compilation.

use super::{Case, Check, Context, success};
use crate::process::IoMode;
use crate::report::{self, Category, Failure};
use serde::Deserialize;
use std::collections::HashSet;
use std::fs;

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Document {
    schema_version: u8,
    cases: Vec<RawCase>,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct RawCase {
    id: String,
    name: String,
    argv: Vec<String>,
    stdin_hex: String,
    #[serde(default, deserialize_with = "optional_hex_string")]
    stdout_hex: Option<String>,
    #[serde(default)]
    reject: bool,
    #[serde(default)]
    input_file: bool,
    #[serde(default)]
    io: VectorIo,
    #[serde(default, deserialize_with = "optional_hex_string")]
    stderr_hex: Option<String>,
    #[serde(default, deserialize_with = "optional_argv")]
    roundtrip_argv: Option<Vec<String>>,
}

fn optional_argv<'de, D>(deserializer: D) -> Result<Option<Vec<String>>, D::Error>
where
    D: serde::Deserializer<'de>,
{
    Vec::<String>::deserialize(deserializer).map(Some)
}

fn optional_hex_string<'de, D>(deserializer: D) -> Result<Option<String>, D::Error>
where
    D: serde::Deserializer<'de>,
{
    String::deserialize(deserializer).map(Some)
}

#[derive(Clone, Copy, Default, Deserialize, PartialEq)]
#[serde(rename_all = "snake_case")]
enum VectorIo {
    #[default]
    Normal,
    Full,
    Directory,
    BrokenPipe,
}

pub(crate) struct VectorCase {
    input: Vec<u8>,
    expected: Option<Vec<u8>>,
    argv: Vec<String>,
    input_file: bool,
    io: VectorIo,
    stderr: Option<Vec<u8>>,
    roundtrip_argv: Option<Vec<String>>,
}

fn bytes(hex: &str) -> Result<Vec<u8>, String> {
    if hex.len() % 2 != 0
        || !hex
            .bytes()
            .all(|b| b.is_ascii_digit() || (b'a'..=b'f').contains(&b))
    {
        return Err("bytes must be lowercase hexadecimal without whitespace".into());
    }
    (0..hex.len())
        .step_by(2)
        .map(|i| u8::from_str_radix(&hex[i..i + 2], 16).map_err(|e| e.to_string()))
        .collect()
}

pub(super) fn parse(text: &str) -> Result<Vec<Case>, String> {
    let document: Document = serde_json::from_str(text).map_err(|e| e.to_string())?;
    if document.schema_version != 1 || document.cases.is_empty() {
        return Err("expected schema_version 1 and nonempty cases".into());
    }
    let mut ids = HashSet::new();
    document
        .cases
        .into_iter()
        .map(|raw| {
            if raw.id.split('-').any(|part| {
                part.is_empty()
                    || !part
                        .bytes()
                        .all(|b| b.is_ascii_lowercase() || b.is_ascii_digit())
            }) || !ids.insert(raw.id.clone())
                || raw.name.trim().is_empty()
            {
                return Err(format!("invalid or duplicated case ID/name: {}", raw.id));
            }
            if raw.reject == raw.stdout_hex.is_some() {
                return Err(format!("{}: expected stdout_hex OR reject:true", raw.id));
            }
            if raw.argv.iter().any(|a| a.contains('\0'))
                || raw.input_file != raw.argv.iter().any(|a| a == "{input}")
                || (raw.input_file && raw.io != VectorIo::Normal)
            {
                return Err(format!("{}: invalid argv or file placeholder", raw.id));
            }
            if raw.roundtrip_argv.as_ref().is_some_and(|args| {
                args.is_empty()
                    || args.iter().any(|a| a.contains('\0') || a == "{input}")
                    || raw.reject
                    || raw.input_file
                    || raw.io != VectorIo::Normal
            }) {
                return Err(format!("{}: invalid roundtrip_argv", raw.id));
            }
            let vector = VectorCase {
                roundtrip_argv: raw.roundtrip_argv,
                input: bytes(&raw.stdin_hex)?,
                expected: raw.stdout_hex.as_deref().map(bytes).transpose()?,
                argv: raw.argv,
                input_file: raw.input_file,
                io: raw.io,
                stderr: raw.stderr_hex.as_deref().map(bytes).transpose()?,
            };
            Ok(Case {
                id: raw.id,
                name: raw.name,
                check: Check::Vector(Box::new(vector)),
            })
        })
        .collect()
}

impl VectorCase {
    pub(super) fn check(&self, context: &Context<'_>) -> Result<(), Failure> {
        let mut argv = self.argv.clone();
        let mut input = self.input.as_slice();
        // Keep the directory alive until the child exits, including error paths.
        let directory = if self.input_file {
            let directory = tempfile::Builder::new()
                .prefix("oxide-test-")
                .tempdir()
                .map_err(Failure::harness)?;
            let path = directory.path().join("input with spaces.bin");
            fs::write(&path, input).map_err(Failure::harness)?;
            for arg in &mut argv {
                if arg == "{input}" {
                    *arg = path
                        .to_str()
                        .ok_or_else(|| Failure::setup("Temporary path is not UTF-8"))?
                        .into();
                }
            }
            input = &[];
            Some(directory)
        } else {
            None
        };
        let io = match self.io {
            VectorIo::Normal => IoMode::Normal,
            VectorIo::Full => IoMode::Full,
            VectorIo::Directory => IoMode::Directory,
            VectorIo::BrokenPipe => IoMode::BrokenPipe,
        };
        let limit = self.expected.as_ref().map_or(262144, Vec::len);
        let result = context.execute(input, &argv, limit, io)?;
        drop(directory);
        if let Some(expected) = &self.expected {
            success(&result)?;
            compare_output(expected, &result.stdout)?;
            if let Some(argv) = &self.roundtrip_argv {
                let decoded =
                    context.execute(&result.stdout, argv, self.input.len(), IoMode::Normal)?;
                success(&decoded)?;
                report::compare(&self.input, &decoded.stdout)?;
            }
        } else {
            if result.status.success() {
                return Err(Failure::new(
                    Category::UnexpectedExit,
                    "Invalid input or I/O error returned success",
                ));
            }
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
        }
        if let Some(expected) = &self.stderr {
            report::compare(expected, &result.stderr).map_err(|mut failure| {
                failure.message = format!("stderr: {}", failure.message);
                failure
            })?;
        }
        Ok(())
    }
}

// Recognize only canonical, complete P6 images; arbitrary binary output is never
// interpreted as an image merely because it begins with the magic bytes.
fn ppm_layout(bytes: &[u8]) -> Option<(usize, usize)> {
    let rest = bytes.strip_prefix(b"P6\n")?;
    let dimensions_end = rest.iter().position(|&b| b == b'\n')?;
    let dimensions = std::str::from_utf8(&rest[..dimensions_end]).ok()?;
    let (width, height) = dimensions.split_once(' ')?;
    let number = |s: &str| -> Option<usize> {
        if s.is_empty() || !s.bytes().all(|b| b.is_ascii_digit()) || s.starts_with('0') {
            return None;
        }
        s.parse().ok()
    };
    let width = number(width)?;
    let height = number(height)?;
    let header = 3 + dimensions_end + 1 + 4;
    rest[dimensions_end + 1..].strip_prefix(b"255\n")?;
    let size = width
        .checked_mul(height)?
        .checked_mul(3)?
        .checked_add(header)?;
    (bytes.len() == size).then_some((header, width))
}

fn compare_output(expected: &[u8], actual: &[u8]) -> Result<(), Failure> {
    report::compare(expected, actual).map_err(|mut failure| {
        if let Some((header, width)) = ppm_layout(expected) {
            if let Some(offset) = expected.iter().zip(actual).position(|(a, b)| a != b) {
                if offset >= header {
                    let pixel = (offset - header) / 3;
                    failure.message.push_str(&format!(
                        "\nPixel ({}, {}), channel {}",
                        pixel % width,
                        pixel / width,
                        ["R", "G", "B"][(offset - header) % 3]
                    ));
                }
            }
        }
        failure
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::{Value, json};

    fn document() -> Value {
        json!({"schema_version": 1, "cases": [{
            "id": "binary", "name": "Binary input", "argv": [],
            "stdin_hex": "00ff0a", "stdout_hex": "00ff0a"
        }]})
    }

    #[test]
    fn validates_roundtrip_contract() {
        let mut d = document();
        d["cases"][0]["roundtrip_argv"] = json!(["decode"]);
        assert!(parse(&d.to_string()).is_ok());
        for value in [
            json!([]),
            json!(null),
            json!(["{input}"]),
            json!(["a\u{0}b"]),
            json!([1]),
        ] {
            d["cases"][0]["roundtrip_argv"] = value;
            assert!(parse(&d.to_string()).is_err());
        }
        for (key, value) in [
            ("io", json!("full")),
            ("input_file", json!(true)),
            ("reject", json!(true)),
        ] {
            let mut d = document();
            d["cases"][0]["roundtrip_argv"] = json!(["decode"]);
            d["cases"][0][key] = value;
            assert!(parse(&d.to_string()).is_err());
        }
    }

    #[test]
    fn reads_binary_and_validates_contract() {
        let cases = parse(&document().to_string()).unwrap();
        assert_eq!(cases.len(), 1);
        assert_eq!(cases[0].id, "binary");
        for replacement in [
            json!("0"),
            json!("00 ff"),
            json!("FF"),
            json!("gg"),
            json!(0),
        ] {
            let mut d = document();
            d["cases"][0]["stdin_hex"] = replacement;
            assert!(parse(&d.to_string()).is_err());
        }
        for replacement in [json!(2), json!(true), json!(null)] {
            let mut d = document();
            d["schema_version"] = replacement;
            assert!(parse(&d.to_string()).is_err());
        }
        let mut d = document();
        d["cases"][0]["reject"] = json!(true);
        assert!(parse(&d.to_string()).is_err());
        let mut d = document();
        d["cases"][0].as_object_mut().unwrap().remove("stdout_hex");
        assert!(parse(&d.to_string()).is_err());
        let mut d = document();
        let duplicate = d["cases"][0].clone();
        d["cases"].as_array_mut().unwrap().push(duplicate);
        assert!(parse(&d.to_string()).is_err());
        let mut d = document();
        d["cases"] = json!([]);
        assert!(parse(&d.to_string()).is_err());
    }

    #[test]
    fn rejects_explicit_null_stdout_hex_with_reject() {
        let mut d = document();
        d["cases"][0]["stdout_hex"] = json!(null);
        d["cases"][0]["reject"] = json!(true);
        assert!(parse(&d.to_string()).is_err());
    }

    #[test]
    fn rejects_explicit_null_stderr_hex() {
        let mut d = document();
        d["cases"][0]["stderr_hex"] = json!(null);
        assert!(parse(&d.to_string()).is_err());
    }

    #[test]
    fn validates_file_placeholder_and_arguments() {
        for (args, file, valid) in [
            (json!(["{input}"]), true, true),
            (json!(["{input}"]), false, false),
            (json!([]), true, false),
            (json!(["a\u{0}b"]), false, false),
        ] {
            let mut d = document();
            d["cases"][0]["argv"] = args;
            d["cases"][0]["input_file"] = json!(file);
            assert_eq!(parse(&d.to_string()).is_ok(), valid);
        }
    }
}
