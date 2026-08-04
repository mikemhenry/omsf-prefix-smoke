# omsf-prefix-smoke

`omsf-prefix-smoke` is a deliberately small `noarch: python` package for testing the complete OMSF package-publication path:

1. Build and test a conda package with Rattler-Build.
2. Authenticate to prefix.dev using GitHub OIDC Repository Access.
3. Publish without a long-lived upload token.
4. Generate a Sigstore package attestation and store it with prefix.dev and GitHub.
5. Confirm that the channel indexes the package and that a clean environment can install it.
6. Produce deterministic, machine-readable evidence that the installed package and its data are intact.

It is intentionally not a scientific application. Keeping the first package pure Python and dependency-light makes failures attributable to the publication pipeline instead of compilers, ABI variants, or GPU runtimes.

## Verification command

```console
$ omsf-prefix-smoke verify --pretty
{
  "data": {
    "path": "data/payload.json",
    "sha256": "...",
    "size": 77
  },
  "dependencies": {
    "packaging": "..."
  },
  "package": {
    "name": "omsf-prefix-smoke",
    "version": "0.1.0"
  },
  "python": {
    "implementation": "CPython",
    "version": "..."
  },
  "schema_version": 1,
  "status": "ok"
}
```

The compact form uses sorted keys and stable separators so that the same installation produces the same bytes. Environment-specific version fields are expected to differ between Python environments.

## Local development

Install [Pixi](https://pixi.sh), then run:

```fish
pixi run check
pixi run build-conda
```

The individual tasks are also available:

```fish
pixi run test
pixi run coverage
pixi run lint
pixi run format-check
pixi run typecheck
pixi run verify
```

A standard Python workflow also works:

```fish
python -m venv .venv
source .venv/bin/activate.fish
python -m pip install -e '.[test]'
python -m pytest -q
omsf-prefix-smoke verify --pretty
```

## prefix.dev setup

Create a public prefix.dev channel. The workflows default to `mmh/omsf-test`; set the repository variable `PREFIX_CHANNEL` to use another channel.

In the channel's **Repository Access** settings, authorize:

- GitHub repository: `mikemhenry/omsf-prefix-smoke`
- Workflow: `.github/workflows/publish.yml`
- Permission: package upload only

Repository Access is OIDC-based, so the workflow does not require a stored prefix.dev API key.

## First publication

1. Push this repository to `mikemhenry/omsf-prefix-smoke`.
2. Confirm that the CI workflow passes.
3. Create and publish a GitHub release tagged `v0.1.0`.
4. The release workflow checks that the tag matches both `pyproject.toml` and the conda recipe.
5. It builds and tests exactly one `.conda` package, generates attestations, and uploads without `--force`.

The workflow refuses to overwrite an existing filename. Publish a new version, or deliberately increment the conda build number, instead of replacing an artifact used by existing lock files.

## Install from the test channel

Create a clean Pixi project and install the package with the OMSF channel ahead of conda-forge:

```fish
mkdir omsf-prefix-smoke-check
cd omsf-prefix-smoke-check
pixi init --channel https://prefix.dev/mmh/omsf-test --channel conda-forge
pixi add omsf-prefix-smoke
pixi run omsf-prefix-smoke verify --pretty
```

For a one-off global installation:

```fish
pixi global install \
  --channel https://prefix.dev/mmh/omsf-test \
  --channel conda-forge \
  omsf-prefix-smoke
omsf-prefix-smoke verify --pretty
```

## Release checklist

For a new version:

1. Update `project.version` in `pyproject.toml`.
2. Update `context.version` in `conda.recipe/recipe.yaml`.
3. Add or update tests as needed.
4. Run `pixi run check` and `pixi run build-conda`.
5. Create the matching GitHub release tag, such as `v0.1.1`.

The package builds from the exact release commit checked out by GitHub Actions. The generated Sigstore attestation binds the resulting conda artifact to that workflow identity and source repository. A later feedstock-style production pipeline can additionally build from an immutable source archive pinned by SHA-256.

## Security scope

This package tests publication mechanics; it is not itself a complete trust policy. Consumers still need the planned TUF metadata, trusted root distribution, lock-file policy, and `omsf-adder` verification path.

Please report security-sensitive issues privately using the instructions in [`SECURITY.md`](SECURITY.md).
