# Phase 0.1: Hardware truth - Discussion Log

> **Audit trail only.** Decisions are captured in 0.1-CONTEXT.md.

**Date:** 2026-09-29
**Phase:** 0.1-Hardware truth
**Areas discussed:** measurement scope, runtime route, bandwidth method, thermal protocol, report format, PCIe probe, SSD probe, failure capture

---

## Measurement scope

| Option | Selected |
|---|---|
| Full E0 matrix | ✓ |
| Minimal then expand | |
| Include stress sweeps | |

**User's choice:** Full E0 matrix.

## Runtime and bandwidth

| Option | Selected |
|---|---|
| Windows-native first | ✓ |
| WSL2 first | |
| Parallel routes | |

**User's choice:** Windows-native first, with separately labeled WSL2 fallback.

## Bandwidth method

| Option | Selected |
|---|---|
| Sustained GEMV/GEMM plus copy | ✓ |
| CUDA bandwidth copy | |
| Representative model kernels only | |

**User's choice:** Record copy and representative FFN-shaped effective bandwidth; GEMV drives decode ceilings.

## Thermal protocol

| Option | Selected |
|---|---|
| Fixed power profile + warmups | ✓ |
| Unrestricted normal use | |
| Both AC and battery | |

**User's choice:** Fixed AC/power profile with warmups and telemetry.

## Report format

| Option | Selected |
|---|---|
| JSON + Markdown | ✓ |
| Markdown only | |
| JSON + CSV + Markdown | |

**User's choice:** JSON raw schema plus generated Markdown report.

## PCIe probe

| Option | Selected |
|---|---|
| Pinned H2D/D2H sweep | ✓ |
| nvidia-smi link inventory only | |
| Both inventory and sweep | |

**User's choice:** Use both inventory and pinned transfer sweep; pinned throughput is authoritative for T1 planning.

## SSD probe

| Option | Selected |
|---|---|
| Non-destructive temp-file sweep | ✓ |
| Existing-file read | |
| Sequential only | |

**User's choice:** Bounded temporary-file test with cleanup.

## Failure capture

| Option | Selected |
|---|---|
| Continue with explicit unavailable fields | ✓ |
| Stop at first failure | |
| Auto-switch to WSL2 | |

**User's choice:** Continue independent probes, capture unavailable/error fields, and queue fallback experiments.

## Claude's Discretion

- Exact pinned native benchmark implementation, dependency versions, sample counts, transfer sizes, bounded SSD file size, and JSON field details, subject to pre-registration and raw sample retention.

## Deferred Ideas

- Model loading, quality baseline, kernel work, memory-tier inference, sparsity, and multimodal eviction remain in later roadmap phases.
