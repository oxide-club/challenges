use clap::{Parser, Subcommand};
use std::path::PathBuf;

#[derive(Parser)]
#[command(
    name = "oxide-test",
    version,
    about = "Test your program against Oxide Club's public challenges"
)]
pub struct Cli {
    /// Emit a versioned JSON document instead of terminal output
    #[arg(long, global = true)]
    pub json: bool,
    #[command(subcommand)]
    pub command: Action,
}

#[derive(Subcommand)]
pub enum Action {
    /// List challenges, or list stable case IDs for one challenge
    List { challenge: Option<String> },
    /// Run a challenge suite against your compiled executable
    Run {
        challenge: String,
        program: PathBuf,
        /// Run only this case (repeat to select several)
        #[arg(long = "case", value_name = "ID")]
        cases: Vec<String>,
        /// Stop after the first failed case
        #[arg(long)]
        fail_fast: bool,
        /// Seconds per program invocation, greater than 0 and at most 86400
        #[arg(long, default_value = "5", value_parser = timeout)]
        timeout: f64,
    },
}

fn timeout(value: &str) -> Result<f64, String> {
    let n: f64 = value.parse().map_err(|_| "Timeout must be a number")?;
    if !n.is_finite() || n <= 0.0 || n > 86400.0 || n < 1e-9 {
        return Err(
            "Timeout must be finite, at least 0.000000001 and at most 86400 seconds".into(),
        );
    }
    Ok(n)
}
