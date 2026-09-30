# Local AI Great Again — Qwen3.8-27B on an RTX 3050 Laptop

## Mission
Run the **complete** Qwen3.8-27B multimodal model on a laptop with 4 GB VRAM and 16 GiB RAM at ≥5 tok/s with 4-bit-equivalent quality. The project is invention-forward: it does not prune to a tiny substitute, use cloud answers, or replace the full model as verifier.

## Measured state (as of 2026-09-30)

| Measurement | Value |
|---|---|
| GPU | RTX 3050 Laptop, compute capability 8.6 |
| VRAM | 4095 MiB |
| Driver | 610.62 |
| CPU Triad | 16.94 GB/s, 6 threads |
| SSD | 945 MB/s |
| PCIe H2D | ≈1.85 GB/s |
| Baseline bar | 1.8 decode / 10.3 prefill tok/s, IQ3_S, `ngl16`, context 2048 |
| Machine law | RAM working set >~10 GiB collapses decode to SSD speed: 0.10 t/s at `ngl=0` → 1.24 t/s at `ngl=16` in bench, 1.8 interactive |

## The architecture we're building

T3+T4 are merged: approximately 2.5-bit GDN/attention/head weights remain on GPU in ~2.6 GB; Sherry 1.25-bit ternary FFN weights remain resident on CPU in a 2.67 GB working set; a hot-row cache occupies spare VRAM; MTP/self-drafting sits on top. The quality gate is ≤+15% PPL versus the frozen reference. The verifier is always the full model.

## Repo map

- `AGENTS.md` — project law and experiment protocol.
- `Deep Research  27B on RTX 3050.md` — research record.
- `.planning/` — GSD state, roadmap, and requirements.
- `experiments/` — append-only experiment ledger and artifacts.
- `quality/` — frozen evaluation suites and fixtures.
- `notes/` — machine records, manifests, and route requests.
- `scripts/` — reproducible probes and harnesses.

## Status board

- **E0:** `EVIDENCED-IN-PROGRESS-CLOSURE`; IQ3_S baseline bar established, offload sweep classified, clean control and MTP confirmation pending.
- **E1/E3.1:** scaffolded.
- **Compute request:** authored for Kaggle T4×2 and TPU Research Cloud.
- **MTP:** preliminary result recorded; explicit draft/accept telemetry confirmation pending.

## Rules

Constraints are data, not verdicts. Failures are first-class evidence. Every artifact ends with **Status / Numbers / Next Experiment**. The banned-language list and mandatory engineering replacement pattern are defined in `AGENTS.md`.

Large model files, runtimes, and generated binaries stay outside Git.
