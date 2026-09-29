# Phase 1 Research — Hardware Truth, Baseline, and Reproduction (Normalized E0)

**Status:** Planning input only; no experiments have run.

## Scope
This phase is the normalized integer Phase 1 equivalent of former E0 slices 0.1–0.5: hardware truth, complete artifact inventory, stock baseline, frozen quality/quant ladder, and clean-checkout reproduction. The hard dependency is baseline-first: no invention kernels, model surgery, or E1 work before these evidence artifacts exist.

## Recommended dependency order
1. `01-01-PLAN.md`: Windows-native hardware probe, rerun, JSON + Markdown profile.
2. `01-02-PLAN.md`: immutable model manifest and compatibility classification.
3. `01-03-PLAN.md`: deterministic stock/reference text and multimodal smoke path.
4. `01-04-PLAN.md`: frozen quality fixtures, scorer, and one-variable quant ladder.
5. `01-05-PLAN.md`: orchestration, clean-checkout regeneration, and E0 gate record.

## Technical decisions carried forward
- Windows-native PowerShell first; WSL2 is a separately labeled fallback.
- Capture exact environment and script/model hashes. JSON is canonical; Markdown is generated.
- Hardware probe needs `nvidia-smi` inventory, CUDA event timings where available, device copy, Qwen FFN shapes `17408x5120` and `5120x17408`, CPU/RAM bandwidth, pinned/pageable H2D/D2H, and bounded SSD cold/warm reads.
- Use warmups and repeated samples; preserve raw samples and report median, spread/p95. Record thermal/power state.
- Payload GEMV/GEMM bandwidth is derived and must not be mislabeled as physical DRAM bandwidth.
- Any unavailable tool or loader becomes a structured error/unavailable result. Continue independent probes and report numeric constraint, two routes, and cheapest next command.
- Model manifest must cover language body, untied embedding/lm_head, 48 GDN/16 full attention, vision tower/processor, tokenizer, and native MTP. Text-only support cannot be called complete multimodal support.
- Baseline uses context >=2048 and fixed seed/prompt. Quality fixtures need >=50 text prompts, disjoint calibration/evaluation partitions, and OCR/chart/spatial/multistep image cases.
- Ladder compares Q4/NVFP4, Q3/IQ3, Q2/IQ2 at matched settings; unsupported formats receive evidence-backed records.
- Large model files and generated binaries remain outside version control.

## Failure/fallback routes
- No native CUDA/compiler: WSL2 CUDA helper, then pinned PyTorch CUDA event harness; CPU-only output is separate and not a GPU replacement.
- Pinned transfer allocation failure: smaller pinned buffers and/or WSL2; retain pageable results and exact CUDA error.
- Loader lacks GDN/MTP/vision/untied head: pinned compatible runtime, WSL2, or architecture fixture; never silently omit.
- Full baseline resource failure: label partial/text-only, retain exact VRAM/RAM gap, and route to stock partial offload or CPU/RAM reference as separate runs.
- SSD pressure: reduce bounded temp file only after recording free-space constraint; use page-cache/mmap or RAM staging as later routes.

## Source guidance
- `.planning/phases/01-hardware-truth-baseline-and-reproduction-e0/01-CONTEXT.md` locks user decisions.
- `.planning/REQUIREMENTS.md` owns REQ-E0-01 through REQ-E0-06 and REQ-LOG-01 through REQ-LOG-03.
- `.planning/research/STACK.md`, `ARCHITECTURE.md`, `PITFALLS.md`, and `SUMMARY.md` provide tooling, schema, and pitfalls.
- `AGENTS.md` requires hypothesis + target before each run, exact commands, peaks/speeds/quality, all failures logged, one variable per comparison, and closing Status / Numbers / Next Experiment.

## Plan verification requirements
Every plan uses explicit `<verify><automated>...</automated><fails_when>...</fails_when></verify>` pairs. Plans refer only to tracked source paths or new intended paths. Experiments are not run during planning.

## Status / Numbers / Next Experiment
- **Status:** Research synthesized for normalized Phase 1; no local measurements.
- **Numbers:** 5 dependent plans; context >=2048; >=50 text prompts; 3 quant tiers; repeated hardware samples; Qwen FFN shapes 17408x5120 and 5120x17408.
- **Next Experiment:** Execute `01-01-PLAN.md` first with a pre-registered Windows-native probe; expected output is measured JSON/Markdown plus explicit unavailable fields or numeric fallback routes.
