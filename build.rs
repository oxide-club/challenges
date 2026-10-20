use std::process::Command;

fn main() {
    println!("cargo:rerun-if-env-changed=OXIDE_TEST_REVISION");
    println!("cargo:rerun-if-changed=.git/HEAD");
    println!("cargo:rerun-if-changed=.git/refs");
    println!("cargo:rerun-if-changed=src");
    println!("cargo:rerun-if-changed=001-wc/fixtures");
    let revision = std::env::var("OXIDE_TEST_REVISION").unwrap_or_else(|_| {
        let head = Command::new("git")
            .args(["rev-parse", "HEAD"])
            .output()
            .ok()
            .filter(|o| o.status.success())
            .map(|o| String::from_utf8_lossy(&o.stdout).trim().to_owned())
            .unwrap_or_else(|| "unknown".into());
        let dirty = Command::new("git")
            .args(["status", "--porcelain", "--untracked-files=normal"])
            .output()
            .ok()
            .is_some_and(|o| o.status.success() && !o.stdout.is_empty());
        format!("{head}{}", if dirty { "-dirty" } else { "" })
    });
    println!("cargo:rustc-env=OXIDE_TEST_REVISION={revision}");
}
