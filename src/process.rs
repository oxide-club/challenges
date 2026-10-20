//! Bounded Linux subprocess execution. This is not a security sandbox.
use crate::report::{Category, Failure};
use std::fs::File;
use std::io::{self, Read, Write};
use std::os::fd::{AsRawFd, FromRawFd};
use std::os::unix::process::CommandExt;
use std::path::Path;
use std::process::{Child, Command, ExitStatus, Stdio};
use std::time::{Duration, Instant};

#[derive(Clone, Copy, Debug)]
pub enum IoMode {
    Normal,
    Full,
    Directory,
    BrokenPipe,
}

pub struct Request<'a> {
    pub input: &'a [u8],
    pub argv: &'a [String],
    pub timeout: Duration,
    pub output_limit: usize,
    pub io: IoMode,
}

pub struct ProcessResult {
    pub status: ExitStatus,
    pub stdout: Vec<u8>,
    pub stderr: Vec<u8>,
}

struct Group(Child);
impl Drop for Group {
    fn drop(&mut self) {
        // SAFETY: process_group(0) gives this child its own group.
        unsafe {
            libc::kill(-(self.0.id() as i32), libc::SIGKILL);
        }
        let _ = self.0.wait();
    }
}

fn nonblocking(stream: &impl AsRawFd) -> Result<(), Failure> {
    // SAFETY: the borrowed descriptor stays live throughout both fcntl calls.
    let flags = unsafe { libc::fcntl(stream.as_raw_fd(), libc::F_GETFL) };
    if flags < 0
        || unsafe { libc::fcntl(stream.as_raw_fd(), libc::F_SETFL, flags | libc::O_NONBLOCK) } < 0
    {
        return Err(Failure::harness(io::Error::last_os_error()));
    }
    Ok(())
}

fn broken_pipe() -> Result<File, Failure> {
    let mut fds = [-1; 2];
    // SAFETY: fds points to space for both returned descriptors.
    if unsafe { libc::pipe2(fds.as_mut_ptr(), libc::O_CLOEXEC) } != 0 {
        return Err(Failure::harness(io::Error::last_os_error()));
    }
    // SAFETY: successful pipe2 transfers these fresh descriptors to two Files.
    let reader = unsafe { File::from_raw_fd(fds[0]) };
    let writer = unsafe { File::from_raw_fd(fds[1]) };
    drop(reader);
    Ok(writer)
}

fn read_stream<R: Read>(
    stream: &mut Option<R>,
    bytes: &mut Vec<u8>,
    limit: usize,
    name: &str,
) -> Result<(), Failure> {
    let Some(reader) = stream.as_mut() else {
        return Ok(());
    };
    let mut buffer = [0; 65536];
    let size = buffer
        .len()
        .min(limit.saturating_sub(bytes.len()).saturating_add(1));
    match reader.read(&mut buffer[..size]) {
        Ok(0) => *stream = None,
        Ok(count) => {
            bytes.extend_from_slice(&buffer[..count]);
            if bytes.len() > limit {
                return Err(Failure::new(
                    Category::OutputLimit,
                    format!("{name} exceeded {limit} bytes"),
                ));
            }
        }
        Err(e)
            if matches!(
                e.kind(),
                io::ErrorKind::WouldBlock | io::ErrorKind::Interrupted
            ) => {}
        Err(e) => return Err(Failure::harness(e)),
    }
    Ok(())
}

pub fn execute(program: &Path, request: Request<'_>) -> Result<ProcessResult, Failure> {
    let mut command = Command::new(program);
    command
        .args(request.argv)
        .process_group(0)
        .stderr(Stdio::piped());
    match request.io {
        IoMode::Directory => {
            command.stdin(File::open("/").map_err(Failure::harness)?);
        }
        _ => {
            command.stdin(Stdio::piped());
        }
    }
    match request.io {
        IoMode::Full => {
            let file = File::options().write(true).open("/dev/full").map_err(|e| {
                if e.kind() == io::ErrorKind::NotFound {
                    Failure::skip("/dev/full is unavailable")
                } else {
                    Failure::harness(e)
                }
            })?;
            command.stdout(file);
        }
        IoMode::BrokenPipe => {
            command.stdout(broken_pipe()?);
        }
        _ => {
            command.stdout(Stdio::piped());
        }
    }
    let started = Instant::now();
    let mut group = Group(
        command
            .spawn()
            .map_err(|e| Failure::launch(e.to_string()))?,
    );
    let mut input = group.0.stdin.take();
    let mut output = group.0.stdout.take();
    let mut error = group.0.stderr.take();
    if let Some(stream) = &input {
        nonblocking(stream)?;
    }
    if let Some(stream) = &output {
        nonblocking(stream)?;
    }
    if let Some(stream) = &error {
        nonblocking(stream)?;
    }
    if request.input.is_empty() {
        input = None;
    }
    let mut position = 0;
    let mut stdout = Vec::new();
    let mut stderr = Vec::new();
    let mut status = None;
    loop {
        if started.elapsed() >= request.timeout {
            return Err(Failure::new(
                Category::Timeout,
                format!("Time limit exceeded ({} s)", request.timeout.as_secs_f64()),
            ));
        }
        if let Some(stream) = &mut input {
            let end = (position + 65536).min(request.input.len());
            match stream.write(&request.input[position..end]) {
                Ok(n) => {
                    position += n;
                    if position == request.input.len() {
                        input = None;
                    }
                }
                Err(e) if e.kind() == io::ErrorKind::BrokenPipe => input = None,
                Err(e)
                    if matches!(
                        e.kind(),
                        io::ErrorKind::WouldBlock | io::ErrorKind::Interrupted
                    ) => {}
                Err(e) => return Err(Failure::harness(e)),
            }
        }
        read_stream(&mut output, &mut stdout, request.output_limit, "stdout")?;
        read_stream(&mut error, &mut stderr, 65536, "stderr")?;
        if status.is_none() {
            status = group.0.try_wait().map_err(Failure::harness)?;
        }
        if let Some(status) = status {
            if input.is_none() && output.is_none() && error.is_none() {
                return Ok(ProcessResult {
                    status,
                    stdout,
                    stderr,
                });
            }
        }
        let mut descriptors = Vec::with_capacity(3);
        if let Some(stream) = &input {
            descriptors.push(libc::pollfd {
                fd: stream.as_raw_fd(),
                events: libc::POLLOUT,
                revents: 0,
            });
        }
        if let Some(stream) = &output {
            descriptors.push(libc::pollfd {
                fd: stream.as_raw_fd(),
                events: libc::POLLIN,
                revents: 0,
            });
        }
        if let Some(stream) = &error {
            descriptors.push(libc::pollfd {
                fd: stream.as_raw_fd(),
                events: libc::POLLIN,
                revents: 0,
            });
        }
        let remaining = request.timeout.saturating_sub(started.elapsed());
        let wait_ms = remaining.as_millis().clamp(1, 10) as i32;
        // SAFETY: descriptors owns valid pollfd entries and all FDs remain open.
        let result = unsafe {
            libc::poll(
                descriptors.as_mut_ptr(),
                descriptors.len() as libc::nfds_t,
                wait_ms,
            )
        };
        if result < 0 && io::Error::last_os_error().kind() != io::ErrorKind::Interrupted {
            return Err(Failure::harness(io::Error::last_os_error()));
        }
    }
}
