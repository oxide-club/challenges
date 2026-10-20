use serde::Serialize;
use std::path::Path;
use std::time::Duration;

#[derive(Clone, Copy, Debug, Serialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum Category {
    WrongOutput,
    UnexpectedExit,
    LaunchError,
    Timeout,
    OutputLimit,
    HarnessError,
    Unavailable,
    UsageError,
}

impl std::fmt::Display for Category {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.write_str(match self {
            Self::WrongOutput => "wrong_output",
            Self::UnexpectedExit => "unexpected_exit",
            Self::LaunchError => "launch_error",
            Self::Timeout => "timeout",
            Self::OutputLimit => "output_limit",
            Self::HarnessError => "harness_error",
            Self::Unavailable => "unavailable",
            Self::UsageError => "usage_error",
        })
    }
}

#[derive(Debug, Serialize)]
pub struct Failure {
    pub category: Category,
    pub message: String,
}

impl std::fmt::Display for Failure {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.write_str(&self.message)
    }
}

impl std::error::Error for Failure {}

impl Failure {
    pub fn new(category: Category, message: impl Into<String>) -> Self {
        Self {
            category,
            message: message.into(),
        }
    }
    pub fn setup(message: impl Into<String>) -> Self {
        Self::new(Category::UsageError, message)
    }
    pub fn launch(message: impl Into<String>) -> Self {
        Self::new(Category::LaunchError, message)
    }
    pub fn harness(error: impl std::fmt::Display) -> Self {
        Self::new(Category::HarnessError, error.to_string())
    }
    pub fn skip(message: impl Into<String>) -> Self {
        Self::new(Category::Unavailable, message)
    }
}

#[derive(Clone, Copy, Debug, Serialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum Status {
    Passed,
    Failed,
    Skipped,
}

#[derive(Debug, Serialize)]
pub struct CaseResult {
    pub id: String,
    pub name: String,
    pub status: Status,
    pub duration_ms: f64,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub category: Option<Category>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub message: Option<String>,
    pub rerun: String,
}

impl CaseResult {
    pub fn new(
        id: &str,
        name: &str,
        duration: Duration,
        outcome: Result<(), Failure>,
        rerun: String,
    ) -> Self {
        let (status, category, message) = match outcome {
            Ok(()) => (Status::Passed, None, None),
            Err(f) => (
                if f.category == Category::Unavailable {
                    Status::Skipped
                } else {
                    Status::Failed
                },
                Some(f.category),
                Some(f.message),
            ),
        };
        Self {
            id: id.into(),
            name: name.into(),
            status,
            duration_ms: duration.as_secs_f64() * 1000.0,
            category,
            message,
            rerun,
        }
    }
}

#[derive(Debug, Serialize)]
pub struct Summary {
    pub total: usize,
    pub selected: usize,
    pub executed: usize,
    pub passed: usize,
    pub failed: usize,
    pub skipped: usize,
    pub not_run: usize,
}

#[derive(Debug, Serialize)]
pub struct Report {
    pub schema_version: u32,
    pub runner_version: &'static str,
    pub test_revision: &'static str,
    pub challenge: String,
    pub program: String,
    /// Original Unix path bytes, in hex, when the display path is not UTF-8.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub program_bytes_hex: Option<String>,
    pub duration_ms: f64,
    pub all_public_tests_passed: bool,
    pub summary: Summary,
    pub results: Vec<CaseResult>,
}

impl Report {
    pub fn new(
        challenge: &str,
        program: &Path,
        total: usize,
        selected: usize,
        duration: Duration,
        results: Vec<CaseResult>,
    ) -> Self {
        let summary = Summary {
            total,
            selected,
            executed: results.len(),
            passed: results
                .iter()
                .filter(|r| r.status == Status::Passed)
                .count(),
            failed: results
                .iter()
                .filter(|r| r.status == Status::Failed)
                .count(),
            skipped: results
                .iter()
                .filter(|r| r.status == Status::Skipped)
                .count(),
            not_run: selected - results.len(),
        };
        Self {
            schema_version: 1,
            runner_version: env!("CARGO_PKG_VERSION"),
            test_revision: env!("OXIDE_TEST_REVISION"),
            challenge: challenge.into(),
            program: program
                .to_str()
                .map(str::to_owned)
                .unwrap_or_else(|| format!("{:?}", program.as_os_str())),
            program_bytes_hex: if program.to_str().is_none() {
                use std::os::unix::ffi::OsStrExt;
                Some(
                    program
                        .as_os_str()
                        .as_bytes()
                        .iter()
                        .map(|b| format!("{b:02x}"))
                        .collect(),
                )
            } else {
                None
            },
            duration_ms: duration.as_secs_f64() * 1000.0,
            all_public_tests_passed: summary.passed == total,
            summary,
            results,
        }
    }
    pub fn exit_code(&self) -> u8 {
        if self.summary.failed > 0 {
            1
        } else if self.summary.skipped > 0 || self.summary.not_run > 0 {
            3
        } else {
            0
        }
    }
    pub fn text(&self) -> String {
        use std::fmt::Write;
        let mut text = format!("{} · {}\n\n", self.challenge, escaped(&self.program));
        for result in &self.results {
            let label = match result.status {
                Status::Passed => "PASS",
                Status::Failed => "FAIL",
                Status::Skipped => "SKIP",
            };
            writeln!(
                text,
                "{label:4}  {} · {} ({:.1} ms)",
                result.id, result.name, result.duration_ms
            )
            .unwrap();
            if let Some(message) = &result.message {
                if let Some(category) = result.category {
                    writeln!(text, "      [{category}]").unwrap();
                }
                for line in message.lines() {
                    writeln!(text, "      {}", escaped(line)).unwrap();
                }
                writeln!(text, "      Rerun: {}", escaped(&result.rerun)).unwrap();
            }
        }
        writeln!(
            text,
            "\n{} passed · {} failed · {} skipped · {} not run",
            self.summary.passed, self.summary.failed, self.summary.skipped, self.summary.not_run
        )
        .unwrap();
        writeln!(
            text,
            "Executed {} of {} selected checks ({} public checks total).",
            self.summary.executed, self.summary.selected, self.summary.total
        )
        .unwrap();
        if self.all_public_tests_passed {
            text.push_str("Passed all public tests.\n");
        }
        text
    }
}

pub fn escaped(value: &str) -> String {
    value
        .chars()
        .flat_map(|c| {
            if c.is_control() {
                c.escape_default().collect::<Vec<_>>()
            } else {
                vec![c]
            }
        })
        .collect()
}

pub fn quote(value: &str) -> String {
    format!("'{}'", value.replace('\'', "'\\''"))
}

/// Bash byte quoting preserves opaque Linux paths and keeps controls printable.
/// Ordinary UTF-8 paths use portable POSIX single quoting.
pub fn quote_path(path: &Path) -> String {
    if let Some(path) = path.to_str().filter(|s| !s.chars().any(char::is_control)) {
        return quote(path);
    }
    use std::os::unix::ffi::OsStrExt;
    let mut result = String::from("$'");
    for &byte in path.as_os_str().as_bytes() {
        match byte {
            b'\'' => result.push_str("\\'"),
            b'\\' => result.push_str("\\\\"),
            0x20..=0x7e => result.push(byte as char),
            _ => result.push_str(&format!("\\x{byte:02x}")),
        }
    }
    result.push('\'');
    result
}

pub fn compare(expected: &[u8], actual: &[u8]) -> Result<(), Failure> {
    if expected == actual {
        return Ok(());
    }
    let offset = expected
        .iter()
        .zip(actual)
        .position(|(a, b)| a != b)
        .unwrap_or(expected.len().min(actual.len()));
    let preview = |data: &[u8]| {
        let end = data.len().min(offset.saturating_add(16));
        if offset >= data.len() {
            return "<EOF>".to_string();
        }
        data[offset..end]
            .iter()
            .map(|b| format!("{b:02x}"))
            .collect::<Vec<_>>()
            .join(" ")
    };
    let mut message = format!(
        "First difference at byte offset {offset}\nExpected ({} bytes): {}\nReceived ({} bytes): {}",
        expected.len(),
        preview(expected),
        actual.len(),
        preview(actual)
    );
    if expected.len() <= 80 && actual.len() <= 80 {
        message.push_str(&format!(
            "\nExpected text: {:?}\nReceived text: {:?}",
            String::from_utf8_lossy(expected),
            String::from_utf8_lossy(actual)
        ));
    }
    Err(Failure::new(Category::WrongOutput, message))
}
