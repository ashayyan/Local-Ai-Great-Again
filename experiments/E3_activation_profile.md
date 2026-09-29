# E3.1 Activation Sparsity Profiling Harness

## Pre-registration

- **Hypothesis:** Native SiLU/SwiGLU activation magnitudes differ by prompt category; per-layer tails, top-k mass, inactive fractions, and consecutive-token reuse identify sparsity/precision routes.
- **Target:** Profile at least **1000 tokens** across instruction, code, reasoning, and factual categories. Report per-layer magnitude distributions (mean, p50/p90/p99/max), top-k absolute-mass (default k=1% and 10%), inactive fraction (absolute activation <= 1e-3), and consecutive-token row reuse/reuse-distance traces.
- **Command (free or borrowed compute):**
  `python scripts/s16_activation_profile.py --model <LOCAL_MODEL> --tokenizer <LOCAL_TOKENIZER> --output notes/activation_profile.json`
- **Routes:** (1) free local Transformers/PyTorch execution; (2) borrowed compute with the same model/tokenizer arguments and output schema; (3) architecture-specific hook adapter if native SiLU/SwiGLU modules are not exposed.
- **Status:** pre-registered; no weights are downloaded by the harness.

## Harness behavior

`scripts/s16_activation_profile.py` always uses `local_files_only=True` and does not call download APIs. It accepts `--model` and `--tokenizer` for a local/borrowed model, discovers native `torch.nn.SiLU` and modules named SwiGLU, and records structured JSON. The output explicitly reports `status: unavailable` with an exact dependency, model, architecture, or runtime blocker when prerequisites are absent. `--min-tokens` rejects values below 1000.

## Local validation

Syntax validation:

```powershell
python -m py_compile scripts/s16_activation_profile.py
```

Unavailable-mode run (no model argument; expected exit code 2):

```powershell
python scripts/s16_activation_profile.py --output notes/activation_profile.json
```

This records the exact local model absence and any dependency/runtime blocker in `notes/activation_profile.json`; no model weights are fetched. A measured run must preserve the command shape, >=1000-token target, and output schema.

## Status / Numbers / Next Experiment

- **Status:** Harness implemented and local unavailable path validated; activation numbers await a local or borrowed model/tokenizer.
- **Numbers:** Required minimum 1000 tokens; default categories 4; default top-k mass 1% and 10%; inactive threshold 1e-3; no activation samples in unavailable mode.
- **Next Experiment:** Run the pre-registered command on free/borrowed compute with a local checkpoint; confirm `status: measured`, `tokens.observed >= 1000`, nonzero native hooks, and layer/category distributions.
