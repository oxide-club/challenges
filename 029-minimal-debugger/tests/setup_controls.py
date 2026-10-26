#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Controles da classificação de preparação; não simulam uma sessão ptrace."""
import pathlib, subprocess, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]


def main():
    source = r"""
#define main supervisor_main
#include "notify_ptrace.c"
#undef main
int main(void) {
    int absent[]={EPERM,EACCES,ENOSYS,EOPNOTSUPP};
    for (unsigned i=0;i<sizeof(absent)/sizeof(absent[0]);++i) {
        errno=absent[i];if(seccomp_setup_error("consulta seccomp",0)!=77)return 1;
        errno=absent[i];if(seccomp_setup_error("instalação seccomp",1)!=77)return 2;
    }
    errno=EINVAL;if(seccomp_setup_error("consulta seccomp",0)!=77)return 7;
    errno=EINVAL;if(seccomp_setup_error("instalação seccomp",1)!=125)return 8;
    errno=EBUSY;if(seccomp_setup_error("instalação seccomp",1)!=77)return 3;
    errno=EBUSY;if(seccomp_setup_error("consulta seccomp",0)!=125)return 4;
    errno=ENOMEM;if(seccomp_setup_error("instalação seccomp",1)!=125)return 5;
    errno=EINVAL;if(setup_error("outra preparação")!=125)return 6;
    return 0;
}
"""
    with tempfile.TemporaryDirectory(prefix="ox-notify-controls-") as tmp:
        c = pathlib.Path(tmp) / "controls.c"
        exe = c.with_suffix("")
        c.write_text(source)
        subprocess.run(
            [
                "cc",
                "-std=c11",
                "-Wall",
                "-Wextra",
                "-Werror",
                "-I",
                str(ROOT / "tests"),
                str(c),
                "-o",
                str(exe),
            ],
            check=True,
        )
        subprocess.run(
            [str(exe)], check=True, capture_output=True, text=True, timeout=5
        )
    print(
        "PASS classificação de instalação seccomp; EBUSY restrito ao listener e erros distintos preservados"
    )


if __name__ == "__main__":
    main()
