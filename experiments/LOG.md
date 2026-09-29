# Experiment Log

Every run records hypothesis, target, command, model, quant, context, VRAM/RAM peaks, prefill/decode speed, quality, script/hash, and Status / Numbers / Next Experiment.

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

