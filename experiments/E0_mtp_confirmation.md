# E0 MTP confirmation (pre-registered)

## Hypothesis / expectation
Run the same IQ3_S configuration twice with MTP disabled and twice with `--spec-type draft-mtp`: `ngl=16`, context 2048, seed 7, `-n 128`, fixed short prompt, verbose logging. Require explicit draft/accept telemetry. Preliminary operator result was MTP 1.5 decode / 4.7 prefill versus the 1.8 / 10.3 baseline; expectation is no net speedup and possible slowdown.

## Classification rules
- No accept telemetry in either MTP run: unsupported flag on this build; dormant, trigger llama.cpp MTP support for qwen35 hybrid.
- MTP engages and median is slower: dormant, trigger GPU-resident ternary draft (T1 kernel phase).
- MTP net speedup >=1.2x: record improvement but retain stock baseline as the honest bar.

## Run artifacts
- Baseline repeats: `experiments/raw/mtp-base-1.txt`, `mtp-base-2.txt`
- MTP repeats: `experiments/raw/mtp-mtp-1.txt`, `mtp-mtp-2.txt`

## Status / Numbers / Next Experiment
- **Status:** Four verbose runs executing sequentially.
- **Numbers:** Preliminary MTP 1.5 decode / 4.7 prefill; confirmation telemetry pending.
- **Next Experiment:** Parse draft/accept lines, compute median ± spread, classify MTP, and update `experiments/LOG.md`.