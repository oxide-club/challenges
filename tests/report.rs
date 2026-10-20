use oxide_test::report::{CaseResult, Category, Failure, Report};
use std::path::Path;
use std::time::Duration;

fn result(id: &str, outcome: Result<(), Failure>) -> CaseResult {
    CaseResult::new(id, id, Duration::ZERO, outcome, String::new())
}

#[test]
fn unavailable_check_is_incomplete_and_failure_takes_precedence() {
    let skipped = || result("write-error", Err(Failure::skip("/dev/full unavailable")));
    let report = Report::new(
        "002-ppm",
        Path::new("./ppm"),
        2,
        2,
        Duration::ZERO,
        vec![result("image", Ok(())), skipped()],
    );
    assert_eq!(report.exit_code(), 3);
    assert!(!report.all_public_tests_passed);
    assert_eq!(report.summary.skipped, 1);
    assert!(report.text().contains("SKIP"));
    assert!(report.text().contains("[unavailable]"));
    let report = Report::new(
        "002-ppm",
        Path::new("./ppm"),
        2,
        2,
        Duration::ZERO,
        vec![
            result(
                "image",
                Err(Failure::new(Category::WrongOutput, "bad image")),
            ),
            skipped(),
        ],
    );
    assert_eq!(report.exit_code(), 1);
}

#[test]
fn reports_escape_candidate_control_characters() {
    let report = Report::new(
        "001-wc",
        Path::new("evil\x1b[2J"),
        1,
        1,
        Duration::ZERO,
        vec![result("vazio", Err(Failure::launch("evil\x1b[2J\0")))],
    );
    assert!(!report.text().contains('\x1b'));
    assert!(!report.text().contains('\0'));
    let json = serde_json::to_string(&report).unwrap();
    let value: serde_json::Value = serde_json::from_str(&json).unwrap();
    assert_eq!(value["results"][0]["message"], "evil\x1b[2J\0");
}
