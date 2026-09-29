# Plan 01-04 Summary — Quality and quant ladder

**Status:** Partial fixture preparation only; model-dependent work not executed.

- Froze 50 initial text prompts and a manifest with disjoint calibration/evaluation identifiers.
- Added five genuinely disjoint calibration prompts and four hashed deterministic SVG image fixtures for OCR/charts/spatial/multistep; visual model behavior remains unmeasured.
- Implemented `scripts/s04_freeze_quality.ps1`, `scripts/s05_score_quality.ps1`, and `scripts/s06_quant_ladder.ps1`, which report unmeasured PPL and three unavailable quant tiers rather than fabricated quality numbers.

## Status / Numbers / Next Experiment
- **Status:** Fixture and availability harnesses run; semantic scoring/quant comparisons remain open.
- **Numbers:** 50 evaluation prompts, 5 calibration prompts, 4 SVG image fixtures, 0 model outputs, 0 quant tiers benchmarked.
- **Next Experiment:** Pin model/tokenizer/processor assets and compatible stock runtime, then measure the first reference before lower-bit comparisons.
