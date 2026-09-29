# E0 Decision Gate

| Requirement | Evidence | Decision |
|---|---|---|
| REQ-E0-01 | `notes/hardware_profile.json`, `experiments/LOG.md` | Partial: identity measured twice; full rerun protocol pending |
| REQ-E0-02 | `notes/hardware_profile.json` | Open: GPU/CPU/PCIe bandwidth unmeasured; SSD 1 MiB sample only |
| REQ-E0-03 | `notes/model_compatibility.md` | Open: zero local source assets, revision unresolved |
| REQ-E0-04 | `experiments/E0_stock_baseline.md` | Open: zero weights, no inference |
| REQ-E0-05 | `experiments/E0_quant_ladder.md` | Open: zero quant tiers measured |
| REQ-E0-06 | `quality/manifest.json` | Partial: 50 text prompts; image/calibration/reference fixtures pending |
| REQ-LOG-01 | `experiments/LOG.md` | Partial: hardware and manifest/baseline attempts recorded |
| REQ-LOG-02 | `experiments/LOG.md` | Open: no inference measurements |
| REQ-LOG-03 | numbered scripts in `scripts/` | Open: no clean-checkout rerun or full E0 orchestration |

## Blocker routes

- **Constraint:** 4,096 MB measured GPU VRAM; local model weight files: 0; GPU/CPU/PCIe bandwidth values: unmeasured. No full-model speed/quality sample exists.
- **Route A:** Pin source revision, fetch metadata and NVFP4 shards, use compatible stock runtime with CPU/RAM offload.
- **Route B:** Pin compatible GGUF reference and run stock partial offload or CPU-only fallback; preserve model-feature support classification.
- **Cheapest next experiment:** Resolve immutable model SHA, metadata-only download, rerun `scripts/s02_model_manifest.ps1`; separately implement CUDA/STREAM transfer probes.

## Status / Numbers / Next Experiment
- **Status:** E0 gate remains open. Partial hardware/fixture evidence is committed; no thesis promotion or baseline performance claim.
- **Numbers:** 4 GB VRAM, 16 GiB RAM, 6C/12T CPU, 50 text prompts, 0 local model weights, 0 quant tiers measured.
- **Next Experiment:** Metadata-only source pin followed by repeated native bandwidth and pinned-transfer probes; then first stock full-model output at context 2048.
