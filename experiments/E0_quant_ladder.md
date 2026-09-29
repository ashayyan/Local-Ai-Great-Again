# E0 Stock Quantization Ladder

| Tier | Model artifact | VRAM peak | RAM peak | Prefill tok/s | Decode tok/s | Quality | Status |
|---|---:|---:|---:|---:|---:|---|---|
| Q4/NVFP4 | unavailable locally | — | — | — | — | — | not run |
| Q3/IQ3 | unavailable locally | — | — | — | — | — | not run |
| Q2/IQ2 | unavailable locally | — | — | — | — | — | not run |

## Status / Numbers / Next Experiment

- **Status:** 50 text prompts, 5 disjoint calibration prompts, and four SVG image fixtures are hashed in `quality/manifest.json`. No weight checkpoint is locally available and no quant tier has been run. Reference outputs and full-model scoring remain pending.
- **Numbers:** 50 evaluation prompts; 5 calibration prompts; 4 image fixture categories; 0 measured quant tiers; quality/VRAM/RAM/prefill/decode unmeasured. `quality/quant_ladder/ladder.json` records all 3 tiers as unavailable.
- **Next Experiment:** Acquire pinned stock weights/runtime at source revision `1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0` or a pinned quant source, measure Q4/NVFP4 reference at context 2048, then vary only quant tier in separate runs.
