# E0 — llama.cpp b11259 Windows CUDA 12.4 runtime

## Hypothesis / target
The official b11259 Windows x64 CUDA 12.4 binary should match commit `d280808f5` and execute `--version` and `--list-devices` when launched from its extracted directory (DLL directory on PATH).

## Official release inspection
- Release: [llama.cpp b11259](https://github.com/ggml-org/llama.cpp/releases/tag/b11259)
- Release API: https://api.github.com/repos/ggml-org/llama.cpp/releases/tags/b11259
- `target_commitish`: `d280808f5d82fcc3142b53f94ea5f594250cd765`
- Selected asset: `llama-b11259-bin-win-cuda-12.4-x64.zip`
- Asset URL: https://github.com/ggml-org/llama.cpp/releases/download/b11259/llama-b11259-bin-win-cuda-12.4-x64.zip
- Official asset size: 264,528,828 bytes
- Official API digest: `sha256:4f0551811b6e836344a90176583031f9ac0fe258359eb3f0bc94c81a88087cd5`
- Local SHA-256: `4F0551811B6E836344A90176583031F9AC0FE258359EB3F0BC94C81A88087CD5` (matches)
- Downloaded file: `runtimes/llama-b11259-bin-win-cuda-12.4-x64.zip`
- Extracted directory: `runtimes/llama-b11259-cuda124`
- Runtime-only asset selected; no model asset was downloaded.

## Runtime command and exact output
Working directory / DLL directory: `runtimes/llama-b11259-cuda124` (prepended to `PATH`).

Command:
```powershell
$d=(Resolve-Path 'runtimes/llama-b11259-cuda124').Path
$env:PATH="$d;"+$env:PATH
& "$d/llama-cli.exe" --version
& "$d/llama-cli.exe" --list-devices
```

Combined captured result (stdout/stderr):
```text
Available devices:
  (none)
version: 0.5.0-dev (build 11259, commit d280808f5)
built with Clang 20.1.8 for Windows x86_64
```

Exit codes: `--version=0`, `--list-devices=0`.

## Existing b11259 directory check
The pre-existing `runtimes/llama.cpp-release` directory was also tested with that directory prepended to `PATH`:

```text
version: 0.5.0-dev (build 11259, commit d280808f5)
built with Clang 20.1.8 for Windows x86_64
Available devices:
  (none)
```

Exit codes: `--version=0`, `--list-devices=0`.

## Result
The official CUDA 12.4 Windows x64 asset is available, downloaded, hash-verified, extracted separately, and matches the requested b11259 commit. Both runtime directories execute successfully but report no CUDA devices in this environment (`(none)`).
