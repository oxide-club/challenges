#[cfg(not(target_os = "linux"))]
compile_error!("oxide-test currently supports Linux only");

mod cli;

use clap::Parser;
use cli::{Action, Cli};
use oxide_test::{
    challenges,
    report::{Failure, escaped},
};
use serde_json::json;
use std::io::{self, Write};
use std::process::ExitCode;
use std::time::Duration;

fn output(text: &str) -> io::Result<()> {
    let stdout = io::stdout();
    let mut out = stdout.lock();
    out.write_all(text.as_bytes())?;
    out.flush()
}

fn main() -> ExitCode {
    let args = match Cli::try_parse() {
        Ok(args) => args,
        Err(error) => {
            let help = matches!(
                error.kind(),
                clap::error::ErrorKind::DisplayHelp | clap::error::ErrorKind::DisplayVersion
            );
            if !help && std::env::args_os().any(|a| a == "--json") {
                let _ = output(&format!(
                    "{}\n",
                    json!({"schema_version":1, "error":{"category":"usage_error", "message":error.to_string()}})
                ));
            } else {
                let _ = error.print();
            }
            return ExitCode::from(if help { 0 } else { 2 });
        }
    };
    let result: Result<(String, u8), Failure> = (|| match args.command {
        Action::List { challenge } => {
            if let Some(id) = challenge {
                let suite = challenges::suite(&id)
                    .ok_or_else(|| Failure::setup(format!("Unknown challenge: {id}")))?;
                let cases: Vec<_> = suite
                    .cases
                    .iter()
                    .map(|c| json!({"id":c.id, "name":c.name}))
                    .collect();
                Ok((
                    if args.json {
                        format!(
                            "{}\n",
                            json!({"schema_version":1, "challenge":id, "cases":cases})
                        )
                    } else {
                        format!(
                            "{id}\n{}",
                            suite
                                .cases
                                .iter()
                                .map(|c| format!("  {:32} {}\n", c.id, c.name))
                                .collect::<String>()
                        )
                    },
                    0,
                ))
            } else {
                Ok((
                    if args.json {
                        format!(
                            "{}\n",
                            json!({"schema_version":1, "challenges": challenges::CATALOG})
                        )
                    } else {
                        challenges::CATALOG
                            .iter()
                            .map(|c| format!("{:<12} {}\n", c.id, c.name))
                            .collect()
                    },
                    0,
                ))
            }
        }
        Action::Run {
            challenge,
            program,
            cases,
            timeout,
            fail_fast,
        } => {
            let report = oxide_test::run(
                &challenge,
                &program,
                &cases,
                Duration::from_secs_f64(timeout),
                fail_fast,
            )?;
            let code = report.exit_code();
            Ok((
                if args.json {
                    format!(
                        "{}\n",
                        serde_json::to_string_pretty(&report).map_err(Failure::harness)?
                    )
                } else {
                    report.text()
                },
                code,
            ))
        }
    })();
    match result {
        Ok((text, code)) => match output(&text) {
            Ok(()) => ExitCode::from(code),
            Err(e) if e.kind() == io::ErrorKind::BrokenPipe => ExitCode::SUCCESS,
            Err(e) => {
                eprintln!("Unable to write report: {e}");
                ExitCode::from(2)
            }
        },
        Err(error) => {
            if args.json {
                let _ = output(&format!(
                    "{}\n",
                    json!({"schema_version":1, "error": error})
                ));
            } else {
                eprintln!("Error: {}", escaped(&error.message));
            }
            ExitCode::from(2)
        }
    }
}
