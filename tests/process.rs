#![cfg(target_os = "linux")]

use oxide_test::process::{IoMode, Request, execute};
use oxide_test::report::Category;
use std::path::Path;
use std::time::{Duration, Instant};
use tempfile::TempDir;

fn request(input: &[u8], limit: usize) -> Request<'_> {
    Request {
        input,
        argv: &[],
        timeout: Duration::from_secs(2),
        output_limit: limit,
        io: IoMode::Normal,
    }
}

#[test]
fn concurrently_feeds_and_drains_more_than_pipe_capacity() {
    let data = b"binary\x00\xff\n".repeat(131072);
    let result = execute(Path::new("/bin/cat"), request(&data, data.len())).unwrap();
    assert!(result.status.success());
    assert_eq!(result.stdout, data);
}

#[test]
fn kills_descendants_after_success_even_when_they_close_all_pipes() {
    let dir = TempDir::new().unwrap();
    let marker = dir.path().join("survived");
    let args = vec![
        "-c".into(),
        format!(
            "(sleep 0.15; touch '{}') </dev/null >/dev/null 2>&1 &\nexit 0\n",
            marker.display()
        ),
    ];
    let mut request = request(b"", 1024);
    request.argv = &args;
    let result = execute(Path::new("/bin/sh"), request).unwrap();
    assert!(result.status.success());
    std::thread::sleep(Duration::from_millis(250));
    assert!(
        !marker.exists(),
        "background descendant survived a successful invocation"
    );
}

#[test]
fn inherited_pipes_cannot_bypass_timeout_and_descendants_are_killed() {
    let dir = TempDir::new().unwrap();
    let marker = dir.path().join("survived");
    let args = vec![
        "-c".into(),
        format!("(sleep 0.2; touch '{}') &\nexit 0\n", marker.display()),
    ];
    let mut request = request(b"", 1024);
    request.argv = &args;
    request.timeout = Duration::from_millis(50);
    let start = Instant::now();
    let error = execute(Path::new("/bin/sh"), request).err().unwrap();
    assert_eq!(error.category, Category::Timeout);
    assert!(start.elapsed() < Duration::from_secs(2));
    std::thread::sleep(Duration::from_millis(300));
    assert!(!marker.exists());
}

#[test]
fn preserves_empty_arguments_and_arguments_with_spaces() {
    let args = vec!["%s|%s".into(), "".into(), "a b".into()];
    let mut request = request(b"", 1024);
    request.argv = &args;
    let result = execute(Path::new("/usr/bin/printf"), request).unwrap();
    assert_eq!(result.stdout, b"|a b");
}
