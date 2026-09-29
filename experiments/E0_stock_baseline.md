# E0 Stock Reference Baseline

## Status / Numbers / Next Experiment

- **Status:** Reference availability test ran; no model weights were found, so no inference or quality claim is made.
- **Numbers:** 0 local model weight files, context target 2048, seed 0; VRAM/RAM peaks and prefill/decode tok/s are not measured. Structured run record: `experiments/raw/stock/run.json`.
- **Next Experiment:** Resolve an immutable Qwen3.8-27B source revision and fetch metadata only; inspect compatible stock runtime support, then download the pinned NVFP4 or supported GGUF artifact for the first measured full-model run. Candidate routes: (1) pinned NVFP4 with compatible runtime and CPU offload, (2) supported GGUF partial offload or CPU-only stock reference. Cheapest command: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/s02_model_manifest.ps1 -ModelPath models -Output models/qwen3.8-27b-manifest.json` after metadata acquisition.
