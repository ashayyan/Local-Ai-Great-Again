# E0 IQ3_S Route A acquisition

## Hypothesis / target
A trusted, parallel aria2 transfer from the exact Hugging Face resolve URL can acquire the unchanged IQ3_S artifact resumably within a bounded three-hour window. Target is exactly 12,040,883,104 bytes and SHA-256 `d847e2c1e4aa276e4b7b8e9ad7628050e61e165d49ab995407bc36677a6f3864`.

## Tooling
`aria2c` was initially absent. Installed only the small `aria2.aria2` winget package, version 1.37.0; winget reported successful installer hash verification. Script: `scripts/s18_aria2_iq3s.ps1`.

## Exact transfer
URL: `https://huggingface.co/unsloth/Qwen3.8-27B-GGUF/resolve/main/Qwen3.8-27B-UD-IQ3_S.gguf`
Output: `models/ignored/Qwen3.8-27B-UD-IQ3_S.gguf`
State: `models/ignored/Qwen3.8-27B-UD-IQ3_S.gguf.aria2`
Connections/splits: 16; `--continue=true`; `--file-allocation=none`; maximum window: 10,800 seconds.

## Observations
Two initial launches failed before transfer due PowerShell argument construction; they wrote 0 bytes and no state. The corrected launch is active as job `pwsh-349` (aria2c PID 32068 at the last check). It reached 9,409,921,024 bytes after roughly 20 seconds, then 11,451,498,496 bytes after another 30 seconds. aria2's live output reported ~42–48 MiB/s and ETA approximately 2–4 minutes, with 16 connections. The transfer is intentionally left running and resumable; final bytes/rate/hash are emitted to `notes/iq3s_acquisition_routeA.json` by the script when aria2 exits.

No quant or revision was altered. `experiments/LOG.md` was not edited.

**Status / Numbers / Next Experiment:** Route A active; last observed 11,451,498,496 / 12,040,883,104 bytes (~95.1%), 16 connections, ~42–48 MiB/s live rate. Next: allow job to finish, then require exact size and SHA before any inference/load test.
