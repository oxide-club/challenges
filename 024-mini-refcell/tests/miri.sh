#!/bin/sh
# SPDX-License-Identifier: MIT
# Execute na raiz do pacote; a detecção de vazamentos permanece habilitada.
set -eu
channel=${MIRI_TOOLCHAIN:-nightly}
if [ "${MIRI_DIRECT:-0}" = 1 ]; then
    set -- cargo miri
else
    set -- cargo +"$channel" miri
fi
if ! "$@" --version; then
    echo "INDISPONÍVEL: instale rustup toolchain install $channel --component miri,rust-src" >&2
    exit 77
fi
exec "$@" test --offline --test contract
