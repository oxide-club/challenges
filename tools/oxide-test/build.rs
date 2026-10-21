use std::{path::PathBuf, process::Command};

fn main() {
    println!("cargo:rerun-if-env-changed=OXIDE_TEST_REVISION");
    let root = PathBuf::from(std::env::var_os("CARGO_MANIFEST_DIR").unwrap()).join("../..");
    println!("cargo:rerun-if-changed=src");
    // git-path also handles linked worktrees, whose .git is a pointer file.
    for entry in ["HEAD", "refs", "packed-refs", "index"] {
        if let Ok(output) = Command::new("git")
            .current_dir(&root)
            .args(["rev-parse", "--git-path", entry])
            .output()
        {
            if output.status.success() {
                let path = PathBuf::from(String::from_utf8_lossy(&output.stdout).trim());
                let path = if path.is_absolute() {
                    path
                } else {
                    root.join(path)
                };
                println!("cargo:rerun-if-changed={}", path.display());
            }
        }
    }
    if let Ok(entries) = std::fs::read_dir(&root) {
        for entry in entries.flatten() {
            let suite = entry.path().join("tests/cases.json");
            if suite.is_file() {
                println!("cargo:rerun-if-changed={}", suite.display());
            }
        }
    }
    let revision = std::env::var("OXIDE_TEST_REVISION").unwrap_or_else(|_| {
        let head = Command::new("git")
            .current_dir(&root)
            .args(["rev-parse", "HEAD"])
            .output()
            .ok()
            .filter(|o| o.status.success())
            .map(|o| String::from_utf8_lossy(&o.stdout).trim().to_owned())
            .unwrap_or_else(|| "unknown".into());
        let dirty = Command::new("git")
            .current_dir(&root)
            .args(["status", "--porcelain", "--untracked-files=normal"])
            .output()
            .ok()
            .is_some_and(|o| o.status.success() && !o.stdout.is_empty());
        format!("{head}{}", if dirty { "-dirty" } else { "" })
    });
    println!("cargo:rustc-env=OXIDE_TEST_REVISION={revision}");
}
