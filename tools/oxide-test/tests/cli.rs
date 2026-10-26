#![cfg(target_os = "linux")]

use serde_json::Value;
use std::fs;
use std::os::unix::fs::PermissionsExt;
use std::path::Path;
use std::process::{Command, Output};
use tempfile::TempDir;

fn cli(args: &[&str]) -> Output {
    Command::new(env!("CARGO_BIN_EXE_oxide-test"))
        .args(args)
        .output()
        .unwrap()
}

fn script(dir: &Path, body: &str) -> String {
    let path = dir.join("candidate with ' spaces");
    fs::write(&path, format!("#!/bin/sh\n{body}\n")).unwrap();
    fs::set_permissions(&path, fs::Permissions::from_mode(0o755)).unwrap();
    path.to_str().unwrap().to_owned()
}

fn report(args: &[&str]) -> (Output, Value) {
    let mut args = args.to_vec();
    args.push("--json");
    let output = cli(&args);
    let json = serde_json::from_slice(&output.stdout)
        .unwrap_or_else(|e| panic!("{e}: stdout={:?} stderr={:?}", output.stdout, output.stderr));
    (output, json)
}

#[test]
fn lists_challenges_and_individual_rle_cases() {
    let output = cli(&["list"]);
    assert!(output.status.success());
    for id in ["001-wc", "002-ppm", "003-rle"] {
        assert!(String::from_utf8_lossy(&output.stdout).contains(id));
    }
    let (_, json) = report(&["list", "003-rle"]);
    let cases = json["cases"].as_array().unwrap();
    assert!(cases.len() > 50);
    assert!(cases.iter().any(|c| c["id"] == "encode-run-256"));
    assert!(
        cases
            .iter()
            .any(|c| c["id"] == "decode-incomplete-after-prefix")
    );
}

#[test]
fn catalog_and_embedded_vectors_cover_every_definition() {
    let (_, json) = report(&["list"]);
    let catalog = json["challenges"].as_array().unwrap();
    let root = Path::new(env!("CARGO_MANIFEST_DIR")).join("../..");
    let mut definitions: Vec<_> = fs::read_dir(&root)
        .unwrap()
        .map(|entry| entry.unwrap().path())
        .filter(|path| path.join("index.md").is_file())
        .map(|path| path.file_name().unwrap().to_str().unwrap().to_owned())
        .collect();
    definitions.sort();
    let identifiers: Vec<_> = catalog
        .iter()
        .map(|item| item["id"].as_str().unwrap())
        .collect();
    // Cada definição tem cobertura declarada, inclusive rascunhos e APIs sem CLI.
    let policy: Value =
        serde_json::from_slice(&fs::read(root.join("docs/verification-policy.json")).unwrap())
            .unwrap();
    let registered: Vec<_> = policy.as_object().unwrap().keys().cloned().collect();
    assert_eq!(registered, definitions);
    let embedded: Vec<_> = policy
        .as_object()
        .unwrap()
        .iter()
        .filter(|(_, entry)| entry["mode"] == "embedded")
        .map(|(id, _)| id.as_str())
        .collect();
    assert_eq!(identifiers, embedded);
    let policy_check = Command::new("python3")
        .arg(root.join("tools/verification_policy.py"))
        .output()
        .unwrap();
    assert!(
        policy_check.status.success(),
        "{}",
        String::from_utf8_lossy(&policy_check.stderr)
    );
    assert!(identifiers.len() >= 21);
    for id in identifiers {
        let (output, listing) = report(&["list", id]);
        assert!(output.status.success(), "{id}: {listing}");
        let cases = listing["cases"].as_array().unwrap();
        assert!(!cases.is_empty(), "{id}");
        let vector_path = root.join(id).join("tests/cases.json");
        {
            let vectors: Value = serde_json::from_slice(&fs::read(vector_path).unwrap()).unwrap();
            let source_ids: Vec<_> = vectors["cases"]
                .as_array()
                .unwrap()
                .iter()
                .map(|c| c["id"].as_str().unwrap())
                .collect();
            let embedded_ids: Vec<_> = cases.iter().map(|c| c["id"].as_str().unwrap()).collect();
            assert_eq!(source_ids, embedded_ids, "{id}");
        }
    }
}

#[test]
fn embedded_binary_file_case_runs_outside_checkout_without_python() {
    // Independently compiled echo candidate for one file-mode hexdump vector.
    // It doesn't implement the challenge: it isolates the runner's file staging.
    let dir = TempDir::new().unwrap();
    let manifest: Value = serde_json::from_slice(
        &fs::read(concat!(
            env!("CARGO_MANIFEST_DIR"),
            "/../../004-hexdump/tests/cases.json"
        ))
        .unwrap(),
    )
    .unwrap();
    let case = manifest["cases"]
        .as_array()
        .unwrap()
        .iter()
        .find(|case| case["input_file"] == true && case["stdout_hex"].is_string())
        .unwrap();
    let input = case["stdin_hex"].as_str().unwrap();
    let expected = case["stdout_hex"].as_str().unwrap();
    fn literals(hex: &str) -> String {
        if hex.is_empty() {
            return "0".into();
        }
        (0..hex.len())
            .step_by(2)
            .map(|i| format!("0x{}", &hex[i..i + 2]))
            .collect::<Vec<_>>()
            .join(",")
    }
    let source = format!(
        r#"
        #include <stdio.h>
        int main(int argc, char **argv) {{
            const unsigned char input[] = {{{}}}, output[] = {{{}}};
            if (argc != 2 || getchar() != EOF) return 1;
            FILE *f = fopen(argv[1], "rb"); if (!f) return 2;
            for (unsigned i = 0; i < {}; i++) if (fgetc(f) != input[i]) return 3;
            if (fgetc(f) != EOF || fclose(f)) return 4;
            return fwrite(output, 1, {}, stdout) != {} || fflush(stdout);
        }}
    "#,
        literals(input),
        literals(expected),
        input.len() / 2,
        expected.len() / 2,
        expected.len() / 2
    );
    let source_path = dir.path().join("candidate.c");
    let candidate = dir.path().join("candidate");
    fs::write(&source_path, source).unwrap();
    let built = Command::new("cc")
        .arg(source_path)
        .arg("-o")
        .arg(&candidate)
        .output()
        .unwrap();
    assert!(
        built.status.success(),
        "{}",
        String::from_utf8_lossy(&built.stderr)
    );
    let output = Command::new(env!("CARGO_BIN_EXE_oxide-test"))
        .current_dir(dir.path())
        .env("PATH", "")
        .args([
            "run",
            "004-hexdump",
            "./candidate",
            "--case",
            case["id"].as_str().unwrap(),
            "--json",
        ])
        .output()
        .unwrap();
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stdout)
    );
}

#[test]
fn selected_wc_case_accepts_program_with_spaces_and_embeds_fixtures() {
    let dir = TempDir::new().unwrap();
    let path = script(dir.path(), "printf '0 1 5\\n'");
    let (output, json) = report(&["run", "001-wc", &path, "--case", "sem-quebra"]);
    assert_eq!(output.status.code(), Some(0), "{json}");
    assert_eq!(json["summary"]["passed"], 1);
    assert_eq!(json["summary"]["selected"], 1);
    assert_eq!(json["all_public_tests_passed"], false);
    assert_eq!(json["results"][0]["status"], "passed");
    assert!(json["test_revision"].as_str().is_some());
    let rerun = json["results"][0]["rerun"].as_str().unwrap();
    // Execute the rendered hint, proving quotes survive a shell round trip.
    let output = Command::new("sh")
        .args(["-c", rerun])
        .env(
            "PATH",
            format!(
                "{}:/usr/bin:/bin",
                Path::new(env!("CARGO_BIN_EXE_oxide-test"))
                    .parent()
                    .unwrap()
                    .display()
            ),
        )
        .output()
        .unwrap();
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
}

#[test]
fn wrong_output_has_a_diff_and_failure_summary() {
    let dir = TempDir::new().unwrap();
    let path = script(dir.path(), "printf '1 1 5\\n'");
    let (output, json) = report(&["run", "001-wc", &path, "--case", "sem-quebra"]);
    assert_eq!(output.status.code(), Some(1));
    assert_eq!(json["results"][0]["category"], "wrong_output");
    assert!(
        json["results"][0]["message"]
            .as_str()
            .unwrap()
            .contains("offset 0")
    );
    let text = cli(&["run", "001-wc", &path, "--case", "sem-quebra"]);
    let text = String::from_utf8(text.stdout).unwrap();
    assert!(text.contains("FAIL"));
    assert!(text.contains("Expected"));
    assert!(text.contains("Received"));
}

#[test]
fn fail_fast_reports_unexecuted_checks() {
    let dir = TempDir::new().unwrap();
    let path = script(dir.path(), "printf 'wrong\\n'");
    let (output, json) = report(&["run", "001-wc", &path, "--fail-fast"]);
    assert_eq!(output.status.code(), Some(1));
    assert_eq!(json["summary"]["executed"], 1);
    assert!(json["summary"]["not_run"].as_u64().unwrap() > 0);
    assert_eq!(json["all_public_tests_passed"], false);
}

#[test]
fn rejects_bad_selection_and_timeout_without_running_program() {
    let dir = TempDir::new().unwrap();
    let marker = dir.path().join("ran");
    let path = script(dir.path(), &format!("touch '{}'", marker.display()));
    for tail in [
        vec!["--case", "absent"],
        vec!["--timeout", "0"],
        vec!["--timeout", "nan"],
        vec!["--timeout", "inf"],
        vec!["--timeout", "1e100"],
    ] {
        let mut args = vec!["run", "001-wc", &path];
        args.extend(tail);
        let (output, json) = report(&args);
        assert_eq!(output.status.code(), Some(2));
        assert!(json["error"].is_object());
        assert!(!marker.exists());
    }
}

#[test]
fn reports_launch_exit_timeout_and_output_limit_separately() {
    let dir = TempDir::new().unwrap();
    let absent = dir.path().join("absent");
    let (output, json) = report(&["run", "001-wc", absent.to_str().unwrap()]);
    assert_eq!(output.status.code(), Some(2));
    assert_eq!(json["error"]["category"], "launch_error");
    for (body, category) in [
        ("exit 42", "unexpected_exit"),
        ("exec sleep 10", "timeout"),
        ("exec 1>&- 2>&-; exec sleep 10", "timeout"),
        ("exec yes x", "output_limit"),
        ("exec yes x >&2", "output_limit"),
    ] {
        let path = script(dir.path(), body);
        let (output, json) = report(&[
            "run",
            "001-wc",
            &path,
            "--case",
            "vazio",
            "--timeout",
            "0.15",
        ]);
        assert_eq!(output.status.code(), Some(1), "{body}: {json}");
        assert_eq!(json["results"][0]["category"], category, "{body}: {json}");
    }
}

fn compile(dir: &Path, challenge: u8, mutation: u8) -> String {
    let path = dir.join(format!("reference-{challenge}-{mutation}"));
    let result = Command::new("cc")
        .args(["-std=c11", "-O2", "-Wall", "-Wextra", "-Werror"])
        .arg(format!("-DCHALLENGE={challenge}"))
        .arg(format!("-DMUTATION={mutation}"))
        .arg(concat!(
            env!("CARGO_MANIFEST_DIR"),
            "/tests/candidates/reference.c"
        ))
        .arg("-o")
        .arg(&path)
        .output()
        .unwrap();
    assert!(
        result.status.success(),
        "{}",
        String::from_utf8_lossy(&result.stderr)
    );
    path.to_str().unwrap().to_owned()
}

#[test]
fn all_suites_accept_correct_real_programs_and_reject_mutants() {
    let dir = TempDir::new().unwrap();
    for (challenge, number) in [("001-wc", 1), ("002-ppm", 2), ("003-rle", 3)] {
        let path = compile(dir.path(), number, 0);
        let (output, json) = report(&["run", challenge, &path]);
        assert_eq!(output.status.code(), Some(0), "{challenge}: {json}");
        assert_eq!(json["all_public_tests_passed"], true);
        assert_eq!(json["summary"]["skipped"], 0);
        // The existing public suite must agree on this independently compiled candidate.
        let old = Command::new("python3")
            .arg(format!(
                "{}/../../{challenge}/tests/test.py",
                env!("CARGO_MANIFEST_DIR")
            ))
            .arg(&path)
            .output()
            .unwrap();
        assert!(
            old.status.success(),
            "{}",
            String::from_utf8_lossy(&old.stderr)
        );

        let path = compile(dir.path(), number, 1);
        let (output, json) = report(&["run", challenge, &path, "--fail-fast"]);
        assert_eq!(output.status.code(), Some(1), "{challenge}: {json}");
        let old = Command::new("python3")
            .arg(format!(
                "{}/../../{challenge}/tests/test.py",
                env!("CARGO_MANIFEST_DIR")
            ))
            .arg(path)
            .output()
            .unwrap();
        assert!(!old.status.success());
    }
}

#[test]
fn relative_program_runs_outside_checkout_without_python() {
    let dir = TempDir::new().unwrap();
    let path = compile(dir.path(), 1, 0);
    let output = Command::new(env!("CARGO_BIN_EXE_oxide-test"))
        .current_dir(dir.path())
        .env("PATH", "")
        .args([
            "run",
            "001-wc",
            Path::new(&path).file_name().unwrap().to_str().unwrap(),
            "--json",
        ])
        .output()
        .unwrap();
    assert_eq!(
        output.status.code(),
        Some(0),
        "{}",
        String::from_utf8_lossy(&output.stdout)
    );
}

#[test]
fn invalid_executable_format_is_a_setup_error() {
    let dir = TempDir::new().unwrap();
    let path = dir.path().join("not really a binary");
    fs::write(&path, b"invalid executable format\0").unwrap();
    fs::set_permissions(&path, fs::Permissions::from_mode(0o755)).unwrap();
    let (output, json) = report(&["run", "001-wc", path.to_str().unwrap()]);
    assert_eq!(output.status.code(), Some(2), "{json}");
    assert_eq!(json["error"]["category"], "launch_error");
}

#[test]
fn repeated_case_selection_runs_each_case_once() {
    let dir = TempDir::new().unwrap();
    let path = script(dir.path(), "printf '0 0 0\\n'");
    let (output, json) = report(&["run", "001-wc", &path, "--case", "vazio", "--case", "vazio"]);
    assert_eq!(output.status.code(), Some(0));
    assert_eq!(json["summary"]["executed"], 1);
}

#[test]
fn ppm_mismatch_reports_pixel_and_channel() {
    let dir = TempDir::new().unwrap();
    let path = compile(dir.path(), 2, 1);
    let (output, json) = report(&["run", "002-ppm", &path, "--case", "image"]);
    assert_eq!(output.status.code(), Some(1));
    let message = json["results"][0]["message"].as_str().unwrap();
    assert!(message.contains("Pixel (0, 0), channel B"));
    assert!(message.contains("offset 17"));
}

#[test]
fn whitespace_only_diagnostic_including_vertical_tab_is_rejected() {
    let dir = TempDir::new().unwrap();
    let path = script(dir.path(), "printf '\\013' >&2; exit 1");
    let (output, json) = report(&["run", "003-rle", &path, "--case", "args-missing"]);
    assert_eq!(output.status.code(), Some(1));
    assert_eq!(json["results"][0]["category"], "wrong_output");
}

#[test]
fn non_utf8_program_path_has_a_lossless_rerun() {
    use std::ffi::OsString;
    use std::os::unix::ffi::OsStringExt;
    let dir = TempDir::new().unwrap();
    let original = compile(dir.path(), 1, 0);
    let path = dir
        .path()
        .join(OsString::from_vec(b"candidate-\xff\n".to_vec()));
    fs::rename(original, &path).unwrap();
    let output = Command::new(env!("CARGO_BIN_EXE_oxide-test"))
        .args(["run", "001-wc"])
        .arg(&path)
        .args(["--case", "sem-quebra", "--json"])
        .output()
        .unwrap();
    assert!(output.status.success());
    let json: Value = serde_json::from_slice(&output.stdout).unwrap();
    let rerun = json["results"][0]["rerun"].as_str().unwrap();
    let output = Command::new("bash")
        .args(["-c", rerun])
        .env(
            "PATH",
            format!(
                "{}:/usr/bin:/bin",
                Path::new(env!("CARGO_BIN_EXE_oxide-test"))
                    .parent()
                    .unwrap()
                    .display()
            ),
        )
        .output()
        .unwrap();
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    assert!(
        json["program_bytes_hex"]
            .as_str()
            .unwrap()
            .ends_with("ff0a")
    );
}

#[test]
fn roundtrip_checks_decode_after_exact_encode() {
    let dir = TempDir::new().unwrap();
    // Encode is independently correct. Each failure can only come from decode,
    // including its own timeout and output limit rather than the first phase.
    for (decode, category) in [
        ("printf x", "wrong_output"),
        ("printf wrong", "output_limit"),
        ("exit 42", "unexpected_exit"),
        ("exec sleep 10", "timeout"),
    ] {
        let path = script(
            dir.path(),
            &format!("if [ \"$1\" = encode ]; then printf '\\001\\303'; else {decode}; fi"),
        );
        let (output, json) = report(&[
            "run",
            "003-rle",
            &path,
            "--case",
            "roundtrip-1",
            "--timeout",
            "0.15",
        ]);
        assert_eq!(output.status.code(), Some(1), "{json}");
        assert_eq!(json["results"][0]["category"], category, "{json}");
    }
}

#[test]
fn roundtrip_requires_the_known_encoding_before_decoding() {
    let dir = TempDir::new().unwrap();
    // This pair of operations composes to the original byte while using an
    // incorrect representation; a composition-only check would accept it.
    let path = script(
        dir.path(),
        "if [ \"$1\" = encode ]; then printf xx; else printf '\\303'; fi",
    );
    let (output, json) = report(&["run", "003-rle", &path, "--case", "roundtrip-1"]);
    assert_eq!(output.status.code(), Some(1), "{json}");
    assert_eq!(json["results"][0]["category"], "wrong_output");
}
