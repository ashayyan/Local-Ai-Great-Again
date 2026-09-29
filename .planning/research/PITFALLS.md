# PITFALLS — Qwen3.8-27B on RTX 3050

**Scope.** Failure modes that can make a promising number look real while it is not: bandwidth, low-bit quality, speculation, sm_86 kernels, AVX2, PCIe streaming, Windows tooling, VLM eviction, and unsupported claims in the research brief. This is a risk register, not a verdict. Every blocker below has a measured constraint, two routes, and a cheapest next experiment.

## 1. Measurement protocol: the first failure mode

### Pitfall: confusing payload bandwidth, kernel time, and end-to-end tok/s
The brief's `25.6B parameters/token` is a useful lower-bound model, not a trace. It excludes scales/zeros, metadata, dequantization traffic, lm-head read choices, recurrent-state reads, allocator copies, synchronization, and any tensor that is reread. A nominal 180 GB/s therefore does **not** imply 180/5.3 = 34 tokens/s. Decode GEMV has poor occupancy at batch 1; PCIe and CPU copies can be on the critical path. Prefill GEMM numbers are not decode numbers.

**Mitigations/routes:** (A) report separately: device DRAM bytes from Nsight/benchmark, wall-clock prefill and decode, and effective payload GB/s; pin clocks/power mode and warm up. (B) add a synthetic one-token GEMV with exactly the packed format and a model-level run; use the gap as overhead rather than silently folding it into a ceiling.

**Cheapest experiment (one variable):**
```powershell
# llama.cpp, fixed model/context; capture its own timing lines
./llama-bench.exe -m .\models\qwen3.8-27b-q4.gguf -p 0 -n 128 -b 1 -ub 1 -ngl 99
```
Target: repeatable decode within ±5% over three runs; record actual model bytes, `t/s`, VRAM peak, and inferred effective GB/s. Then run `-b 512` as a separate prefill experiment. A failed/unstable result is a measurement blocker, not evidence about the model.

### Pitfall: RTX 3050 is not one bandwidth number
Laptop 3050 configurations vary (4/6/8 GB, 35–80 W, 64/128-bit memory bus, clocks, shared system memory). The brief's 168–224 GB/s range is an unverified assumption. PCIe link may be Gen3 x8 or x4 and power/thermal throttling changes throughput.

**Routes:** (A) identify SKU with `nvidia-smi --query-gpu=name,memory.total,pci.bus,clocks.gr,power.limit --format=csv`; (B) use measured copy and CUDA bandwidth, not a desktop 3050 spec sheet, and repeat cold/hot.

**Cheapest experiment:**
```powershell
nvidia-smi --query-gpu=name,memory.total,pci.bus,clocks.gr,power.limit --format=csv
bandwidthTest.exe  # CUDA samples, pinned H2D/D2H and device-to-device
```
Expected output: actual VRAM, bus/link facts, and D2D GB/s. If CUDA samples are unavailable, `llama-bench` plus `nvidia-smi dmon -s pucm` is the fallback.

## 2. Low-bit quality and footprint traps

### Pitfall: ideal bit arithmetic is not a deployable model
`27e9 × 1.58/8 = 5.33 GB` assumes pure payload. Ternary encodings often use 2 bits/weight (6.75 GB before scales), alignment, group scales, tensor headers, scratch buffers, CUDA workspaces, KV/state, and the untied 1.27B lm_head. The brief's 5.3 GB mixed estimate can therefore exceed a 6 GB card even at context 2048. Conversely, a 4-bit checkpoint of 14 GB cannot be treated as a 4-bit verifier resident on a 6 GB card.

**Routes:** (A) calculate `file size + runtime allocations + KV/state + safety margin` from the actual artifact; reserve 5–10% VRAM. (B) keep lm_head/vision/FFN residual in RAM and use a true packed ternary kernel; do not call a simulation a fit.

**Cheapest experiment:**
```powershell
Get-Item .\models\*.gguf | Select Name,Length
./llama-cli.exe -m .\models\candidate.gguf -c 2048 -n 64 -ngl 99 --no-display-prompt
```
Expected: load success, peak VRAM, and allocation failure boundary. Sweep only `-ngl` after this baseline; log each failure in `experiments/LOG.md`.

### Pitfall: PTQ benchmark transfer is invalid
The brief uses Llama-2/Llama-3 AQLM/QTIP results and a Qwen W4A4 result to motivate Qwen3.8 ternary. Architecture, tokenizer, calibration corpus, recurrent GDN dynamics, untied head, and instruction tuning differ. PPL can improve while task behavior, multimodal grounding, or long-context stability collapses. “Within 0.1–0.2” BitDistill results are small models (≤4B), not evidence at 27B.

**Routes:** (A) establish FP16/NVFP4 reference PPL and fixed 50-prompt scores on *this* tokenizer/model; compare per-layer/block error and logit KL, not only aggregate PPL. (B) use layer-wise distillation/QAT on a representative calibration corpus before end-to-end claims; evaluate image prompts separately.

**Cheapest experiment:** run 128 fixed text sequences at 2,048 tokens through FP/NVFP4 and candidate quant, compute PPL and token agreement; target candidate PPL delta ≤15% and agreement distribution reported (not just mean). If no reference fits, use teacher logits streamed one layer at a time and record that limitation.

### Pitfall: calibration leakage and cherry-picked prompts
A 200-prompt agreement test can be inflated by greedy decoding, short/easy prompts, or using the same calibration data for quantization and evaluation. Token acceptance also depends on temperature and tokenizer exactness.

**Routes:** (A) pre-register disjoint calibration/evaluation sets and deterministic seeds; (B) report stratified text/code/math/long-context/VLM subsets with median and p05 acceptance, plus a BF16/NVFP4 reference.

**Cheapest experiment:** create `quality/prompts.jsonl` with 50 prompts per stratum, hash it, and run greedy and temperature 0.7 separately. Expected result: confidence intervals and failure examples, not a single quality headline.

## 3. Speculative decoding pitfalls

### Pitfall: acceptance is not speedup
Acceptance length `α` or `τ` does not include draft cost, verifier batching efficiency, sampling overhead, tree bookkeeping, or extra KV/state copies. The brief's T1 estimate (cycle ≈435 ms, ≈7 tok/s) mixes an assumed CPU residual read with assumed token times and is not a measurement. Native MTP can slow down (the brief itself cites a −24% report).

**Routes:** (A) measure baseline and speculation with identical prompt, output length, sampler, context, and warmup; report wall tok/s, accepted tokens/cycle, verifier batch latency, and p50/p95 inter-token latency. (B) sweep draft length 1/2/4/8 and disable speculation when acceptance or batch efficiency falls below break-even.

**Cheapest experiment:**
```powershell
./llama-cli.exe -m .\models\candidate.gguf -ngl 99 -c 2048 -n 256 --timing
# Then repeat with the runtime's documented Qwen MTP/speculator flag only; no other change.
```
Target: speculation must exceed baseline wall tok/s by ≥10% across 3 seeds and not worsen p95 latency by >20%. If the runtime has no native flag, record “unsupported,” do not infer from paper τ.

### Pitfall: exact-distribution claim is conditional
A low-bit drafter plus higher-quality verifier can preserve the verifier distribution only if rejection sampling, logits, tokenizer, RNG, and KV/state handling are correct. A ternary base plus RAM residual is not automatically “4-bit quality by construction”; approximate logits, stale recurrent state, quantized softmax, or greedy acceptance break equivalence.

**Routes:** (A) first test speculative loop against a CPU/PyTorch reference with identical logits and seeded sampling; (B) fall back to draft-only speed/quality characterization if exact verification cannot be proven.

**Cheapest experiment:** on 100 short prompts, compare speculative output to an unfused verifier using identical seed; expected mismatch rate is 0 for exact implementation (apart from documented floating-point ties). Any mismatch blocks quality claims and routes to a correctness test before optimization.

## 4. sm_86 CUDA/kernel traps

### Pitfall: “sm_80–sm_90 supported” does not mean sm_86 fast or correct
A kernel may compile via PTX JIT yet use unavailable tensor-core modes, unsupported `cp.async` assumptions, register-heavy code, or a fallback FP16 path. INT2/ternary lookup/dequant kernels can be memory-bound, occupancy-limited, or numerically wrong for Qwen's 5120×17408 shapes. First-run PTX JIT contaminates timing.

**Routes:** (A) build explicit `-arch=sm_86`, run correctness against reference, warm up, and inspect achieved occupancy/bandwidth with Nsight Compute. (B) retain a known-good FP16/INT8 fallback and compare per-layer outputs before any speed claim.

**Cheapest experiment:**
```powershell
cmake -S . -B build -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=86
cmake --build build --config Release -j 4
# run twice; discard first JIT run
```
Expected: no PTX fallback warning, second-run timing, max absolute/relative error on a fixed GEMV fixture. If compiler/toolkit lacks sm_86 support, route to a compatible CUDA container/WSL build or CPU reference and report the toolchain blocker.

### Pitfall: benchmark shape mismatch
Batch-16/32 GEMM papers and desktop GPUs do not predict batch-1 decode on a laptop. GDN has recurrent operations; only 16 layers are full attention according to the brief, so generic attention kernels may measure the wrong path.

**Routes:** (A) benchmark exact Qwen hidden/intermediate/head shapes at M=1 and M=4/8/16; (B) separately benchmark prefill and decode and verify model layer types from `config.json`/implementation.

**Cheapest experiment:** run a synthetic GEMV fixture with `M={1,4,8,16}`, dimensions 5120×17408, same packing and activation dtype; target monotonic tokens-per-weight-read improvement at M>1. Record correctness and achieved GB/s for each M.

## 5. CPU AVX2 pitfalls

### Pitfall: AVX-512 evidence does not transfer to AVX2
FairyFuse's cited result uses BMI2/AVX-512 masked operations. A laptop AVX2 implementation has different lane width, gather/packing cost, cache behavior, and may not have BMI2. “70% of STREAM” is not guaranteed for a ternary GEMV: bit unpacking and 17,408×5,120 dimensions add compute and rereads.

**Routes:** (A) implement scalar correctness → AVX2 FMA/bit-select kernel with 32/64-byte blocking and benchmark against STREAM; (B) use a proven bitnet.cpp/oneDNN path and compare CPU-only versus CPU+GPU split, including copy/sync time.

**Cheapest experiment:**
```powershell
# build the actual AVX2 microbenchmark (MSVC)
cmake -S . -B build-avx2 -DENABLE_AVX2=ON
cmake --build build-avx2 --config Release
.\build-avx2\Release\ternary_gemv_bench.exe --m 1 --k 5120 --n 17408 --iters 100
```
Target: ≥70% of measured STREAM triad *and* output error ≤1e-3 versus scalar on 100 random vectors. If below target, route to blocked packing/AVX2 lookup or move only the FFN to GPU; do not extrapolate FairyFuse's tok/s.

### Pitfall: Windows scheduling and memory behavior
Power plans, Defender scans, NUMA/thread affinity, page faults, and thermal throttling make a single CPU run meaningless. AVX2 may lower all-core frequency.

**Routes:** (A) pin process affinity/priority and use repeated medians with warm pages; (B) benchmark WSL2/Linux and native Windows separately, documenting clocks and RAM bandwidth.

**Cheapest experiment:** 10 warm runs with `Measure-Command`, fixed process affinity, and `nvidia-smi dmon`/Task Manager memory logs. Expected: coefficient of variation <5%; otherwise treat the run as environment-noisy and collect clocks/temperature before optimization.

## 6. PCIe streaming and tiering

### Pitfall: hidden-state transfer estimates omit synchronization and topology
The brief estimates ~10 KB/layer and ~30 µs sync, but pageable copies, WDDM scheduling, launch latency, pinned-buffer setup, PCIe Gen3 x4/x8 direction, and CPU/GPU dependency barriers can dominate. Streaming weights (GB/token) over PCIe cannot meet GPU DRAM assumptions: Gen3 x4 is about 3.9 GB/s theoretical, far below 150–224 GB/s VRAM.

**Routes:** (A) keep weights in RAM but stream only hidden states; double-buffer pinned transfers and overlap copy/compute. (B) if weights must cross PCIe, quantize/chunk, prefetch N+1, and model the link as the bottleneck; compare mmap/page-fault versus explicit pinned I/O.

**Cheapest experiment:**
```powershell
bandwidthTest.exe  # record pageable/pinned H2D/D2H at 1 KB, 10 KB, 1 MB
nvidia-smi -q -d PCI
```
Expected: measured per-transfer latency and GB/s for the actual link. Set a go/no-go target of ≤10% of token wall time for hidden-state copies; if exceeded, route to fewer synchronization points or CPU-resident execution.

### Pitfall: mmap is not asynchronous SSD prefetch
Windows file cache, compressed pages, antivirus, and SSD queue depth can make the first token or occasional token stall. A model fitting in RAM is not proof that it fits in VRAM or that pages are resident.

**Routes:** (A) explicit sequential read + pinned host staging + double buffering; (B) pre-load hot tensors into RAM and instrument page faults/cache hits; retain an SSD-cold benchmark.

**Cheapest experiment:** run 3 cold and 3 warm decode sessions while logging `Get-Counter '\Memory\Page Faults/sec'` and disk throughput. Expected: cold/warm tok/s gap <10% for a usable warm tier; otherwise report cold-start and steady-state separately.

## 7. Windows tooling pitfalls

### Pitfall: WDDM and build/runtime mismatch
Windows WDDM can add scheduling/jitter; CUDA, driver, MSVC, CMake, cuBLAS, and runtime ABI versions can silently select fallback kernels. Linux-only tooling (Nsight CLI, perf, huge pages, fork-based loaders) may not map to native Windows. “Runs” is not reproducibility.

**Routes:** (A) pin a tested CUDA/driver/MSVC matrix in `notes/toolchain.md`; package exact binaries and command lines. (B) use WSL2 for Linux-only profilers while retaining native Windows user path; compare outputs and timings.

**Cheapest experiment:** capture `nvidia-smi`, `nvcc --version`, `cmake --version`, compiler version, llama.cpp commit, model SHA256, and command in an experiment record. Expected: a second run on the same machine reproduces within ±5%; if not, fix environment before tuning.

### Pitfall: VRAM/RAM numbers are sampled, not peaks
Task Manager and occasional `nvidia-smi` polling miss short allocation peaks; Windows can report shared GPU memory as available VRAM. A load that appears to fit can fail during vision prefill or context growth.

**Routes:** (A) instrument CUDA `mem_get_info` around every phase and poll `nvidia-smi dmon` at high frequency; (B) use CUDA memory pool stats and explicit phase barriers, with 10% headroom.

**Cheapest experiment:** run text-only, image prefill, and decode separately at context 512/2048, recording minimum free VRAM. Expected: no phase crosses zero and image phase returns to the decode baseline after ViT eviction.

## 8. VLM eviction and visual-token pitfalls

### Pitfall: ViT eviction is more than freeing weights
The brief assumes an ~0.8 GB BF16 vision tower can be staged then evicted. Vision embeddings, projector activations, CUDA graph captures, allocator fragmentation, and KV entries for visual tokens remain. Freeing the module does not guarantee allocator reuse; asynchronous kernels may still reference buffers.

**Routes:** (A) hard phase boundary: synchronize, measure, release vision tensors, empty/rebuild memory pool, then decode; (B) CPU-offload vision and project embeddings, retaining only the required language-side inputs, with an explicit memory budget.

**Cheapest experiment:** image-only prefill followed by 256-token decode; record `cudaMemGetInfo` before ViT, after ViT, after embeddings, and after `cudaDeviceSynchronize()`. Expected: recovered bytes match freed tensors within allocator overhead (<5%); otherwise identify live references before claiming eviction.

### Pitfall: visual token pruning can delete task-critical evidence
The brief cites 11.1% retention and 93% performance, but aggregate VLM scores conceal OCR, small-object, chart, multi-image, and multi-step failures. GDN's constant recurrent state reduces KV growth but does not make visual prefill compute or information free.

**Routes:** (A) dynamic pruning with uncertainty/recovery tokens and a no-prune fallback; (B) retain high-resolution/OCR regions and evaluate image categories separately.

**Cheapest experiment:** 20 prompts each for OCR, chart, small object, spatial relation, and general captioning at 100%, 50%, 25%, 11% retention. Gate on per-category accuracy drop ≤5%; route failures to adaptive recovery rather than a global retention claim.

## 9. Claims audit and blocker reporting

The brief contains useful hypotheses but several statements are estimates or synthesis, not measurements on this machine: “5.3 GB fits 6 GB,” “ceiling 24 tok/s,” “T1 ≈7 tok/s,” “T3 6–8 tok/s,” “context nearly free,” and “quality by construction.” The Qwen config/model implementation, exact tensor counts, kernel availability, and future-dated citations must be verified against immutable model/runtime commits. Published results on RTX 6000 Ada, Xeon AVX-512, custom accelerators, or MoE active-parameter counts cannot be directly transplanted to a 3050 dense decode.

**Routes:** (A) label every number `measured`, `derived`, `reported`, or `hypothesis`; require model SHA, command, hardware, and confidence interval. (B) build a falsification matrix: each thesis gets one cheap microbenchmark before engineering work and a quality gate before optimization.

**Cheapest experiment:** make `experiments/LOG.md` with columns: hypothesis/target, command, model SHA, quant, context, VRAM peak, RAM peak, prefill tok/s, decode tok/s, quality sample, status. Run the exact bandwidth, ternary GEMV, acceptance, and VLM phase tests above. Expected: a reproducible baseline table and explicit dormant triggers.

### Blocker rule applied
- **Constraint:** a 6 GB card minus 5.3–6.75 GB packed weights leaves 0 to 0.7 GB before KV/state/workspace; PCIe Gen3 x4 is ~3.9 GB/s versus ~150–224 GB/s device bandwidth; AVX-512 results do not establish AVX2 throughput.
- **At least two routes:** (1) true packed mixed ternary with lm_head/ViT staged outside VRAM and measured kernel; (2) CPU/GPU split with hidden-state-only pinned transfers; additional route is layer/sub-layer scheduling with explicit prefetch.
- **Cheapest next experiment:** identify the actual SKU and run `llama-bench` plus the exact AVX2 GEMV and pinned-transfer microbenchmarks. Expected measurable outputs are VRAM fit boundary, effective GB/s, copy latency, and output error. Three failed attempts on one route require forking the route and recording “dormant because” plus a revisit trigger.

## Status / Numbers / Next Experiment

**Status:** Research-brief numbers are useful bounds and hypotheses, not yet machine measurements. Highest-risk claims are packed ternary footprint, speculative speed, AVX2 transfer, PCIe overlap, and VLM memory reclamation. No claim should pass the quality gate until text and image evaluations use the same tokenizer/model revision and fixed prompts.

**Numbers:** 4–8 GB VRAM SKU range; nominal 168–224 GB/s is unverified; 5.33 GB is ideal 1.58-bit payload while 2-bit packing is 6.75 GB before overhead; PCIe Gen3 x4 theoretical payload is ~3.9 GB/s; quality gate target is ≤+15% PPL delta and ≥3 decode tok/s, but neither is measured here. Acceptance α≥0.6 and 7 tok/s T1 are hypotheses, not results.

**Next Experiment:** Hypothesis: the actual laptop can sustain a stable, correctly implemented baseline and exposes the first bottleneck. Run, in order, (1) SKU/driver query and `llama-bench` at `-ngl 99,c=2048`, (2) exact packed ternary AVX2 GEMV versus scalar/STREAM, (3) pinned 10-KB H2D/D2H latency, then (4) 100-prompt baseline/speculation acceptance with identical seeds. Expected deliverable: one row per run in `experiments/LOG.md` with measured VRAM/RAM, prefill/decode tok/s, bandwidth, acceptance distribution, and a route decision.
