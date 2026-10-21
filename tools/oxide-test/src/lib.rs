//! Reusable public challenge suites. Challenge IDs are metadata, not module names.
#![cfg(target_os = "linux")]

pub mod challenges;
pub mod process;
pub mod report;

use std::path::Path;
use std::time::{Duration, Instant};

use challenges::Context;
use report::{CaseResult, Category, Failure, Report, Status};

/// Run all cases or the requested stable IDs. No shell is used to launch programs.
pub fn run(
    challenge: &str,
    program: &Path,
    selected: &[String],
    timeout: Duration,
    fail_fast: bool,
) -> Result<Report, Failure> {
    let suite = challenges::suite(challenge)
        .ok_or_else(|| Failure::setup(format!("Unknown challenge: {challenge}")))?;
    for id in selected {
        if !suite.cases.iter().any(|case| &case.id == id) {
            return Err(Failure::setup(format!(
                "Unknown case: {id}. Use oxide-test list {challenge}"
            )));
        }
    }
    if timeout.is_zero() || timeout.as_secs_f64() > 86400.0 {
        return Err(Failure::setup(
            "Timeout must be greater than 0 and at most 86400 seconds",
        ));
    }
    let program = program
        .canonicalize()
        .map_err(|e| Failure::launch(e.to_string()))?;
    use std::os::unix::fs::PermissionsExt;
    let metadata = program
        .metadata()
        .map_err(|e| Failure::launch(e.to_string()))?;
    if !metadata.is_file() || metadata.permissions().mode() & 0o111 == 0 {
        return Err(Failure::launch(
            "Program must be a file with execute permission",
        ));
    }
    let total = suite.cases.len();
    let cases: Vec<_> = suite
        .cases
        .into_iter()
        .filter(|case| selected.is_empty() || selected.contains(&case.id))
        .collect();
    let count = cases.len();
    let started = Instant::now();
    let context = Context {
        program: &program,
        timeout,
    };
    let mut results = Vec::new();
    for case in cases {
        let start = Instant::now();
        let outcome = case.check(&context);
        if matches!(&outcome, Err(f) if matches!(f.category, Category::LaunchError | Category::HarnessError))
        {
            return Err(outcome.unwrap_err());
        }
        let result = CaseResult::new(
            &case.id,
            &case.name,
            start.elapsed(),
            outcome,
            format!(
                "oxide-test run {} {} --case {} --timeout {}",
                report::quote(challenge),
                report::quote_path(&program),
                report::quote(&case.id),
                timeout.as_secs_f64()
            ),
        );
        let failed = result.status == Status::Failed;
        results.push(result);
        if failed && fail_fast {
            break;
        }
    }
    Ok(Report::new(
        challenge,
        &program,
        total,
        count,
        started.elapsed(),
        results,
    ))
}
