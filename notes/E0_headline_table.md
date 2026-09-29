# E0 headline table

This table separates measured host/device probes from model-dependent gates. No row below is a full-model throughput or quality claim.

| Area | Evidence | Result | Gate |
|---|---|---:|---|
| GPU identity | `notes/hardware_profile.json` | RTX 3050 Laptop, 4096 MiB, CC 8.6 | partial |
| CPU identity | `notes/hardware_profile.json` | i5-11400H, 6C/12T, 16 GiB RAM | partial |
| CPU memory probe | `notes/cpu_stream.json` | 11,978.009 MiB/s median, single-thread Triad | partial |
| CUDA D2D copy | `notes/gpu_transfer.json`, `notes/gpu_transfer_run2.json` | 16 MiB medians 72,365.5 / 69,084.5 MiB/s | partial; variance/power control open |
| Pinned H2D | same | 16 MiB medians 1,860.5 / 1,841.6 MiB/s | partial; synchronous calls |
| Model metadata | `notes/model_metadata_followup.md` | 7 files, 64/48/16 architecture, 18 shards missing | partial |
| Stock baseline | `experiments/raw/stock/run.json` | blocked-no-weights, 0 model files | open |
| Quality fixtures | `quality/manifest.json` | 50 eval, 5 calibration, 4 images | partial; no outputs |
| Quant ladder | `quality/quant_ladder/ladder.json` | 3 tiers listed, 0 executed | open |
| Reproduction | `experiments/e0_runs/clean-checkout.json` | structural partial, model_reproduced=false | open |

## Status / Numbers / Next Experiment
- **Status:** E0 is structurally instrumented with honest partial/open gates; no full-model baseline exists.
- **Numbers:** 4096 MiB VRAM; 16 GiB RAM; 11,978 MiB/s CPU Triad; 16 MiB pinned H2D 1,860.5/1,841.6 MiB/s; 18/18 model shards missing; 0 model outputs.
- **Next Experiment:** Acquire one pinned quantized artifact and compatible GDN/vision/MTP runtime; run context-2048 stock output with VRAM/RAM peaks, prefill/decode, and quality score. In parallel, measure FFN-shaped GEMV and controlled transfer variance.
