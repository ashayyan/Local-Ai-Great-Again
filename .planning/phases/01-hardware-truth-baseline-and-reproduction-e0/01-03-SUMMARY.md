# Plan 01-03 Summary — Stock baseline

**Status:** Partial: runner and structured availability failure implemented; no full-model inference measured.

- Implemented `scripts/s03_stock_baseline.ps1`, which records model/runtime availability at context 2048 without inventing throughput or quality.
- Ran one local attempt: `blocked-no-weights`, 0 local weight files; no pinned runtime.
- Wrote `experiments/raw/stock/run.json`, `experiments/E0_stock_baseline.md`, and an experiment ledger update.
- Remaining: pinned model artifacts, compatible full-model runtime, coherent text and multimodal outputs, VRAM/RAM peaks and tok/s.

## Status / Numbers / Next Experiment
- **Status:** Availability failure captured; baseline gate open.
- **Numbers:** 0 weights; context 2048; performance and quality unmeasured.
- **Next Experiment:** Pin source SHA and fetch metadata, then choose a compatible stock runtime before downloading weights.
