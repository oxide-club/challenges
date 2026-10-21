# The toolchains are also available in the final image so participants can
# compile Linux C/Rust submissions without installing compilers on the host.
ARG RUST_IMAGE=rust:1-bookworm
FROM ${RUST_IMAGE} AS build
WORKDIR /build
ARG OXIDE_TEST_REVISION=unknown
ENV OXIDE_TEST_REVISION=${OXIDE_TEST_REVISION}
COPY . .
RUN cargo build --manifest-path tools/oxide-test/Cargo.toml --release --locked

FROM ${RUST_IMAGE} AS runtime
COPY --from=build /build/tools/oxide-test/target/release/oxide-test /usr/local/bin/oxide-test
RUN cc --version && rustc --version
WORKDIR /submission
ENTRYPOINT ["oxide-test"]
CMD ["--help"]
