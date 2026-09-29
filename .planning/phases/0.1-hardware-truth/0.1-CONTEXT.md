# Phase 0.1: Hardware truth - Context

**Gathered:** 2026-09-29
**Status:** Ready for planning

<domain>
## Phase Boundary

Build a rerunnable E0 hardware and environment probe for the actual RTX 3050 laptop. It must capture measured GPU, CPU/RAM, PCIe, SSD, software, and thermal/power facts, produce machine-readable and human-readable reports, and record missing measurements without silently substituting assumptions. This phase does not download or benchmark the Qwen model; stock model compatibility and inference begin in later E0 phases.

</domain>

<decisions>
## Implementation Decisions

### Measurement scope
- **D-01:** Implement the full E0 matrix in the first probe: GPU identity/VRAM/SM, driver/CUDA/toolchain, GPU copy and representative FFN-shaped GEMV/GEMM bandwidth, CPU/SIMD and RAM bandwidth, PCIe/host-device transfer, SSD throughput, and power/thermal context.
- **D-02:** Run each independent measurement with warmups and repeated samples, reporting median and spread rather than a single best case. Preserve raw samples for later route-budget calculations.

### Runtime and bandwidth
- **D-03:** Prioritize Windows-native execution using PowerShell, `nvidia-smi`, and native microbenchmarks. Provide WSL2 as a separately labeled fallback when a native CUDA/Linux tool is unavailable; do not merge the environments into one unlabeled result.
- **D-04:** Treat sustained device copy bandwidth and representative FFN-shaped GEMV/GEMM effective bandwidth as separate measurements. Use the GEMV result for decode-ceiling calculations, while retaining copy bandwidth as the transport ceiling.

### Power and repeatability
- **D-05:** Use a fixed AC/power profile with recorded Windows power mode, AC/battery state, clocks, temperature, and power where available. Warm up before timed samples and report run conditions with every result.

### Output and failure behavior
- **D-06:** Make JSON the canonical raw schema and generate `notes/hardware_profile.md` from it. The Markdown report is the human-readable table; JSON supports programmatic comparisons and reruns.
- **D-07:** Measure PCIe using both link inventory and an application-level pinned pageable/H2D/D2H sweep across transfer sizes. The sweep is authoritative for T1 memory-tier planning; inventory identifies negotiated link generation/width.
- **D-08:** Measure SSD with a bounded, non-destructive temporary-file test covering sequential and chunked/read behavior as applicable, then clean up. Do not overwrite model artifacts or rely only on cached existing files.
- **D-09:** If one probe component is unavailable, continue independent probes and emit explicit unavailable/error fields with captured command output. Queue the cheapest fallback experiment and at least one alternative route in the report; do not stop or auto-merge WSL2 data silently.

### Claude's Discretion

- Select concrete native benchmark implementations and dependency versions, provided they are pinned and reproducible.
- Choose sample counts, transfer-size sweep points, bounded SSD test-file size, and exact JSON schema details, provided the choices are recorded before the run and raw samples are retained.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Governing project documents
- `AGENTS.md` — experiment protocol, blocker reporting, folder layout, and communication rules.
- `Deep Research  27B on RTX 3050.md` — architecture facts, thesis assumptions, E0 targets, and bandwidth/PCIe hypotheses.
- `.planning/PROJECT.md` — core value, constraints, and key decisions.
- `.planning/REQUIREMENTS.md` § E0 — testable E0 hardware and bandwidth requirements.
- `.planning/ROADMAP.md` § Phase 0.1 — observable E0 deliverable and success criteria.
- `.planning/STATE.md` — current planning state and required run record.

### Research guidance
- `.planning/research/STACK.md` — Windows-native/WSL2 runtime ladder and reproducibility schema.
- `.planning/research/ARCHITECTURE.md` — artifact/report contracts and E0–E4 component boundaries.
- `.planning/research/PITFALLS.md` — measurement, SKU, PCIe, Windows, and thermal pitfalls.
- `.planning/research/SUMMARY.md` — synthesized findings and roadmap implications.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- No application/runtime code exists yet. The repository currently contains project documents, empty experiment/runtime/script/quality/notes directories, and `experiments/LOG.md`.
- The existing experiment ledger establishes the required append-only logging destination.

### Established Patterns
- Numbered scripts under `scripts/` are the project convention.
- Model artifacts belong under `models/` and generated reports under `notes/`; large artifacts must remain uncommitted.
- Every run must state a hypothesis and numeric target before execution and end with Status / Numbers / Next Experiment.

### Integration Points
- The probe's raw JSON should feed the generated `notes/hardware_profile.md`, future E2 ceiling tables, and `experiments/LOG.md`.
- The probe should expose stable machine-readable fields for later baseline, kernel, PCIe, and memory-tier scripts.

</code_context>

<specifics>
## Specific Ideas

- The user's stated E0 deliverable is a measured table replacing all assumed figures such as 168–224 GB/s GPU bandwidth and 50 GB/s RAM bandwidth.
- The key transport number for T1 is achievable pinned host-device throughput, not only negotiated PCIe link metadata.
- Missing native tools must be represented honestly while independent facts continue to be collected.

</specifics>

<deferred>
## Deferred Ideas

- Stock/reference model loading and quality baseline — Phase 0.2–0.4.
- Ternary agreement, healing, kernels, memory-tier inference, sparsity, and VLM eviction — later E1–E4 phases.
- Cross-environment comparison of Windows-native versus WSL2 overhead — only if needed after the primary native probe.

</deferred>

---

*Phase: 0.1-Hardware truth*
*Context gathered: 2026-09-29*
