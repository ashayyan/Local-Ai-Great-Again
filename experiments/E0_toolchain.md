# E0 toolchain — official llama.cpp Windows CUDA Route A

## Hypothesis / target
Acquire the cheapest official llama.cpp Windows CUDA x64 release, without model weights, and verify executable help for Qwen3.5 (`qwen35`) and speculative MTP (`--spec-type draft-mtp`). Target: a release zip under 200 MB with a runnable CUDA CLI.

## Metadata-first acquisition
- Repository: https://github.com/ggml-org/llama.cpp
- Latest stable metadata URL queried: https://api.github.com/repos/ggml-org/llama.cpp/releases/latest
  - Returned tag `v0.5.0`; its listed assets contained only `nightly-tag.txt`, so no Windows CUDA binary was available through that stable release metadata.
- Release list queried: https://api.github.com/repos/ggml-org/llama.cpp/releases?per_page=10
- Selected official prerelease/nightly release: `b11259`
- Release API: https://api.github.com/repos/ggml-org/llama.cpp/releases/tags/b11259
- Release page: https://github.com/ggml-org/llama.cpp/releases/tag/b11259
- Assets API: https://api.github.com/repos/ggml-org/llama.cpp/releases/399364719/assets

Selected asset:
- Name: `llama-b11259-bin-win-cuda-13.4-x64.zip`
- Exact URL: https://github.com/ggml-org/llama.cpp/releases/download/b11259/llama-b11259-bin-win-cuda-13.4-x64.zip
- GitHub API size: 153,546,058 bytes (146.4 MiB), reasonable against 193.57 GB free on C: before download.
- GitHub API digest: `sha256:7e93d79ed0dfacb67a7a5448eab38b60511ec3ad623022259b08490d5cf01404`
- Downloaded local archive: `runtimes/llama-b11259-win-cuda-13.4-x64.zip`
- Local SHA-256: `7E93D79ED0DFAC67A7A5448EAB38B60511EC3AD623022259B08490D5CF01404` (matches API digest)
- Extracted to: `runtimes/llama.cpp-release/`
- No model weights downloaded.

Alternative asset considered:
- `cudart-llama-bin-win-cuda-13.4-x64.zip`, API size 423,535,356 bytes, digest `sha256:738f8c251ac22b70c3ae6f83a10cf222725df0395246a2cf58f32bdb85fbe668`; not selected because the 153.5 MB `llama-b...` package is substantially smaller.
- CUDA 12.4 binary also existed (`llama-b11259-bin-win-cuda-12.4-x64.zip`, 264,528,828 bytes, digest `sha256:4f0551811b6e836344a90176583031f9ac0fe258359eb3f0bc94c81a88087cd5`). CUDA 13.4 selected for smallest official x64 binary and current driver compatibility.

## Verification outputs
Command:
```powershell
& "runtimes/llama.cpp-release/llama-cli.exe" --version
```
Output:
```text
version: 0.5.0-dev (build 11259, commit d280808f5)
built with Clang 20.1.8 for Windows x86_64
```

Command:
```powershell
& "runtimes/llama.cpp-release/llama-cli.exe" --help
```
Relevant output:
```text
--spec-type none,draft-simple,draft-eagle3,draft-mtp,draft-dflash,draft-dspark,ngram-simple,ngram-map-k,ngram-map-k4v,ngram-mod,ngram-cache
```
Thus `--spec-type draft-mtp` is explicitly accepted by this binary's help.

Qwen3.5 architecture checks:
- `llama-cli --help` does not enumerate model architecture names, therefore no `qwen35` help line was present.
- ASCII scan of every extracted `.exe` and `.dll` found no `qwen35` or `qwen3.5` literal.
- This is not a runtime model-load test because no model weights were downloaded. The release metadata changelog includes qwen35-related tensor-parallel handling (`qwen35`), but executable string inspection did not independently confirm the architecture symbol.

MTP string check:
- ASCII scan found `draft-mtp` in `llama-common.dll`, consistent with the explicit help output.

Environment:
- GPU: NVIDIA GeForce RTX 3050 Laptop GPU
- Driver: 610.62
- C: free space before download: 193.57 GB

## Failure routes / blockers
1. Stable `v0.5.0` latest-release metadata had no Windows CUDA binary asset (only `nightly-tag.txt`), so acquisition continued through official release-list metadata to `b11259`.
2. The official Windows CUDA `cudart` package was available but 423,535,356 bytes; the smaller 153,546,058-byte `llama-b...` package was selected.
3. `qwen35` was not discoverable in `--help` or ASCII strings. Exact blocker: this verification method cannot prove architecture support without a compatible GGUF model load; model weights were intentionally not downloaded. Next experiment: load a separately acquired Qwen3.5 GGUF with `llama-cli --model ... --help`/startup metadata and record success or exact loader error.

## Status / Numbers / Next Experiment
**Status:** Official Windows CUDA runtime acquired and hash-verified; no weights acquired. `draft-mtp` confirmed by help. `qwen35` not independently confirmed by strings/help.

**Numbers:** 153,546,058-byte zip; SHA-256 `7e93d79ed0dfacb67a7a5448eab38b60511ec3ad623022259b08490d5cf01404`; 193.57 GB free at acquisition; version build 11259 / commit d280808f5.

**Next Experiment:** With a Qwen3.5 GGUF already available (or when separately approved), run `runtimes/llama.cpp-release/llama-cli.exe -m <qwen35.gguf> --spec-type draft-mtp --help` and a minimal load test, without changing this toolchain.
