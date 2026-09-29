# E0 Decision Gate

| Requirement | Evidence | Decision |
|---|---|---|
| REQ-E0-01 | `notes/hardware_profile.json`, `experiments/LOG.md` | Partial: GPU/CPU/RAM identity recorded; SM count, AVX2 support and controlled duplicate benchmark pending |
| REQ-E0-02 | `notes/hardware_profile.json`, `notes/cpu_stream.json`, `notes/gpu_transfer.json`, `notes/gpu_transfer_run2.json` | Partial: single-thread Triad and synchronous CUDA D2D/H2D/D2H copy measured; GEMV, multicore RAM, thermal-controlled PCIe repeat, cold SSD ceiling unmeasured |
| REQ-E0-03 | `notes/model_compatibility.md`, `notes/model_metadata_followup.md` | Partial: pinned config/index metadata parsed; 18/18 weight shards and full tokenizer remain absent; runtime untested |
| REQ-E0-04 | `experiments/E0_stock_baseline.md` | Open: zero weights, no inference |
| REQ-E0-05 | `experiments/E0_quant_ladder.md` | Open: zero quant tiers measured |
| REQ-E0-06 | `quality/manifest.json` | Partial: 50 eval + 5 calibration prompts, 4 image fixtures; reference outputs/PPL and processor revision pending |
| REQ-LOG-01 | `experiments/LOG.md` | Partial: hardware, manifest, baseline, CPU, and fixture attempts recorded; some early run records lack complete pre-registration or peaks |
| REQ-LOG-02 | `experiments/LOG.md` | Open: no inference measurements |
| REQ-LOG-03 | `scripts/s07_run_e0.ps1`, `scripts/s08_verify_e0_reproduction.ps1`, `notes/E0_headline_table.md` | Partial: six-stage orchestration and structural checks run; no fresh checkout or full-model rerun |

## Blocker routes

- **Constraint:** 4,096 MiB reported GPU VRAM; 0/18 indexed BF16 weight shards locally present (index total size 55,562,855,904 bytes); GPU FFN GEMV bandwidth unmeasured; 16 MiB pinned H2D 1,861/1,842 MiB/s from two retained runs; CPU single-thread Triad median 11,978 MiB/s. No full-model speed/quality sample exists.
- **Route A:** Pin source revision, fetch metadata and NVFP4 shards, use compatible stock runtime with CPU/RAM offload.
- **Route B:** Pin compatible GGUF reference and run stock partial offload or CPU-only fallback; preserve model-feature support classification.
- **Cheapest next experiment:** Fetch tokenizer metadata at pinned SHA `1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0`, rerun `scripts/s02_model_manifest.ps1`; run an FFN-shaped GEMV microbenchmark and repeat pinned transfers at fixed AC/clocks.

## Status / Numbers / Next Experiment
- **Status:** E0 gate remains open. Partial hardware/fixture evidence is committed; no thesis promotion or baseline performance claim.
- **Numbers:** 4,096 MiB reported VRAM, 16 GiB RAM, 6C/12T CPU, single-thread Triad median 11,978 MiB/s, 16 MiB pinned H2D medians 1,861/1,842 MiB/s, 50 text + 5 calibration prompts, 4 image fixtures, 7 model metadata files, 18/18 weight shards missing, 0 quant tiers measured.
- **Next Experiment:** Metadata-only source pin followed by repeated native bandwidth and pinned-transfer probes; then first stock full-model output at context 2048.
