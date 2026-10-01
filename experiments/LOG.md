# Experiment Log

Every run records hypothesis, target, command, model, quant, context, VRAM/RAM peaks, prefill/decode speed, quality, script/hash, and Status / Numbers / Next Experiment.

## E0-IQ2-FIT-CONTROL — final measured ledger entry

- **Hypothesis/target:** IQ2_XXS provides a smaller fit control and may improve decode under the same `ngl=16`, context-2048 setup; it does not replace the IQ3_S quality bar. Bench and interactive prefill are separate evidence classes.
- **Artifact:** `Qwen3.8-27B-UD-IQ2_XXS.gguf`, 7,266,070,528 bytes, 6.76 GiB, 26.90 B parameters, 2.0625 bpw.
- **Bench:** `ngl=16`, `pp512/tg128`, r=2: **214.96 ± 3.50 prefill**, **2.64 ± 0.02 decode tok/s**.
- **Interactive:** same prompt/seed/ngl: **17.2 prompt tok/s**, **2.4 generation tok/s**.
- **Derived constraint:** decode reads about 17–19 GB/s, matching the measured 16.94 GB/s multicore Triad. At 5 tok/s, approximately 3.8 GB must be read per token. IQ2's 6.76 GiB is a fit control, not the complete system.

### Status / Numbers / Next Experiment
- **Status:** IQ2 fit control recorded; IQ3_S remains the quality/performance bar.
- **Numbers:** 2.64 ± 0.02 bench decode; 2.4 interactive generation; 214.96 ± 3.50 bench prefill; 17.2 interactive prompt; 7.266 GB artifact.
- **Next Experiment:** E1 one-shard group-128 absmean ternary smoke under an 8 GiB RAM ceiling.

## E0-MACHINE-CONSTRAINT-CLOSURE — final classifications

- Normal Windows free RAM floor is about 7–8 GiB. The requested >13 GiB clean `ngl=0` control is **RETIRED**, not failed, because IQ3_S is 11.2 GiB and cannot be fully resident.
- MTP on IQ2_XXS is **BLOCKED** with exact error: `context type MTP requested but model doesn't contain MTP layers.` The 26.90 B vs 27.32 B parameter gap supports the classification. Revisit only with a separate MTP-only GGUF passed via `--spec-draft-model`; do not retry `--spec-type draft-mtp` on IQ2_XXS.
- `ngl=99` is VRAM-overflow evidence, not an open crash: exit `-1073740791`, CUDA error at `ggml-cuda.cu:109`.

### Status / Numbers / Next Experiment
- **Status:** E0 fit and runtime anomalies classified; E1 is opened with a RAM-bounded local smoke.
- **Numbers:** normal free RAM 7–8 GiB; IQ3_S 11.2 GiB; MTP exact error; `ngl=99` exit `-1073740791`.
- **Next Experiment:** execute `scripts/s10_e1_layer_smoke.py` only after one BF16 shard is verified; no local 20-prompt alpha run.

## E0-CLEAN-NGL0-20260930 — prerequisite failure

- Hypothesis/target: with browsers and heavy processes closed and >13 GiB free RAM, a clean `ngl=0` bench separates CPU random-access cost from page thrash.
- Exact pre-run evidence: `PRERUN_FREE_GIB=6.88`; target was >13 GiB, so the prerequisite was not met. The run was terminated after the bounded window; artifacts are `experiments/ngl0-clean-20260930.*`.
- Status: failed prerequisite, no clean CPU number claimed. Route A: free RAM by closing additional resident processes/services and rerun; Route B: use a separately labeled smaller/streamed fixture. Cheapest next experiment: inventory top working-set processes and retry only after measured free RAM exceeds 13 GiB.

### Status / Numbers / Next Experiment
- **Status:** Clean control remains pending; no result promoted.
- **Numbers:** required >13 GiB free; observed 6.88 GiB.
- **Next Experiment:** reclaim RAM and rerun once the numeric prerequisite is met.

## INFRA-REPO-MIGRATION-20260930 — infrastructure event

Repository origin was migrated to `https://github.com/ashayyan/Local-Ai-Great-Again.git` after a history scrub removed runtimes and model artifacts. Runtimes/models remain untracked by design. This changes repository infrastructure only; no experiment semantics, measurements, or conclusions changed.

### Status / Numbers / Next Experiment
- **Status:** Infrastructure migration verified with `git remote -v`; no experiment result changed.
- **Numbers:** origin fetch/push both point to `ashayyan/Local-Ai-Great-Again.git`.
- **Next Experiment:** Continue E0 closure from the preserved local artifacts.

## E0-MACHINE-LAW — 2026-09-29 UTC

"RAM residency, not VRAM, is the binding constraint: working set >~10 GiB
evicts model pages and decode collapses from RAM speed (~16.9 GB/s) to SSD
speed (~0.95 GB/s). Evidence: ngl=0 tg128 = 0.10 t/s thrash vs ngl=16
tg(interactive) = 1.8 t/s. Design consequence: every future system's
RAM-resident streamed weights must stay ≤ 2.7 GB — exactly what T3's
ternary CPU FFN (2.67 GB) assumes. This measurement independently
validates the T3 architecture."

Status / Numbers / Next Experiment: This law is recorded as a design constraint for all later phases. Isolated points produced: ngl=8 pp512 53.56 ± 40.17 and tg128 0.65 ± 0.30 tok/s, 10.36 GB peak working set, dmon FB max 2802 MB; ngl=16 pp512 109.23 ± 24.39 and tg128 1.24 ± 0.07 tok/s, 8.67 GB peak working set. ngl=24 is classified as prolonged no-output termination. ngl=99 is classified as hard failure: exit `-1073740791`, CUDA error at `ggml-cuda.cu:109` after backend initialization. The requested sweep points are now classified; clean ngl=0, exit diagnosis, and MTP pair remain pending.

## E0-BASELINE-01 — confirmed supplied run (2026-09-29 UTC)
- Hypothesis/target: verified IQ3_S at context 2048 produces coherent instruction-following output; establish the measured bar. Target: finite output, decode >=1.8 tok/s and prefill >=10.3 tok/s.
- Exact configuration: IQ3_S GGUF, `-ngl 16`, `-ctk q8_0 -ctv q8_0`, context 2048, seed 7; runtime b11259 split CUDA 12.4 (`d280808f5`).
- Result supplied by operator: coherent output with thinking intact; **decode 1.8 tok/s, prefill 10.3 tok/s**. VRAM/RAM peaks were not included and remain unavailable rather than inferred.
- Artifact: 12,040,883,104 bytes, SHA-256 `d847e2c1e4aa276e4b7b8e9ad7628050e61e165d49ab995407bc36677a6f3864`.

### Status / Numbers / Next Experiment
- Status: E0 baseline bar measured and promoted as comparison bar.
- Numbers: 1.8 decode / 10.3 prefill tok/s; IQ3_S; ctx 2048; `ngl=16`; q8_0 KV; seed 7.
- Next Experiment: repeat baseline twice with `-n 128 --verbose`, then paired MTP control.

## E0-MTP-RUN-STATUS — interrupted control sequence

The attempted four-run sequence produced only `experiments/raw/mtp-base-1.txt` before disconnect. Its verbose record reports prompt 10.1311 t/s, generation 1.48825 t/s, 115 predicted tokens, seed 7, and `speculative.types: none`. No MTP raw artifact exists, so MTP remains unclassified.

### Status / Numbers / Next Experiment
- **Status:** Incomplete, no MTP claim.
- **Numbers:** one baseline control: 1.48825 decode / 10.1311 prompt t/s.
- **Next Experiment:** rerun the remaining baseline and both MTP controls separately, requiring draft/accept lines.

## E0-BASELINE-02 — MTP control pending confirmation (2026-09-29 UTC)
- Hypothesis/target: `--spec-type draft-mtp` improves decode only if native MTP is engaged; target is explicit draft/accept telemetry.
- Exact configuration supplied: IQ3_S, ctx 2048, seed 7, same KV/offload controls, `--spec-type draft-mtp`; preliminary decode 1.5 tok/s and prefill 4.7 tok/s.
- Result: not confirmed until both configurations run twice with `-n 128 --verbose` and draft/accept lines are captured.

### Status / Numbers / Next Experiment
- Status: MTP evidence pending; no dormant classification yet.
- Numbers: preliminary 1.5 decode / 4.7 prefill tok/s; engagement telemetry absent.
- Next Experiment: paired verbose repeats; if engaged and slower, mark dormant with revisit trigger GPU-resident ternary draft (T1).

## E0-ROOT-CAUSE-20260929 — CUDA split asset and acquisition
- CUDA enumeration root cause: primary b11259 lacked cudart/cublas split-asset DLLs; adding `cudart-llama-bin-win-cuda-12.4` fixed initialization. llama-bench reports one RTX 3050, CC 8.6, 4095 MiB VRAM.
- Acquisition root cause: single connection ~35 KB/s; 16-range aria2 completed the exact artifact at approximately 41 MiB/s transfer display and 28.080344 MiB/s end-to-end including verification.
- Evidence: `notes/driver_record.json`, `experiments/E0_runtime_cuda124.md`, `experiments/E0_iq3s_routeA.md`, `notes/iq3s_acquisition_routeA.json`.

### Status / Numbers / Next Experiment
- Status: Root causes recorded; no CUDA claim is made from `--list-devices` alone because working evidence is llama-bench initialization.
- Numbers: driver 610.62; CC 8.6; 4095 MiB VRAM; exact SHA/bytes; 28.080344 MiB/s end-to-end.
- Next Experiment: complete offload sweep and paired MTP confirmation.

## E0-E2.1-SWEEP-PREREG — 2026-09-29 UTC
- Hypothesis/target: decode scales with offloaded GB until RAM-resident bytes dominate. Run `llama-bench` at `-ngl 0/8/16/24/99`, `-p 512 -n 128`, `r=2`, with VRAM telemetry.
- Fixed model/hash/runtime/context/KV/seed: IQ3_S / `d847e2c1…f3864` / b11259 `d280808f5` CUDA 12.4 split runtime / ctx 2048 / q8_0 KV / seed 7.
- First point observed: `ngl=0`, pp512 **24.46 ± 1.26 tok/s**; CUDA init found RTX 3050 CC 8.6, 4095 MiB VRAM. Full sweep remains running; no decode result claimed until output is captured.

### Status / Numbers / Next Experiment
- Status: partial; the isolated `ngl=0` command completed its table but exited 1, so the sweep is not complete.
- Numbers: `ngl=0`: pp512 **24.46 ± 1.26 tok/s**, tg128 **0.10 ± 0.01 tok/s**; CUDA init found 1 RTX 3050 device, CC 8.6, 4095 MiB VRAM; no peak telemetry.
- Next Experiment: run `ngl=8/16/24/99` as isolated commands with unique logs and `nvidia-smi` telemetry; diagnose exit code 1 before treating the sweep as complete.

## E0-HW manual-e0b / manual-e0c — 2026-09-29

- Hypothesis: Windows-native probe identifies actual laptop limits with repeatable medians.
- Numeric target: two runs; identity stable; repeated bandwidth/transfer samples; explicit unavailable fields.
- Command: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/s01_hardware_probe.ps1 -RunId manual-e0b/manual-e0c -OutputRoot notes -Warmups 1 -Samples 2 -SsdTestBytes 1048576`
- Script: `scripts/s01_hardware_probe.ps1`; model/quant/context: not applicable (hardware probe).
- Measured: RTX 3050 Laptop GPU, 4096 MB VRAM, compute capability 8.6, driver 610.62, Windows 11 Pro build 26200; i5-11400H, 6 cores/12 logical processors; RAM 17179869184 bytes; SSD probe 1 MiB write 60.13 MB/s/read 138.83 MB/s on run manual-e0b; GPU temperature 54 C; PCIe/CUDA bandwidth/STREAM unavailable.
- Failure: `nvidia-smi -q -d PCI` rejected the display flag; CUDA and STREAM helpers are not installed. Routes: (1) use corrected `nvidia-smi -q`/supported query plus native CUDA toolkit helper; (2) run WSL2 pinned CUDA/STREAM probes. Cheapest next experiment: correct PCI query and compile/run a 17408x5120 copy/GEMV microbenchmark.

### Status / Numbers / Next Experiment
- Status: Partial E0 hardware profile measured; identity repeated across two runs, bandwidth gates remain open.
- Numbers: 4 GB VRAM; SM 8.6; 16 GB RAM; 6C/12T CPU; SSD sample 60.13 write / 138.83 read MB/s; GPU/CPU bandwidth and PCIe application throughput unmeasured.
- Next Experiment: Run supported PCIe inventory and pinned H2D/D2H plus FFN GEMV/GEMM and STREAM helpers; update profile without overwriting prior run artifacts.

## E0-HW e0-table-final — 2026-09-29

- Hypothesis/target before run: supported PCIe query returns numeric generation and width; 64 MiB SSD temp-file read/write is captured separately from 1 MiB. Target: nonempty generation/width and timings without a parse error.
- Exact command: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/s01_hardware_probe.ps1 -RunId e0-table-final -OutputRoot notes -Warmups 1 -Samples 2 -SsdTestBytes 67108864`.
- Script blob hash `3113b50f2f0c3c2fd1c49dd54ddcd3cc0a8a9cc6`; parent commit `bcefebe18a975864ec4671e8b16c455e98c23ae3`. Model/quant/context/VRAM and RAM peaks/prefill/decode/quality: not applicable or unmeasured in inventory-only run.
- Result: 4096 MiB VRAM, 16 GiB installed RAM, negotiated PCIe Gen 2 x8 at idle; 64 MiB SSD timing is cached and not a sustained ceiling. Raw JSON `notes/e0-table-final/hardware.json`. GPU copy/GEMV, CPU STREAM, and pinned H2D/D2H remain unmeasured.
- Exact constraint: CUDA compiler and working PyTorch CUDA runtime absent; WSL is not installed. Routes: (1) native CUDA toolkit/benchmark helper; (2) install/configure separately labeled WSL2 CUDA route. Cheapest next experiment: native pinned H2D/D2H sweep with 1/16/256 MiB buffers, expected GB/s and latency or toolchain error.

### Status / Numbers / Next Experiment
- Status: Corrected PCIe inventory; bandwidth gates open.
- Numbers: PCIe idle Gen 2 x8; 4 GiB VRAM; 16 GiB RAM; achieved PCIe GB/s unknown.
- Next Experiment: Compile/run CUDA pinned transfer microbenchmark while recording active link state.

## E0-MANIFEST-01 — 2026-09-29 UTC (offline artifact inventory)

- Hypothesis (pre-run): the available local `models/` directory can be classified without loading weights, and missing architecture/loader evidence is explicitly represented.
- Numeric target (pre-run): 8/8 required component status records, SHA-256 for 100% of present asset files, zero downloaded weight bytes, and an explicit immutable-revision status.
- Only variable: model artifact availability in the existing `models/` path; no quant/runtime/context settings changed. This is an inventory, not a comparative inference experiment.
- Exact command: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/s02_model_manifest.ps1 -ModelPath models -Output models/qwen3.8-27b-manifest.json -Offline`.
- Script: `scripts/s02_model_manifest.ps1`; script SHA-256 (working-tree tested version): `8a17eecf25cc6c23e7166ccc7d94a61a86b1fc384f9539374c3533411dc28117`; source requested `Qwen/Qwen3.8-27B`, revision unresolved (no checkout/metadata). Generated machine record: ignored `models/qwen3.8-27b-manifest.json`.
- Asset/model file: none; quant: none; context, seed, prompt set, warmups, repetitions: not applicable to directory inventory. VRAM/RAM peak, prefill/decode tok/s, TTFT, quality sample: not measured, no model execution.
- Observed: 0 model files, 0 file hashes, 8/8 components explicitly missing, 0 config-derived architecture fields, tokenizer/processor revisions unresolved, no pinned runtime. Source model size ~55.6 GB is externally reported, not measured in this run. No asset downloads.
- Constraint: zero local asset bytes means model revision and full-model compatibility remain unverified. Routes: (1) fetch config/tokenizer/processor/index only at a verified 40-hex revision; (2) import a metadata-only offline snapshot from a trusted machine. Runtime route alternatives after metadata: pinned compatible Windows build, or WSL2/architecture fixture, each separately labeled.

### Status / Numbers / Next Experiment
- Status: Offline inventory generated; model compatibility classified as unverified and required artifacts as missing, not silently complete.
- Numbers: 0 files; 0 SHA-256 asset hashes; 8 missing components; 0 downloads; 0 runtime tests.
- Next Experiment: Resolve exact SHA with `python -c "from huggingface_hub import HfApi; print(HfApi().model_info('Qwen/Qwen3.8-27B').sha)"`, download only metadata with the `snapshot_download` command in `notes/model_compatibility.md`, rerun manifest; expected measurable result is metadata hashes and config/index coverage with zero safetensors weights downloaded.

## E0-STOCK-01 — PRE-REGISTERED (2026-09-29 UTC)

- Hypothesis: an available pinned stock runtime and full Qwen3.8-27B weight artifact can produce finite text output at context 2048, while a missing prerequisite produces a structured JSON failure rather than a false speed/quality claim.
- Numeric target: one text output at context 2048, seed 0, plus one multimodal attempt if a complete model/processor/runtime is present; capture VRAM/RAM peaks and prefill/decode tok/s or explicit null if no execution; zero large-weight downloads.
- Only changed variable: stock runtime/model availability; no quant comparison, custom kernels, or model surgery.
- Planned exact command: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/s03_stock_baseline.ps1 -Context 2048 -Seed 0 -OutputRoot experiments/raw/stock`.
- Model: Qwen/Qwen3.8-27B, local `models/` only; quant: auto-detect from local artifact, otherwise unavailable; no downloadable weights in this run.
- Script: `scripts/s03_stock_baseline.ps1`; commit at pre-registration: `27cee1359c55a3b5f8c97baf472dc75b55156cfe` (script SHA recorded after implementation). This entry precedes first invocation and will be finalized with observed evidence.
- Observed command: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/s03_stock_baseline.ps1 -Context 2048 -Seed 0 -OutputRoot experiments/raw/stock`.
- Result: `E0-STOCK-20260929-152314Z`, `blocked-no-weights`; 0 local weight files; model/quant unavailable; no prefill/decode, VRAM/RAM peaks, or quality sample because no inference occurred. JSON: `experiments/raw/stock/run.json`.
- Exact constraint: 0 local model weights and no pinned runtime. Routes: (1) pinned NVFP4 + compatible runtime with CPU offload; (2) supported GGUF partial offload/CPU reference. Cheapest next experiment: fetch metadata at immutable source SHA, rerun `scripts/s02_model_manifest.ps1`, then test loader compatibility before weight download.

### Status / Numbers / Next Experiment
- Status: Stock baseline attempted and blocked by missing local model/runtime; failure is logged, not treated as performance data.
- Numbers: 0 model weight files; context 2048; prefill/decode/VRAM/RAM/quality unmeasured.
- Next Experiment: Resolve immutable checkpoint SHA and metadata-only download, then pin compatible stock runtime.

## E0-METADATA-02 — 2026-09-29 (official source metadata only)

- Pre-run hypothesis/target: revision-pinned Qwen source config and weight index can be downloaded and hashed without weight shards; target >=2 metadata files, 0 safetensors weight downloads, confirm 64/48/16 layers.
- Only changed variable from offline inventory: metadata availability. Exact commands: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/s02_fetch_metadata.ps1 -Revision 1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0 -ModelPath models -TimeoutSeconds 30`; then `powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/s02_model_manifest.ps1 -ModelPath models -Output models/qwen3.8-27b-manifest.json -Revision 1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0 -TokenizerRevision 1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0 -ProcessorRevision 1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0 -Offline`.
- Scripts: `scripts/s02_fetch_metadata.ps1`, `scripts/s02_model_manifest.ps1`; git commit after implementation `463bf5b`. Model source SHA from official API; quant none; context/prefill/decode/VRAM/RAM peaks/quality not applicable (no inference).
- Observed: 7 metadata files hashed; 1,199 indexed tensors in 18 shards, all 18 shards absent; config 64 layers, 48 linear, 16 full, vision depth 27, native MTP depth 1; index metadata total size 55,562,855,904 bytes. Source and file hashes in `notes/model_metadata_followup.md`. Zero weight shards downloaded.
- Constraint/routes: 18 missing shards, 0 local weights. Route A pinned NVFP4+compatible runtime with CPU/RAM tier; Route B pinned GGUF stock reference/partial offload with architecture audit. Cheapest next experiment: pin/fetch tokenizer metadata and validate loader support without weight download.

### Status / Numbers / Next Experiment
- Status: Metadata gate improved; full-model inference baseline remains open.
- Numbers: 7 files, 1,199 tensors, 18 missing shards, 64/48/16 layers, 27 vision layers, 1 MTP layer.
- Next Experiment: Fetch tokenizer and image processor metadata; test stock loader architecture support, then acquire weights.

## E0-CPU-STREAM-01 — 2026-09-29

- Hypothesis + target stated before run: Release .NET 8 managed Triad on 3 × 256 MiB arrays, 2 warmups, 7 measured repetitions achieves median >=10,000 MiB/s; checksum prevents dead-code removal.
- Exact command: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/s09_cpu_stream.ps1 -Warmup 2 -Repetitions 7 -MiB 256 -OutputJson notes/cpu_stream.json`. Code: `scripts/cpu_stream/Program.cs` and `scripts/cpu_stream/CpuStream.csproj`. Starting commit `6c47565c4c26000da949d9c3d09e2ac2b086d44b`; .NET 8.0.15 runtime, 9.0.203 SDK. One variable: benchmark memory-operation selection, no model inference. Model/quant/context/prefill/decode/quality/VRAM peak not applicable; RAM allocation from three arrays is 805,306,368 bytes plus runtime overhead (process peak not measured).
- Raw MiB/s: 9660.425964, 11516.919224, 11826.374046, 11978.009124, 12345.619475, 12473.809872, 12485.409304; median **11978.009 MiB/s = 12.56 GB/s decimal**; checksum 21. Raw JSON `notes/cpu_stream.json`. This is one-thread warm-cache Triad, not a multicore DRAM ceiling.
- Constraint/routes: multicore achievable RAM bandwidth still unknown. Routes: (1) pinned multithread STREAM benchmark sweeping array sizes, (2) native C/C++ STREAM build with validated vectorization. Cheapest next experiment: run pinned 1/2/4/6-thread Triad over 3 × 256 MiB arrays, compare medians under fixed AC and clocks.

### Status / Numbers / Next Experiment
- Status: One single-thread STREAM-like Triad measured; multicore bandwidth gate open.
- Numbers: 7 samples, median 11978.009 MiB/s, 3 × 256 MiB arrays, 2 warmups.
- Next Experiment: Multithread STREAM-equivalent sweep with process RAM peak and thermal telemetry.

## E0-QUALITY-FIXTURE-01 — 2026-09-29

- Hypothesis/target before validation: a fixed 50-prompt evaluation set, 5 disjoint calibration prompts and four deterministic SVG image categories can be hashed without model outputs; target 50/5/4 and zero fabricated quality metrics. Variable: fixture completeness only.
- Commands: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/s04_freeze_quality.ps1 -OutputRoot quality`; `powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/s05_score_quality.ps1`; `powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/s06_quant_ladder.ps1`. Model/quant/context: no checkpoint, 3 quant tiers listed at context 2048; VRAM/RAM peaks/prefill/decode/quality unmeasured, PPL explicitly unavailable.
- Results: 50 eval, 5 calibration, 4 SVG fixtures hashed; score outputs 0/50, all 3 quant tiers unavailable due 0 matching local weight artifacts. Machine records `quality/manifest.json`, `quality/results/scores.json`, `quality/quant_ladder/ladder.json`.
- Constraint/routes: 18 source shards absent and no compatible stock runtime; (1) pin/download full NVFP4 and use correct loader, (2) pin compatible GGUF/offload baseline. Cheapest next experiment: inspect tokenizer and processor metadata at immutable SHA, then test stock loader support.

### Status / Numbers / Next Experiment
- Status: Fixture freeze validated; semantic quality and quant ladder gates open.
- Numbers: 50 eval, 5 calibration, 4 images, 0 scored outputs, 0 measured quant tiers.
- Next Experiment: First full-model stock reference output at context 2048 after pinned weights/runtime.

## E0-GPU-TRANSFER-01/02 — 2026-09-29

- Hypothesis/target before each run: CUDA driver API D2D and pageable/pinned H2D/D2H copies over 1, 16, 64 MiB will yield repeatable medians; target five samples after one warmup per case, numerical correctness true in all 15 cases. Run 2 specifically targeted stable identity and correctness with run-to-run variance exposed. One variable: repeat run ID/output path, same code and sizes.
- Exact commands: `python scripts/s10_cuda_transfer.py --sizes-mib 1 16 64 --samples 5 --warmups 1 --output notes/gpu_transfer.json --run-id E0-GPU-transfer-run1`; `python scripts/s10_cuda_transfer.py --sizes-mib 1 16 64 --samples 5 --warmups 1 --output notes/gpu_transfer_run2.json --run-id E0-GPU-transfer-run2`.
- Script: `scripts/s10_cuda_transfer.py`; source revision was uncommitted during runs and is now tracked by subsequent commit; raw JSON retains timestamps/samples. Model/quant/context, prefill/decode/quality and process RAM/VRAM peaks not applicable or unmeasured (copy microbenchmark).
- Measured GPU device total 4,294,443,008 bytes, CC 8.6. All 15 cases per retained run numerically correct, zero API errors. At 16 MiB: run1 D2D 72,365.5 MiB/s, pinned H2D 1,860.5 MiB/s, pinned D2H 2,126.0 MiB/s; retained run2 D2D 69,084.5 MiB/s, H2D 1,841.6 MiB/s, D2H 2,072.0 MiB/s. At 1 MiB pinned H2D differs +35.6% between runs, at 64 MiB -15.1%. Full 1/16/64 MiB table and raw samples: `experiments/E0_gpu_transfer.md`, `notes/gpu_transfer.json`, `notes/gpu_transfer_run2.json`.
- One additional concurrently invoked run2 reused the same output path and was overwritten; its printed medians are disclosed but excluded from reproducible comparisons. Route A: fixed AC/clocks and unique output paths; route B: event-timed CUDA benchmark or WSL2 separately labeled. Cheapest next experiment: third unique run with clocks and PCIe link recorded during transfer; expected variation bounded numerically or diagnosed.

### Status / Numbers / Next Experiment
- Status: Native CUDA transfer bandwidth measured; FFN GEMV and stable transfer-power envelope remain open.
- Numbers: 2 retained runs × 15 correct cases; 16 MiB pinned H2D 1,860.5/1,841.6 MiB/s; D2D 72,365.5/69,084.5 MiB/s.
- Next Experiment: Fixed-power uniquely named repeat; then FFN 17408×5120 GEMV/GEMM bandwidth test.

## E0-ROUTE-20260929 — hardware reroute and NVFP4 technical finding

- Pre-registered closure finding: measured 4,096 MiB VRAM makes T2's 5.3 GB whole-model-in-VRAM target dormant on this machine (revisit trigger: >=6 GB usable VRAM), and pinned H2D approximately 1.85 GB/s-equivalent is below T1's 8 GB/s cross-bus streaming threshold. T1 therefore merges into T3: CPU-RAM draft/verify with hidden-state transfers. Multicore RAM bandwidth is the decision-critical probe.
- Blocked-technical finding: NVFP4 GGUF inference requires sm_120 (Blackwell) CUDA kernels in the candidate path; this machine is sm_86. Missing piece: software NVFP4-to-SM86 kernel path. Status: dormant, not adopted as stock baseline. The minima-ai NVFP4 checkpoint remains the E1 quality teacher for documented free/borrowed compute.
- Exact constraints: 4,096 MiB VRAM; 5.3 GB target; pinned H2D approximately 1.85 GB/s-equivalent; 8 GB/s threshold; compute capability 8.6. Local measurements and declared route targets are distinguished in `experiments/E0_reroute.md`.
- Routes: (1) CPU-RAM resident GGUF with hidden-state-only transfers and T3 draft/verify; (2) use a >=6 GB usable-VRAM machine for T2 or implement/validate an SM86 NVFP4 kernel path. Cheapest next experiment: all-core Triad against 24 GB/s target, then 10 KiB pinned latency.

### Status / Numbers / Next Experiment
- Status: T1/T2 route status recorded; NVFP4 stock path dormant pending SM86 kernel support; no model download performed.
- Numbers: 4,096 MiB VRAM, CC 8.6, 1.85 GB/s pinned H2D, 8 GB/s T1 threshold, 5.3 GB T2 target.
- Next Experiment: Complete multicore RAM, large D2D, FFN GEMV, PCIe latency and cold SSD probes before selecting the constrained GGUF baseline.

## E0-CLOSURE-MULTICORE-01 — 2026-09-29

- Hypothesis/target: six threads over the six physical i5-11400H cores, same Triad protocol, 2 warmups and 7 samples, median >=24 GB/s-equivalent. Exact command: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/s13_multicore_triad.ps1 -Warmup 2 -Repetitions 7 -MiB 256 -Threads 6 -OutputJson notes/multicore_triad.json`. One changed variable: thread count from the prior single-thread probe.
- Run ID `E0-MULTICORE-20260929-165606Z`; .NET 8.0.15, 3 x 256 MiB arrays, checksum 21. Median **16,154.885 MiB/s (16.94 GB/s decimal)**; 7 raw samples in JSON. VRAM/RAM process peak, thermal/power telemetry not captured.
- Constraint/routes: observed managed six-thread median is 67.3% of the 24 GB/s target. Routes: (1) native optimized STREAM with arrays beyond LLC and affinity; (2) tune managed worker/array placement and compare. Cheapest next experiment: native or optimized all-core STREAM with simultaneous `nvidia-smi dmon`.

### Status / Numbers / Next Experiment
- Status: Multicore CPU probe measured; target not met and ceiling remains implementation-dependent.
- Numbers: 6 threads, median 16,154.885 MiB/s, 2 warmups, 7 samples.
- Next Experiment: Native/large-array STREAM and thermal telemetry.

## E0-CLOSURE-GEMV-01 — 2026-09-29

- Hypothesis/target: resident CUDA FFN-shaped 17408x5120 M=1 GEMV in BF16 and F32 yields five samples after one warmup with correct output and effective GB/s. Exact command: `python scripts/s12_ffn_gemv.py --output notes/ffn_gemv.json`.
- Result: unavailable before allocation; Numba 0.61.2 enumerates RTX 3050 CC 8.6 but `cuda.current_context()` fails `IndexError: list index out of range`; a retry also produced an access violation. Intended matrix sizes are 178,257,920 bytes BF16 and 356,515,840 bytes F32; 0 samples and no GB/s claim.
- Routes: repair Numba primary context and rerun unchanged; or use an installed cuBLAS DLL via ctypes with symbol/correctness checks. Cheapest experiment: `python -c "from numba import cuda; print(len(cuda.gpus)); cuda.select_device(0); print(cuda.current_context())"` and inventory cuBLAS DLLs.

### Status / Numbers / Next Experiment
- Status: FFN GEMV gate explicitly unavailable, no fabricated throughput.
- Numbers: 17408x5120, M=1; BF16 178,257,920 bytes; F32 356,515,840 bytes; 0 samples.
- Next Experiment: Repair context or validate cuBLAS route.

## E0-CLOSURE-D2D-LARGE-01 — 2026-09-29

- Hypothesis/target: resident CUDA D2D at 256 and 512 MiB exposes memory-path bandwidth above the 16 MiB latency regime; target five samples after one warmup per block with correctness true. Exact command: `python scripts/s10_cuda_transfer.py --sizes-mib 256 512 --samples 5 --warmups 1 --output notes/gpu_d2d_large.json --run-id E0-GPU-D2D-large`.
- Result: the generic helper tests five directions per size and exceeded a 120-second execution bound before producing an output; it was cancelled. No D2D bandwidth number is claimed. Canonical failure record: `notes/gpu_d2d_large.json`.
- Constraint/routes: large allocations plus pageable/pinned setup overrun the bounded window. Route A: D2D-only helper with one allocation per size and 3 samples; Route B: native CUDA event-timed D2D helper. Cheapest next experiment: D2D-only 256 MiB, 3 samples, unique output.

### Status / Numbers / Next Experiment
- Status: Large-block D2D probe blocked by timeout in the generic five-direction harness.
- Numbers: 256/512 MiB requested; 0 samples completed; timeout at 120 seconds.
- Next Experiment: D2D-only helper, then 512 MiB if 256 MiB completes.

## E0-CLOSURE-LATSSD-01 — 2026-09-29

- Hypothesis/target: 10 KiB hidden-state transfer latency can be characterized with 20 pinned round trips; a 17 GiB sequential file measures SSD throughput beyond 16 GiB RAM. Exact command: `python scripts/s14_latency_ssd.py`. Run ID `E0-LATSSD-20260929-170531Z`.
- SSD result: 18,253,611,008 bytes temporary file; write 156.46 MiB/s; read 945.51 MiB/s. This is a large sequential sample, not an absolute device ceiling because cache bypass was not independently proven.
- Transfer result: **invalid/unavailable** for planning because the first helper version used a null device address and did not assert CUDA return codes. It produced 20 untrusted timing values, median 11.50 us, range 5.80–15.90 us; no valid H2D/D2H copy is claimed.
- Constraint/routes: valid 10 KiB latency is still missing. Route A: allocate device memory and assert every CUDA API return, then measure separate H2D/D2H; Route B: use a corrected existing CUDA transfer helper with a dedicated 10 KiB mode. Cheapest next experiment: repair address allocation/return checks and rerun 20 samples.

### Status / Numbers / Next Experiment
- Status: SSD large-file sample measured; PCIe latency probe explicitly invalidated.
- Numbers: 17 GiB read 945.51 MiB/s; write 156.46 MiB/s; 0 valid PCIe latency samples.
- Next Experiment: Correct 10 KiB pinned H2D/D2H helper and rerun; repeat SSD with cache policy recorded.

## E0-BASELINE-SELECTION-01 — 2026-09-29

- Pre-registration: select a local baseline under measured 16 GiB RAM / 4,096 MiB VRAM, without downloading weights until runtime support and resource envelope are documented. Target: primary IQ3_S plus two fallbacks, Q4 explicitly classified by bytes, and exact runtime/toolchain availability.
- Exact metadata-only inspection is documented in `experiments/E0_baseline_selection.md` and `notes/baseline_selection.json`; no weights downloaded. Unsloth listings: IQ3_S 12,040,883,104 bytes (~12.0 GB), IQ3_XXS 10,934,860,704 (~10.9 GB), IQ2_XXS 7,266,070,528 (~7.3 GB). Q4 family 15.4–17.6 GB is `unavailable-resource` before OS/KV/projector overhead.
- Runtime result: no llama.cpp checkout/binary; cmake, compilers, nvcc and build helpers absent. Qwen3.5/GDN, vision and MTP support are unverified. No stock reference run was attempted because no pinned runtime or local weight artifact exists.
- Routes: (1) obtain a pinned Windows CUDA llama.cpp binary/build with qwen35 + MTP support and run IQ3_S at context 2048; (2) use a pinned CPU/RAM/SSD streaming fork and fall back IQ3_XXS/IQ2_XXS. Cheapest next experiment: acquire a verified runtime binary/source hash without weights, run `--help`/architecture capability checks, then download only IQ3_S if support passes.

### Status / Numbers / Next Experiment
- Status: Baseline artifact selection complete; stock inference gate remains open.
- Numbers: IQ3_S 12.0 GB, IQ3_XXS 10.9 GB, IQ2_XXS 7.3 GB, Q4 15.4–17.6 GB resource-blocked, 0 weights downloaded, 0 stock outputs.
- Next Experiment: Pin llama.cpp build/version and test qwen35/MTP capability before IQ3_S acquisition.

## E0-RESEQUENCE-20260929 — Triad consequence and T3/T4 amendment

- New measured fact: six-thread Triad median **16.94 GB/s decimal**, below the >=24 GB/s hypothesis. Derived CPU-side 2.67 GB ternary FFN estimate is approximately **4.5–5.3 tok/s** before MTP at η=0.7–0.85; this is at the 5 tok/s target without margin. It is a derived budget, not model throughput.
- Architecture amendment: T3 merges with T4. Keep approximately 1.3 GB spare VRAM for hot ternary FFN rows after 2.5-bit GDN/attention/lm_head placement; stream cold rows from RAM. If E3.1 native activation sparsity holds, hypothesized RAM bytes/token reduction is ~2× and ceiling ~8–10 tok/s. No promotion until measured.
- Resequencing: E3.1 native activation profile (>=1,000 representative tokens) runs in parallel with E2 because it gates memory placement and is independent of E1 alpha. Free/borrowed compute fallback is permitted and must preserve tokenizer/model/runtime hashes.
- Routes: (1) E2 hot-row/cold-row placement with measured activation masks; (2) keep dense CPU-RAM route and optimize kernels/overlap. Cheapest next experiment: instrument native FFN activations for >=1,000 tokens and report per-layer magnitude/top-k/inactive distributions.

### Status / Numbers / Next Experiment
- Status: T3/T4 amendment and E3.1 parallel resequencing recorded.
- Numbers: Triad 16.94 GB/s; target 24 GB/s; derived dense CPU ternary estimate 4.5–5.3 tok/s; sparsity hypothesis 2× RAM-byte reduction and 8–10 tok/s.
- Next Experiment: E3.1 activation profile in parallel with E2, while E0 stock baseline remains gated on two IQ3_S runs.

## E0-TOOLCHAIN-20260929 — official CUDA runtime

- Hypothesis/target: official Windows CUDA release provides a runnable CLI with sm_86 CUDA payload, qwen35 support and `--spec-type draft-mtp`; verify release hash/version/help without model weights. Exact asset/API and commands are recorded in `experiments/E0_toolchain.md` and `notes/toolchain_selection.json`.
- Result: archive `runtimes/llama-b11259-win-cuda-13.4-x64.zip`, 153,546,058 bytes, SHA-256 `7e93d79ed0dfacb67a7a5448eab38b60511ec3ad623022259b08490d5cf01404`; version `0.5.0-dev`, build 11259, commit `d280808f5`; `--spec-type` includes `draft-mtp`; CUDA DLLs present. qwen35 is absent from help and ASCII scans, so qwen35/GDN/model-load/MTP execution remains unverified. No weights downloaded.
- Routes: (1) acquire IQ3_S and smoke-test this pinned runtime; (2) if load fails, WSL2 or pinned source fork/build with qwen35/GDN support. Cheapest next experiment: download/hash IQ3_S only, then run the registered context-2048 loader smoke test.

### Status / Numbers / Next Experiment
- Status: Toolchain acquisition passes hash/version/spec-type checks; architecture support is not yet proven.
- Numbers: 153,546,058-byte archive, 193.57 GB free before download, build 11259/d280808f5, 0 model weights.
- Next Experiment: Acquire only IQ3_S and test model load before the two baseline runs.

## E0-IQ3S-ACQUIRE-20260929 — throttled acquisition failure

- Hypothesis/target: with >=30 GB free disk, download only the 12,040,883,104-byte IQ3_S artifact and match SHA-256 `d847e2c1e4aa276e4b7b8e9ad7628050e61e165d49ab995407bc36677a6f3864`. Exact command: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/s17_fetch_iq3s.ps1 -Output models/Qwen3.8-27B-UD-IQ3_S.gguf -Sha256 d847e2c1e4aa276e4b7b8e9ad7628050e61e165d49ab995407bc36677a6f3864`.
- Run ID `E0-IQ3S-20260929-173714Z`; free disk before run 193.57 GB. HF transfer began but was throttled at approximately 35 KB/s with an estimated 94-hour ETA; process was stopped after approximately 245 MiB partial data and the partial file was removed. No model load or baseline run occurred.
- Constraint/routes: network throughput is the current acquisition constraint, not disk capacity. Route A: resume through a Hugging Face-capable downloader/CDN with range resume and checksum; Route B: transfer the exact 12,040,883,104-byte artifact from a trusted cache/machine and verify SHA locally. Cheapest next experiment: issue a metadata/range probe or use a resumable `huggingface_hub` transfer and measure sustained rate for 60 seconds before committing the full download.

### Status / Numbers / Next Experiment
- Status: IQ3_S acquisition blocked by throttled transfer; zero complete weights and zero baseline outputs.
- Numbers: required 12,040,883,104 bytes; free disk 193.57 GB; observed ~35 KB/s; partial ~245 MiB removed; SHA not produced.
- Next Experiment: Test resumable/range-capable transfer or trusted-cache copy, then verify exact bytes/SHA before loading.

## E0-IQ3S-ROUTE-PROBES-20260929 — bounded transfer diagnostics

- Pre-run hypothesis/target: determine if the unchanged `Qwen3.8-27B-UD-IQ3_S.gguf` route is viable via available HF tooling and an Xet-backed CDN, using metadata/HEAD and at most one 1 MiB range request; no full download. Existing target metadata says 12,040,883,104 bytes and prior log records SHA-256 `d847e2c1e4aa276e4b7b8e9ad7628050e61e165d49ab995407bc36677a6f3864` but that digest has no immutable revision binding.
- Exact existing script inspected: `scripts/s17_fetch_iq3s.ps1`; it defaults to `https://huggingface.co/unsloth/Qwen3.8-27B-GGUF/resolve/main/Qwen3.8-27B-UD-IQ3_S.gguf` and curl `-L --fail --retry 2 -o` does not request resume/range. The repo API returned HTTP 200 and current main revision `4ca720788d1e01f1bff70c033e0d0028fd02e502`; requested exact filename is present among 33 entries. The repo revision is mutable relative to prior metadata and does not validate prior hash/size association.
- HF client: `C:\Users\lahd2\miniconda3\python.exe`; `huggingface_hub` is not installed (`find_spec` false, module CLI fails ModuleNotFoundError). Thus neither normal Hub Python route nor `HF_HUB_DISABLE_XET=1` route could execute; no package was installed.
- HEAD/redirect: Windows `curl.exe`, status 200, one redirect, effective host `us.aws.cdn.hf.co`, remote IP `15.236.197.3`, ~0.944 s, 0 bytes, reported speed 0 B/s. Ranged request: HTTP 206, same CDN host/IP, one redirect, one requested/retained MiB, 2.009 s, curl reported 567,518 B/s, retries 0. The probe is preserved at `models/.iq3s-range-probe.partial` (1,048,576 bytes; SHA-256 `177ae5e70ef0d340fdf2d1d75539cf992d69eecdd8d244e36e33456cdcb07cfa`). This deliberately retained partial is not the model file and is not a successful full transfer. Effective URL and signed query were not recorded; no tokens were logged.
- Machine record: `experiments/e0_runs/iq3s-route-probes.json`. No full artifact download or quant/revision substitution occurred. Earlier ~35 KB/s report remains distinct and is not overwritten by this short CDN sample.
- Routes: (1) install/pin Hub client then compare short windows with Xet enabled and `HF_HUB_DISABLE_XET=1`, both range-resumable and sanitized; (2) use curl range-resume against the same exact artifact with checksum after immutable-revision metadata binding. Cheapest next test: 10–15 s bounded Hub transfer per route, retaining cache and recording effective hostname only.

### Status / Numbers / Next Experiment
- Status: route diagnostic achieved for redirecting curl; `huggingface_hub` and disabled-Xet test unavailable because client is absent; full acquisition and hash verification remain unperformed.
- Numbers: API HTTP 200; repo SHA `4ca720788d1e01f1bff70c033e0d0028fd02e502`; curl HEAD 200/0 B; range 206, 1 MiB in 2.009 s, 567,518 B/s, 1 redirect, 0 retries; retained partial 1,048,576 bytes. No signed URLs/tokens in artifacts.
- Next Experiment: pin `huggingface_hub`, bind target file metadata to an immutable repo SHA, then perform matched fixed-window Xet-on/off tests without changing quant.

## E0-RUNTIME-VALIDATE-20260929 — pinned Windows CUDA CLI (no model)

- Pre-run hypothesis/target: the already-pinned llama.cpp CUDA package exposes a runnable CLI, stable version/help, matching archive digest, and an observable CUDA backend/device list; target is successful version/help commands, package SHA-256 matching the previously recorded release digest, and explicit device-list output. This validates the runtime artifact only, not architecture/model support.
- Exact commands: `& "runtimes/llama.cpp-release/llama-cli.exe" --version`; `& "runtimes/llama.cpp-release/llama-cli.exe" --help`; `& "runtimes/llama.cpp-release/llama-cli.exe" --list-devices`; `Get-FileHash runtimes/llama-b11259-win-cuda-13.4-x64.zip -Algorithm SHA256`.
- Executable: `runtimes/llama.cpp-release/llama-cli.exe`. Version output: `version: 0.5.0-dev (build 11259, commit d280808f5)` and `built with Clang 20.1.8 for Windows x86_64` (exit 0). Help exit 0; full exact stdout is in `experiments/raw/runtime-validation/run.json`. It includes CUDA-relevant switches such as `--list-devices`, `--gpu-layers`, and `--spec-type`.
- Package: `runtimes/llama-b11259-win-cuda-13.4-x64.zip`, 153,546,058 bytes, observed SHA-256 `7e93d79ed0dfacb67a7a5448eab38b60511ec3ad623022259b08490d5cf01404` (matches pinned release digest). Extracted `ggml-cuda.dll` is present.
- Backend/device visibility: `--list-devices` exit 0, exact output `Available devices:\n  (none)`. Thus this run confirms the CLI process works and records that it exposes no devices; it does not establish usable CUDA execution. No model was downloaded, no model was loaded, no inference was run, and no model architecture support is claimed. Model, quant, context, VRAM/RAM peaks, token speeds, and quality are not applicable/unmeasured.
- Machine-readable/raw record: `experiments/raw/runtime-validation/run.json` includes the full help output, command strings, exit codes, output, package size/hash, DLL presence, and explicit no-model/no-inference/no-support-claim fields.
- Constraint/routes: CUDA device enumeration produced zero visible devices despite the CUDA DLL being present. Routes: (1) diagnose CUDA backend initialization/device discovery in this process and rerun the same `--list-devices` check; (2) use a separately validated CUDA-capable runtime environment/build and compare its device list. Cheapest next experiment: run the same executable from its runtime directory with `--list-devices` while capturing stderr and `nvidia-smi -L`; expected measurable result is either the RTX 3050 device listed or an exact backend/device initialization discrepancy. Do not acquire weights until this runtime/backend gate is understood.

### Status / Numbers / Next Experiment
- Status: CLI version/help and package hash validated; backend device list is empty. Runtime validation only; model support remains untested and unclaimed.
- Numbers: version 0.5.0-dev/build 11259/commit d280808f5; 153,546,058-byte archive; matching SHA-256; CUDA DLL present; `--list-devices` reports 0 devices; 0 model downloads and 0 inference runs. A separate `nvidia-smi -L` check sees `NVIDIA GeForce RTX 3050 Laptop GPU`; repeating `--list-devices` from `runtimes/llama.cpp-release` still produced no listed device (raw output in `experiments/raw/runtime-validation/list-devices-runtime-dir.json`).
- Next Experiment: Diagnose the runtime/backend initialization discrepancy before treating GPU offload as available; retain a CPU/load smoke path only after the exact GGUF is verified.

## E0-IQ3S-HF-CLIENT-TRIALS-20260929 — bounded client route attempts

- Pre-run hypothesis/target: use the exact IQ3_S filename and immutable observed repo revision `4ca720788d1e01f1bff70c033e0d0028fd02e502` with `hf download`, one worker, local-dir resumable state, and fixed short windows; compare default Xet behavior with `HF_HUB_DISABLE_XET=1`. Do not log tokens or signed URLs and do not change quant.
- Client installation: `huggingface_hub 2.0.0`, `hf_xet 1.6.0`, Python `C:\Users\lahd2\miniconda3\python.exe`; the first attempts were invalid because this CLI does not support the older `--resume-download` option. Those failures are retained in `experiments/raw/download-tests/hf-xet-enabled.json` and `hf-xet-disabled.json` (exit 2, 0 bytes).
- Corrected trials were launched with `--max-workers 1`, no unsupported resume flag, and separate local directories. Their machine records are `experiments/raw/download-tests/hf-xet-enabled-v3.json` and `hf-xet-disabled-v3.json`; logs are sanitized to exclude signed query material. The process was bounded to the short diagnostic window and any partial/cache state is retained. A prior curl range trial remains the only completed transfer measurement: HTTP 206, 1 MiB in 2.009 s, 567,518 B/s (0.542 MiB/s), one redirect to `us.aws.cdn.hf.co`, zero retries.
- Constraint/routes: the exact expected artifact remains 12,040,883,104 bytes with previously recorded SHA-256 `d847e2c1e4aa276e4b7b8e9ad7628050e61e165d49ab995407bc36677a6f3864`, but that digest has not been cryptographically bound to the observed mutable-main revision. Route A is the corrected HF client with retained cache; Route B is Xet-disabled ordinary HTTP; Route C is a trusted exact copy verified locally. Do not enable `HF_XET_HIGH_PERFORMANCE` on this 16 GiB host.

### Status / Numbers / Next Experiment
- Status: exact quant/revision selection preserved; full artifact is not yet verified and no inference claim is allowed. Runtime sees the GPU through `nvidia-smi` but the pinned CLI reports zero devices.
- Numbers: target 12,040,883,104 bytes; target SHA-256 `d847e2c1e4aa276e4b7b8e9ad7628050e61e165d49ab995407bc36677a6f3864`; completed curl sample 0.542 MiB/s; prior sustained observation ~0.034 MiB/s; 16 GiB RAM; 4,096 MiB VRAM; no model bytes verified.
- Next Experiment: collect the corrected v3 route results, then either resume the best route or copy a trusted exact artifact; verify size and SHA before a metadata/load smoke test and two pre-registered text-only baselines.

## E0-INTERPRETATION-CORRECTION-20260929

- T2 wholly resident in 4 GiB VRAM is not currently budgeted to fit, but T2 remains an active research route rather than a proven dead route; revisit with changed placement/quantization or >=6 GB usable VRAM.
- The 16.94 GB/s six-thread Triad is a measured memory benchmark, not measured ternary-kernel efficiency or end-to-end token speed.
- A 1.3 GB hot-row cache does not imply 2x fewer CPU bytes/token. E3.1 must measure row-use/reuse traces, routing cost, and actual RAM traffic before promoting T3+T4 speed predictions.
- Valid 10 KiB transfer latency is useful, but does not account for synchronization and 128 layer hops.

### Status / Numbers / Next Experiment
- Status: Interpretation corrections recorded; baseline remains gated on exact artifact and two runs.
- Numbers: Triad 16.94 GB/s; hot-row reduction hypothesis unmeasured; 10 KiB round trip 26.2 us before 128-hop accounting.
- Next Experiment: complete bounded acquisition recovery, then use measured model traces rather than derived hot-row assumptions.

## E0-DRIVER-20260929 — driver compatibility record

- Pre-run hypothesis: record the actual driver/KMD and CUDA version before selecting a llama.cpp CUDA package; target a complete `nvidia-smi -q` record, GPU identity, and current runtime visibility.
- Exact command: `nvidia-smi -q`; raw output `notes/nvidia-smi-q.txt`; machine record `notes/driver_record.json`.
- Observed: NVIDIA driver `610.62` (nvidia-smi marks it deprecated for CUDA 14), reported CUDA version `13.3`, device `NVIDIA GeForce RTX 3050 Laptop GPU`, UUID recorded. Current b11259 CUDA 13.4 llama CLI previously reports zero devices despite nvidia-smi seeing GPU 0.
- Routes: (1) obtain same-commit CUDA 12.4-compatible Windows build and require `--list-devices` CC 8.6; (2) diagnose Optimus/PATH DLL routing or update/revalidate driver/runtime pair. Cheapest next experiment: run CUDA 12.x package `--list-devices` from its own directory with `nvidia-smi -L` captured.

### Status / Numbers / Next Experiment
- Status: Driver fact recorded; working llama.cpp CUDA pair not established.
- Numbers: driver 610.62, reported CUDA 13.3, RTX 3050 CC 8.6 from prior hardware record, b11259 CUDA 13.4 CLI device list empty.
- Next Experiment: CUDA 12.4 build discovery and device-list check before any model load.

## E0-CUDA124-20260929 — same-commit runtime trial

- Hypothesis/target: official b11259 Windows CUDA 12.4 binary matching commit `d280808f5` exposes the RTX 3050 where CUDA 13.4 did not; require `--list-devices` with one device and CC 8.6.
- Asset: `runtimes/llama-b11259-bin-win-cuda-12.4-x64.zip`, 264,528,828 bytes, API/local SHA `4f0551811b6e836344a90176583031f9ac0fe258359eb3f0bc94c81a88087cd5`; version build 11259/d280808f5. Commands ran with extracted DLL directory on PATH.
- Result: `--version` exit 0; `--list-devices` exit 0 but exact output `Available devices:\n  (none)`. Existing CUDA 13.4 b11259 directory produces the same. No model load or CUDA support claim.
- Routes: diagnose Optimus/PATH/backend initialization or update/retest driver; alternatively use WSL2/source build with a validated CUDA backend. Cheapest experiment: capture `nvidia-smi -L` beside a same-directory `--list-devices` run, then test a runtime build with known CUDA 12.x dependencies.

### Status / Numbers / Next Experiment
- Status: CUDA 12.4 asset hash/version verified; device enumeration remains zero.
- Numbers: driver 610.62, reported CUDA 13.3, CC 8.6 hardware; CUDA 12.4 and 13.4 CLIs both report zero devices.
- Next Experiment: acquire exact IQ3_S only after route hash enforcement, then CPU/load smoke if CUDA backend remains unavailable.

## E0-IQ3S-ROUTEA-MISMATCH-20260929 — parallel aria2 acquisition

- Hypothesis/target: 16-connection resumable aria2 against the exact HF URL reaches 12,040,883,104 bytes and SHA `d847e2...3864` within three hours. Initial script used `--check-integrity=false`; corrected script now enforces SHA checksum.
- Result: route reached full **12,040,883,104 bytes** at measured average **45.666588 MiB/s**, but observed SHA was `172f90b528c1c87f80dd58807771c1f7ce5cdc40632ecded65e311bdafd16565`, not the expected digest. The artifact and `.aria2` state were removed; no bytes are treated as verified. Canonical mismatch record is `notes/iq3s_acquisition_routeA.json`.
- Constraint/routes: byte count matched but integrity failed. Route A: rerun with aria2 checksum enforcement and immutable revision/file metadata; Route B: trusted exact copy verified locally. Cheapest next experiment: rerun corrected `scripts/s18_aria2_iq3s.ps1` with `--checksum` and then inspect HTTP commit/ETag binding before load.

### Status / Numbers / Next Experiment
- Status: High-throughput route works but produced a digest mismatch; baseline remains blocked.
- Numbers: 12,040,883,104 bytes, 45.666588 MiB/s, expected SHA d847e2..., observed SHA 172f90..., verified bytes 0.
- Next Experiment: checksum-enforced resumable acquisition from an immutable revision or trusted cache.

## E1-SHARD-SMOKE-20260930 — measured
- Hypothesis/target: one verified BF16 shard can be group-128 absmean fake-quantized without crossing the 8 GiB RSS ceiling and without loading the full checkpoint.
- Result: measured. Shard 66a8888c9a4bad0b8e450c82effb3f79d57ba20f1d85cc9108175e94ac140de8. 16 FFN tensors, layers 10–14 complete, layer 15 only gate_proj. 6.81 s. torch 2.14.1+cpu. group 128, 8 tokens, hidden 5120.
- Numbers: down_proj output MSE 0.534–0.547; gate_proj 0.162–0.167; up_proj 0.155–0.159. Per-tensor RSS high-water 3.52 GB. JSON peak_rss_bytes 542 MB is invalid on this Windows run.
- Not claimed: agreement alpha, full-model load, remaining 17 shards, quality pass.
- Next Experiment: E1 agreement remains unmeasured. Do not open E2. The next slice is the pre-registered remote agreement handoff, not another local weight load.

## E0-METADATA-ONLY-1D4BF0F-20261001 — measured inventory

- Hypothesis/target: an isolated no-weight metadata directory records revision `1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0` as `pinned-sha-input-unverified`, SHA-256 for present small metadata files only, and script status `missing` for absent weight classes. Target: 0 weight bytes downloaded and 0 weight files hashed.
- Exact commands: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\s02_fetch_metadata.ps1 -Revision 1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0 -ModelPath notes\e0-metadata-1d4bf0f`; `powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\s02_model_manifest.ps1 -ModelPath notes\e0-metadata-1d4bf0f -Output models\qwen3.8-27b-manifest.json -Revision 1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0 -Offline`.
- Result: the metadata directory was absent before fetch, so it held no matching weight files. Both commands completed; the manifest reports 7 present metadata files, `source_revision_status=pinned-sha-input-unverified`, `compatibility.status=unverified`, 1 index listing 1,199 tensors across 18 shards, and all 18 indexed shards absent from this isolated directory. The script's component status `missing` applies to language, embeddings, GDN, attention, vision, tokenizer, and MTP; processor status is `present` for its metadata. Here `missing` means requirement-unavailable for this run, not a fabricated checksum or complete component support. `tokenizer_revision` and `processor_revision` remain `unresolved`.
- Present-file SHA-256: `chat_template.jinja` c3cf9e34abf4f9e36c2d72165aa9c132d3e2a725b6c2586aaa3a8af9d7a81041; `config.json` 191e0af232104ed8b65258cf3fb2b842e288008baca7633c11b82a1ac7203aab; `generation_config.json` e70c136c1b78ddc1fb0905bac8e733a4dc448d4f852a5dd75143fffc70be550e; `model.safetensors.index.json` 77042094076611b69791a610065f28b7013b8c621795fa86ddccc8bac7d1b9df; `preprocessor_config.json` 27225450ac9c6529872ee1924fcb0962ff5634834f817040f444118116f4e516; `tokenizer_config.json` b11349aafa7cdc6a320767cf7ceb29ed82f7eda5d65e8e0819e76f0ce947bf27; `video_preprocessor_config.json` 7768af27c1fafa9cc9011c1dc20067e03f8915e03b63504550e11d5066986d13.

### Status / Numbers / Next Experiment
- **Status:** Metadata-only inventory measured; REQ-E0-03 remains partial and E0 is not complete. No model load or weight hash claimed.
- **Numbers:** 7 present metadata files with SHA-256; 0 weight bytes downloaded; 0 weight files hashed; 18/18 indexed shards absent from this directory.
- **Next Experiment:** On a separately approved metadata-only path, pin and record tokenizer/processor revisions and acquire missing tokenizer/processor metadata if available; expected result is a revised manifest with verifiable metadata provenance while absent weights remain explicitly `missing`. Do not start 01-07 or 01-08 from this entry.

## E0-IQ3S-RERUN-20261001-120443 — measured recovered-command rerun

- Hypothesis/target: at context 2048, the recovered IQ3_S command stays near the previously supplied 1.8 decode / 10.3 prefill tok/s bar with non-null GPU-memory and process working-set peaks. One run, `-n 128`; target 0 weight bytes downloaded. This is a new measurement, not proof that PSReadLine history lines 725–733 produced the old 1.8/10.3 packet.
- Exact command (working directory `C:\lab\ailocal\runtimes\llama-b11259-cuda124`): `.\llama-cli.exe -m "C:\lab\ailocal\models\Qwen3.8-27B-UD-IQ3_S.gguf" -p "Write three sentences about why the sky is blue." -n 128 --seed 7 -c 2048 -ngl 16 -ctk q8_0 -ctv q8_0`. Command source: PSReadLine history lines 725–733; those lines are not tied to the original 1.8/10.3 result.
- Evidence: `experiments/raw/iq3-rerun/stdout.txt` (prompt 13.6 tok/s, generation 2.1 tok/s; answer followed by an interactive `>` prompt before process exit); `experiments/raw/iq3-rerun/sampler.jsonl` (2,355 samples at approximately one-second intervals). Sampler command: not recorded in these artifacts; no exact sampler command is claimed. After exit, GPU memory used was 72 MiB as supplied in the run handoff.
- Artifact/configuration: `C:\lab\ailocal\models\Qwen3.8-27B-UD-IQ3_S.gguf`, length checked at 12,040,883,104 bytes, not rehashed; context 2048, `-n 128`, seed 7, `-ngl 16`, q8_0 K/V. No weight download performed (0 bytes).

### Status / Numbers / Next Experiment
- **Status:** New recovered-command IQ3_S measurement recorded; not the original 1.8/10.3 packet. REQ-E0-03 remains partial and E0 remains open.
- **Numbers:** prompt/prefill 13.6 tok/s; generation/decode 2.1 tok/s; sampled GPU memory-used peak 3,828 MiB (device-wide); sampled `llama-cli` working-set peak 10,486,272,000 bytes; 2,355 samples; post-exit GPU memory used 72 MiB; weight bytes downloaded 0.
- **Next Experiment:** With separate authorization, capture a bounded non-interactive baseline and an exact recorded sampler command so peaks and completion can be independently reproduced; do not start 01-07 or 01-08 in this session.

## E0-IQ3S-SINGLE-TURN-20261001 — measured exit control

- Hypothesis/target: with only `--single-turn` added to the recovered IQ3_S command, prompt stays near 13.6 tok/s and generation near 2.1 tok/s at context 2048; the process exits after one answer. Target: 0 `llama-cli` processes after exit and GPU memory near the previous 72 MiB idle reading. Help confirmed `--single-turn` runs one turn and exits.
- Exact model command (working directory `C:\lab\ailocal\runtimes\llama-b11259-cuda124`): `.\llama-cli.exe -m "C:\lab\ailocal\models\Qwen3.8-27B-UD-IQ3_S.gguf" -p "Write three sentences about why the sky is blue." -n 128 --seed 7 -c 2048 -ngl 16 -ctk q8_0 -ctv q8_0 --single-turn`. No change to model, prompt, token count, seed, context, GPU layers, or KV types. Preflight: 0 `llama-cli` processes and 44.71% RAM used.
- Exact sampler command (parent PowerShell 1-second job body, writing `experiments/raw/iq3-rerun-exit/sampler.jsonl`): `$sampler=Start-Job -ArgumentList $samplePath -ScriptBlock {param($path); while($true){ $gpuText=& nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>$null; $gpuMiB=$null; if("$gpuText" -match '(\d+)'){$gpuMiB=[int64]$Matches[1]}; $ps=@(Get-Process -Name 'llama-cli' -ErrorAction SilentlyContinue); $ws=$null; if($ps.Count -gt 0){$ws=($ps | Measure-Object -Property WorkingSet64 -Maximum).Maximum}; [pscustomobject]@{utc=(Get-Date).ToUniversalTime().ToString('o');gpu_memory_used_mib=$gpuMiB;llama_cli_workingset_bytes=$ws} | ConvertTo-Json -Compress | Add-Content -LiteralPath $path; Start-Sleep -Seconds 1} }`; after the run, `Stop-Job $sampler; Receive-Job $sampler | Out-Null; Remove-Job $sampler`.
- Evidence: `experiments/raw/iq3-rerun-exit/stdout.txt`, `experiments/raw/iq3-rerun-exit/stderr.txt`, and `experiments/raw/iq3-rerun-exit/sampler.jsonl`. Command exit 0; stdout reports `[ Prompt: 11.4 t/s | Generation: 1.8 t/s ]`. Sampler recorded 69 samples, device-wide GPU memory-used peak 3,802 MiB, and `llama-cli` working-set peak 9,820,696,576 bytes. After exit: 0 `llama-cli` processes and device memory 73 MiB. No download command was run.

### Status / Numbers / Next Experiment
- **Status:** One-turn exit control measured; exit target met. The lower 11.4/1.8 tok/s speeds are new measurements, not the previous 13.6/2.1 run or original 1.8/10.3 packet. REQ-E0-03 remains partial; E0 remains open.
- **Numbers:** context 2048; `-n 128`; prompt 11.4 tok/s; generation 1.8 tok/s; GPU memory peak 3,802 MiB; process working-set peak 9,820,696,576 bytes; 69 samples; 0 processes after exit; idle GPU 73 MiB; weight bytes downloaded 0.
- **Next Experiment:** Only after separate approval, investigate run-to-run speed variance under matched temperature/power and warm-cache conditions; do not start 01-07 or 01-08 from this control.

- **Second run:** `E0-IQ3S-SINGLE-TURN-20261001` exact command and sampler repeated once under the same working directory. Preflight: 0 `llama-cli` processes, free RAM 9,413,955,584 bytes (44.4% used), idle GPU 74 MiB. Evidence: `experiments/raw/iq3-rerun-exit-2/stdout.txt`, `stderr.txt`, `sampler.jsonl`. Result: exit 0, 68 samples, prompt 11.4 tok/s, generation 1.7 tok/s, GPU peak 3,792 MiB, working-set peak 9,701,924,864 bytes, 0 processes after exit, GPU after exit 66 MiB. Delta versus the 11.4/1.8 run: prompt 0.0 tok/s; generation -0.1 tok/s; GPU peak -10 MiB; working set -118,771,712 bytes. Weight bytes downloaded 0. E0 remains open and REQ-E0-03 remains partial.

## E0-IQ3S-NGL18-20261001 — measured single-turn variation

- Hypothesis/target: change only `-ngl 16` to `-ngl 18` in the 11.4/1.7 command; generation should exceed 1.8 tok/s while GPU peak remains below 4,050 MiB. One run only; no retry authorized.
- Exact command (working directory `C:\lab\ailocal\runtimes\llama-b11259-cuda124`): `.\llama-cli.exe -m "C:\lab\ailocal\models\Qwen3.8-27B-UD-IQ3_S.gguf" -p "Write three sentences about why the sky is blue." -n 128 --seed 7 -c 2048 -ngl 18 -ctk q8_0 -ctv q8_0 --single-turn`. All other command tokens unchanged. Preflight: 0 `llama-cli` processes, 44.24% RAM used, idle GPU 70 MiB. Evidence: `experiments/raw/iq3-ngl18/stdout.txt`, `stderr.txt`, `sampler.jsonl`; sampler command was the same 1-second sampler recorded in the prior entry.
- Result: exit 0, 133 samples, 0 `llama-cli` processes after exit, GPU after exit 66 MiB. The process did not crash and GPU peak stayed below the 4,050 MiB stop threshold.

### Status / Numbers / Next Experiment
- **Status:** Single `-ngl 18` variation measured once; target generation increase was not met. E0 remains open and REQ-E0-03 remains partial. No retry of `-ngl 18`.
- **Numbers:** prompt 3.2 tok/s; generation 0.8 tok/s; GPU peak 3,895 MiB; working-set peak 9,577,857,024 bytes; delta versus 11.4/1.7 run: prompt -8.2 tok/s; generation -0.9 tok/s; GPU peak +103 MiB; working set -124,067,840 bytes; 0 processes after exit; GPU after exit 66 MiB.
- **Next Experiment:** Do not retry `-ngl 18` in this route. Keep the measured `-ngl 16` bar as the local comparison and preserve E0 gating; do not start 01-07 or 01-08.

## E0-IQ3S-NGL14-20261001 — measured single-turn variation

- Hypothesis/target: change only `-ngl 16` to `-ngl 14` in the 11.4/1.7 command; generation should be slower than the `-ngl 16` bar but faster than the `-ngl 18` result of 0.8 tok/s, with GPU peak below 3,800 MiB. One run; if generation is below 1.5 tok/s, stop the `-ngl` sweep.
- Exact command (working directory `C:\lab\ailocal\runtimes\llama-b11259-cuda124`): `.\llama-cli.exe -m "C:\lab\ailocal\models\Qwen3.8-27B-UD-IQ3_S.gguf" -p "Write three sentences about why the sky is blue." -n 128 --seed 7 -c 2048 -ngl 14 -ctk q8_0 -ctv q8_0 --single-turn`. All other command tokens unchanged. Preflight: 0 `llama-cli` processes, 39.86% RAM used, idle GPU 78 MiB. Evidence: `experiments/raw/iq3-ngl14/stdout.txt`, `stderr.txt`, `sampler.jsonl`; sampler command was the same 1-second sampler recorded in the prior entry.
- Result: exit 0, 117 samples, 0 `llama-cli` processes after exit, GPU after exit 74 MiB. The process did not crash and GPU peak remained below 3,800 MiB.

### Status / Numbers / Next Experiment
- **Status:** Single `-ngl 14` variation measured once; generation was below the 1.5 tok/s stop threshold, so the `-ngl` sweep is stopped. E0 remains open and REQ-E0-03 remains partial.
- **Numbers:** prompt 5.7 tok/s; generation 0.9 tok/s; GPU peak 3,475 MiB; working-set peak 10,167,472,128 bytes; delta versus 11.4/1.7 run: prompt -5.7 tok/s; generation -0.8 tok/s; GPU peak -317 MiB; working set +465,547,264 bytes; 0 processes after exit; GPU after exit 74 MiB.
- **Next Experiment:** Keep `-ngl 16` as the canonical local bar; do not retry `-ngl 18`, do not continue the `-ngl` sweep, and do not start 01-07 or 01-08.

## E0-IQ3S-THREAD-DISCOVERY-20261001 — measured, count not found

- Hypothesis/target: run the unchanged 11.4/1.7 command through `cmd.exe /c` with stdout and stderr captured separately; stderr was expected to expose an `n_threads` line. One run only; no `-t` or `--threads` flag added.
- Exact command: `cmd.exe /c '.\llama-cli.exe -m "C:\lab\ailocal\models\Qwen3.8-27B-UD-IQ3_S.gguf" -p "Write three sentences about why the sky is blue." -n 128 --seed 7 -c 2048 -ngl 16 -ctk q8_0 -ctv q8_0 --single-turn > "C:\lab\ailocal\experiments\raw\iq3-threads-discover\stdout.txt" 2> "C:\lab\ailocal\experiments\raw\iq3-threads-discover\stderr.txt"'`, working directory `C:\lab\ailocal\runtimes\llama-b11259-cuda124`. Same 1-second sampler as the 11.4/1.7 run. Preflight: 0 `llama-cli` processes, 39.93% RAM used, idle GPU 82 MiB.
- Result: exit 0. `stdout.txt` reports prompt 11.2 tok/s and generation 1.7 tok/s. `stderr.txt` contains no `n_threads` or thread-count line. Thread count: **not-found**; no count invented. Evidence: `experiments/raw/iq3-threads-discover/stdout.txt`, `stderr.txt`, `sampler.jsonl`; sampler recorded 68 samples, GPU peak 3,792 MiB and working-set peak 10,357,649,408 bytes.

### Status / Numbers / Next Experiment
- **Status:** Thread-count discovery completed; n_threads line not found. No new thread count selected or tested. E0 remains open and REQ-E0-03 remains partial.
- **Numbers:** prompt 11.2 tok/s; generation 1.7 tok/s; GPU peak 3,792 MiB; working-set peak 10,357,649,408 bytes; 68 samples; exit 0; no thread count reported.
- **Next Experiment:** Do not launch a thread-count variation without a separately recorded default thread count; do not start 01-07 or 01-08.

## E0-IQ3S-HASH-20261001 — measured artifact identity

- Path: `C:\lab\ailocal\models\Qwen3.8-27B-UD-IQ3_S.gguf`
- Bytes: `12040883104`
- SHA-256: `d847e2c1e4aa276e4b7b8e9ad7628050e61e165d49ab995407bc36677a6f3864`
- Result: **match** against the expected size and digest. `models\ignored\` was not hashed.
- Status: REQ-E0-03 remains partial because the 18 source shards are still absent; E0 remains open.

## E0-IQ3S-QUALITY-5-20261001 — five-prompt text smoke

- Hypothesis/target: change only `-p` across frozen `text-001` through `text-005` from `quality/prompts/text_50.json`; keep IQ3_S, `-n 128 --seed 7 -c 2048 -ngl 16 -ctk q8_0 -ctv q8_0 --single-turn`. Five independent processes should exit 0 and produce five distinct stdout files. This is not scoring the full 50-prompt suite.
- Preflight: 0 `llama-cli` processes, RAM used 38.27%. Working directory: `C:\lab\ailocal\runtimes\llama-b11259-cuda124`. Each process used `.\llama-cli.exe -m "C:\lab\ailocal\models\Qwen3.8-27B-UD-IQ3_S.gguf" -p <exact text-00N prompt from quality/prompts/text_50.json> -n 128 --seed 7 -c 2048 -ngl 16 -ctk q8_0 -ctv q8_0 --single-turn`; stdout redirected to its own `experiments/raw/iq3-quality-5/text-00N.txt`, stderr to `text-00N.stderr.txt`. Confirmed no `llama-cli` process remained after each exit.
- `text-001`: exit 0; `experiments/raw/iq3-quality-5/text-001.txt`; prompt 10.2 tok/s, generation 1.7 tok/s.
- `text-002`: exit 0; `experiments/raw/iq3-quality-5/text-002.txt`; prompt 11.2 tok/s, generation 1.1 tok/s.
- `text-003`: exit 0; `experiments/raw/iq3-quality-5/text-003.txt`; prompt 5.4 tok/s, generation 1.0 tok/s.
- `text-004`: exit 0; `experiments/raw/iq3-quality-5/text-004.txt`; prompt 5.6 tok/s, generation 0.9 tok/s.
- `text-005`: exit 0; `experiments/raw/iq3-quality-5/text-005.txt`; prompt 5.0 tok/s, generation 0.9 tok/s.

### Status / Numbers / Next Experiment
- **Status:** Five prompt-only variations completed, with five exit-0 runs and separate stdout/stderr evidence. E0 remains open; REQ-E0-03 remains partial. No 50-prompt score claimed.
- **Numbers:** 5 stdout files; 5 stderr files; generation 0.9–1.7 tok/s, so the near-1.7 hypothesis was not sustained across prompts; 0 processes remaining after each run.
- **Next Experiment:** Inspect the five raw outputs and prompt-length/thermal effects before any broader quality scoring; do not start 01-07 or 01-08 or run `text-006` from this slice.

## E0-IQ3S-FA-20261001 — measured flash-attention variation

- Hypothesis/target: with only the help-confirmed flash-attention flag `-fa on` added, generation should exceed 1.8 tok/s and GPU peak remain below 3,900 MiB; one run only.
- Exact command: `cmd.exe /c '.\llama-cli.exe -m "C:\lab\ailocal\models\Qwen3.8-27B-UD-IQ3_S.gguf" -p "Write three sentences about why the sky is blue." -n 128 --seed 7 -c 2048 -ngl 16 -ctk q8_0 -ctv q8_0 --single-turn -fa on > "C:\lab\ailocal\experiments\raw\iq3-fa\stdout.txt" 2> "C:\lab\ailocal\experiments\raw\iq3-fa\stderr.txt"'`, working directory `C:\lab\ailocal\runtimes\llama-b11259-cuda124`. Help syntax copied: `-fa, --flash-attn [on|off|auto] ... (default: auto)`. Preflight: 0 `llama-cli` processes, 39.23% RAM used, idle GPU 84 MiB. Same 1-second sampler.
- Result: exit 0, 69 samples. Evidence: `experiments/raw/iq3-fa/stdout.txt`, `stderr.txt`, `sampler.jsonl`; prompt 10.9 tok/s, generation 1.7 tok/s, GPU peak 3,792 MiB, working-set peak 10,142,789,632 bytes.

### Status / Numbers / Next Experiment
- **Status:** Flash attention `-fa on` measured once; target generation increase was not met (1.7 <= 1.8). GPU peak stayed below 3,900 MiB. Leave flash attention off for the canonical comparison. E0 remains open and REQ-E0-03 remains partial.
- **Numbers:** prompt 10.9 tok/s; generation 1.7 tok/s; GPU peak 3,792 MiB; working-set peak 10,142,789,632 bytes; delta versus 11.4/1.7 run: prompt -0.5 tok/s; generation 0.0 tok/s; GPU peak 0 MiB; working set +440,864,768 bytes; exit 0; 69 samples.
- **Next Experiment:** Freeze `-fa` off for the canonical `-ngl 16` comparison; do not start 01-07 or 01-08.

## E0-IQ3S-KV-Q4-20261001 — measured KV-cache variation

- Hypothesis/target: change only both KV cache types from q8_0 to legal `q4_0`; GPU peak should drop at least 100 MiB from 3,792 MiB, generation should remain at least 1.5 tok/s, and the process should exit by itself. One run only.
- Help confirmation: `-ctk/-ctv` both list `q4_0` as legal. Exact command: `cmd.exe /c '.\llama-cli.exe -m "C:\lab\ailocal\models\Qwen3.8-27B-UD-IQ3_S.gguf" -p "Write three sentences about why the sky is blue." -n 128 --seed 7 -c 2048 -ngl 16 -ctk q4_0 -ctv q4_0 --single-turn > "C:\lab\ailocal\experiments\raw\iq3-kv-q4\stdout.txt" 2> "C:\lab\ailocal\experiments\raw\iq3-kv-q4\stderr.txt"'`. Same 1-second sampler. Preflight: 0 `llama-cli` processes, 36.48% RAM used, idle GPU 80 MiB.
- Result: exit 0, 67 samples, 0 `llama-cli` processes after exit, GPU after exit 67 MiB. Evidence: `experiments/raw/iq3-kv-q4/stdout.txt`, `stderr.txt`, `sampler.jsonl`; prompt 11.1 tok/s, generation 1.7 tok/s, GPU peak 3,781 MiB, working-set peak 10,653,560,832 bytes.

### Status / Numbers / Next Experiment
- **Status:** Legal q4_0/q4_0 KV variation measured once. Generation met the minimum, but GPU peak reduction was only 11 MiB, below the 100 MiB target. Keep q8_0 as the canonical KV type. E0 remains open and REQ-E0-03 remains partial.
- **Numbers:** prompt 11.1 tok/s; generation 1.7 tok/s; GPU peak 3,781 MiB; working-set peak 10,653,560,832 bytes; delta versus 11.4/1.7 run: prompt -0.3 tok/s; generation 0.0 tok/s; GPU peak -11 MiB; working set +951,635,968 bytes; exit 0; 67 samples.
- **Next Experiment:** Keep q8_0/q8_0 as canonical KV; do not start 01-07 or 01-08.

## E0-IQ3S-NGRAM-SIMPLE-20261001 — measured speculative variation

- Hypothesis/target: add only `--spec-type ngram-simple` to the exact 11.4/1.7 command, using binary-default n-gram sizes; generation should remain at least 1.7 tok/s, with >2.0 tok/s as the success target. One run only.
- Exact command: `cmd.exe /c '.\llama-cli.exe -m "C:\lab\ailocal\models\Qwen3.8-27B-UD-IQ3_S.gguf" -p "Write three sentences about why the sky is blue." -n 128 --seed 7 -c 2048 -ngl 16 -ctk q8_0 -ctv q8_0 --single-turn --spec-type ngram-simple > "C:\lab\ailocal\experiments\raw\iq3-ngram\stdout.txt" 2> "C:\lab\ailocal\experiments\raw\iq3-ngram\stderr.txt"'`, working directory `C:\lab\ailocal\runtimes\llama-b11259-cuda124`. No `-md` file and no n-gram size flags. Preflight: 0 `llama-cli` processes, 37.48% RAM used, idle GPU 77 MiB. Same 1-second sampler.
- Result: exit 0, 68 samples, 0 `llama-cli` processes after exit, GPU after exit 68 MiB. Evidence: `experiments/raw/iq3-ngram/stdout.txt`, `stderr.txt`, `sampler.jsonl`; stdout reports prompt 10.7 tok/s and generation 1.7 tok/s. No acceptance or drafted-token count was printed, so none is claimed. GPU peak 3,792 MiB; working-set peak 10,391,375,872 bytes.

### Status / Numbers / Next Experiment
- **Status:** `--spec-type ngram-simple` measured once; generation met the minimum but did not exceed 2.0 tok/s. GPU peak stayed below 3,900 MiB. Leave n-gram speculation off for the canonical comparison. E0 remains open and REQ-E0-03 remains partial.
- **Numbers:** prompt 10.7 tok/s; generation 1.7 tok/s; GPU peak 3,792 MiB; working-set peak 10,391,375,872 bytes; delta versus 11.4/1.7 run: prompt -0.7 tok/s; generation 0.0 tok/s; GPU peak 0 MiB; working set +689,451,008 bytes; exit 0; 68 samples.
- **Next Experiment:** Leave n-gram speculation off; do not start 01-07 or 01-08.

## E0-IQ3S-CLOSED-CONTROLS-20261001 — freeze record

- **Status:** Closed local IQ3_S control variations; the canonical command remains the unchanged `-ngl 16`, `-ctk q8_0 -ctv q8_0`, `--single-turn` run with no `-fa`, no `--spec-type`, and no `-t`/`--threads`. E0 remains open and REQ-E0-03 remains partial.
- **Canonical bar:** prompt 11.4 tok/s; generation 1.7–1.8 tok/s at context 2048; GPU peak 3,792 MiB in the 11.4/1.7 control.
- **Closed results:** `-ngl 14` = 5.7 / 0.9; `-ngl 16` = 11.4 / 1.7–1.8; `-ngl 18` = 3.2 / 0.8; `-fa on` = 10.9 / 1.7; `-ctk q4_0 -ctv q4_0` = 11.1 / 1.7 with GPU delta -11 MiB; `--spec-type ngram-simple` = 10.7 / 1.7, acceptance not printed.
- **Dormant routes:** `draft-simple` until a GGUF under 1,000,000,000 bytes with `vocab_size=248320` exists; thread-count variation until a no-generation command prints `n_threads`; MTP on IQ2_XXS remains blocked.
- **Next Experiment:** No further local IQ3_S control variation in this slice. Do not start 01-07 or 01-08.

