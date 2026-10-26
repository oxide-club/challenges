// SPDX-License-Identifier: MIT
#[derive(Debug, PartialEq, Eq)]
pub enum WriteError {
    WriteZero,
    Syscall(i32),
}
/// Complete a política. O adaptador recebe somente a parte ainda não escrita.
pub fn write_all_with(
    bytes: &[u8],
    mut write: impl FnMut(&[u8]) -> isize,
) -> Result<(), WriteError> {
    let _ = (bytes, &mut write);
    Err(WriteError::Syscall(38)) // TODO: política ainda não implementada.
}
