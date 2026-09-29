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

