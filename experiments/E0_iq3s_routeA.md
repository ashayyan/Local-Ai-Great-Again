# E0 IQ3_S Route A acquisition

## Hypothesis / target
A trusted, parallel aria2 transfer from the exact Hugging Face resolve URL can acquire the unchanged IQ3_S artifact resumably. Target: exactly 12,040,883,104 bytes and SHA-256 `d847e2c1e4aa276e4b7b8e9ad7628050e61e165d49ab995407bc36677a6f3864`.

## Tooling and integrity control
`aria2c` 1.37.0 was installed through the trusted `aria2.aria2` winget package. Script: `scripts/s18_aria2_iq3s.ps1`. The first full transfer used integrity checking disabled and reached the expected byte count but produced SHA `172f90b5...`; that artifact was discarded. The script was corrected to pass `--check-integrity=true` and `--checksum=sha-256=<expected>` before retrying.

## Exact verified transfer
- URL: `https://huggingface.co/unsloth/Qwen3.8-27B-GGUF/resolve/main/Qwen3.8-27B-UD-IQ3_S.gguf`
- Output: `models/ignored/Qwen3.8-27B-UD-IQ3_S.gguf`
- Connections/splits: 16; resumable; file allocation none; 10,800-second maximum window
- Corrected run: 2026-09-29 18:39:29Z–18:46:33Z
- Downloaded bytes: **12,040,883,104**
- Verified SHA-256: **d847e2c1e4aa276e4b7b8e9ad7628050e61e165d49ab995407bc36677a6f3864**
- Route-A manifest status: **verified**; `.aria2` state removed
- Script-reported average including final checksum pass: **28.080344 MiB/s**; aria2 transfer display was approximately 41 MiB/s before verification.

## Status / Numbers / Next Experiment
- **Status:** Exact IQ3_S artifact is acquired and checksum-verified. It is still outside Git under ignored `models/`; no inference has been run.
- **Numbers:** 12,040,883,104/12,040,883,104 bytes; SHA exact; 16 connections; 28.080344 MiB/s end-to-end including verification; first unverified attempt SHA mismatch was discarded.
- **Next Experiment:** Run metadata/load smoke test with the verified artifact using the CUDA 12.4 runtime and separately CPU-only if device enumeration remains empty. Do not claim CUDA support until `--list-devices` lists the RTX 3050.
