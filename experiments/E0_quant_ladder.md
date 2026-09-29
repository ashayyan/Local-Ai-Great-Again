# E0 Stock Quantization Ladder

| Tier | Model artifact | VRAM peak | RAM peak | Prefill tok/s | Decode tok/s | Quality | Status |
|---|---:|---:|---:|---:|---:|---|---|
| Q4/NVFP4 | unavailable locally | — | — | — | — | — | not run |
| Q3/IQ3 | unavailable locally | — | — | — | — | — | not run |
| Q2/IQ2 | unavailable locally | — | — | — | — | — | not run |

## Status / Numbers / Next Experiment

- **Status:** 50 text prompts frozen as an initial fixture; no checkpoint is locally available and no quant tier has been run. Image fixtures, calibration samples, and reference outputs remain pending.
- **Numbers:** 50 text prompts; 0 measured quant levels; quality/VRAM/RAM/prefill/decode unmeasured.
- **Next Experiment:** Pin model and runtime revisions, acquire source metadata, then run the stock Q4/NVFP4 baseline before changing quant tier one variable at a time.
