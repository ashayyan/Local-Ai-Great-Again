# Phase 0.1 Research — Hardware Truth Baseline and Reproduction

**Scope:** design of a Windows-native, rerunnable E0 hardware probe for the actual RTX 3050 laptop. This document specifies commands, benchmark shapes, sampling, artifacts, schemas, and failure routes. It records no local measurements and must not be read as evidence that any probe has run.

## 1. Reproduction contract

The primary environment is native Windows PowerShell 7 (Windows PowerShell 5.1 is acceptable if the script avoids PS7-only syntax), MSVC, and a pinned CUDA toolkit. Each run should capture:

- UTC start/end time, hostname, Windows build, power source and power mode;
- probe script revision/hash and exact command line;
- `nvidia-smi`, `nvcc`, Python/PyTorch (if installed), compiler and CUDA runtime versions;
- exact GPU name, UUID, compute capability/SM, VRAM total, driver and clocks;
- raw samples, not only summary statistics; median, min/max, standard deviation and p95 where meaningful;
- an explicit `measured`, `derived`, `unavailable`, `error`, or `hypothesis` status for every number.

Run on AC with a fixed Windows power mode, after closing competing GPU/SSD workloads. Warm up each benchmark before timed repetitions. A second invocation should compare identity fields and report variance; it must not overwrite the first JSON artifact.

Suggested launcher (to be implemented as a numbered script such as `scripts/01_hardware_probe.ps1`):

```powershell
$ErrorActionPreference = 'Continue'
$run = "E0-HW-{0:yyyyMMdd-HHmmssZ}" -f ([DateTime]::UtcNow)
New-Item -ItemType Directory -Force artifacts/hardware/$run | Out-Null
Get-CimInstance Win32_OperatingSystem | Select Caption,Version,BuildNumber,LastBootUpTime
Get-CimInstance Win32_Processor | Select Name,NumberOfCores,NumberOfLogicalProcessors,MaxClockSpeed
Get-CimInstance Win32_PhysicalMemory | Select Capacity,Speed,Manufacturer,PartNumber
Get-Command nvidia-smi,nvcc,cl,cmake,python -ErrorAction SilentlyContinue |
  Select Name,Source,Version
nvidia-smi --query-gpu=name,uuid,compute_cap,driver_version,memory.total,memory.free,power.limit,temperature.gpu,clocks.gr,clocks.mem --format=csv,noheader,nounits
nvidia-smi -q -d CLOCK,POWER,TEMPERATURE,PCI
```

The probe should write command stdout/stderr to `raw/` beside the canonical JSON. `nvidia-smi` absence is a recorded failure, not permission to substitute a product-page RTX 3050 specification.

## 2. Windows-native GPU and software identity

Use `nvidia-smi --query-gpu=...` for stable machine-readable identity. Also retain `nvidia-smi -q -d PCI` because it exposes bus ID, current/max link generation and width where supported. Record both reported `compute_cap` and the compiled benchmark architecture (`sm_86` only after runtime identity confirms it). Laptop RTX 3050 parts can differ in VRAM, bus width, power limit and clocks, so the product name is not a measurement of those fields.

Capture toolchain provenance with:

```powershell
where.exe nvidia-smi
where.exe nvcc
nvidia-smi --version
nvcc --version
cmake --version
cl 2>&1 | Select-Object -First 3
python -c "import sys; print(sys.version)"
python -c "import torch; print(torch.__version__, torch.version.cuda); print(torch.cuda.get_device_properties(0))"
```

The Python command is optional and must emit `unavailable` if PyTorch is absent. Do not combine DLLs or CUDA runtimes from unrelated installations. Record native Windows and WSL2 as different environments; WSL2 output is a fallback artifact and never merged into the native result.

For thermal/power context, sample before warmup, during each timed batch, and after the batch using:

```powershell
nvidia-smi --query-gpu=timestamp,temperature.gpu,power.draw,power.limit,clocks.gr,clocks.mem,utilization.gpu,utilization.memory,memory.used --format=csv -l 1
```

If a field is unsupported, preserve the raw error and set that field to null with `availability: unavailable`. Windows Task Manager is a sanity check only; it is not a replacement for device telemetry.

## 3. CUDA copy and FFN-shaped GEMV/GEMM

Use a small pinned native CUDA microbenchmark rather than infer bandwidth from vendor specifications. Pin the CUDA toolkit/compiler commit and compile explicitly for the discovered architecture, initially `-arch=sm_86` for the expected Ampere SKU. A C++/CUDA helper should use CUDA events, `cudaMalloc`, `cudaMallocHost`, `cudaMemcpyAsync`, and cuBLAS (`cublasGemmEx` or `cublasGemmStridedBatched`). Time only synchronized work after warmups.

### Device-copy sweep

Measure device-to-device copy separately from host transfers using sizes such as 1 MiB, 4 MiB, 16 MiB, 64 MiB, 256 MiB, and 1 GiB where allocation permits. For each size: 3 warmups and at least 10 timed repetitions, reporting bytes divided by event elapsed time. Use separate allocations and verify a checksum once so a compiler or invalid path cannot produce a zero-time result. D2D copy is a transport sanity check, not model GEMV bandwidth.

### Representative FFN shapes

The Qwen configuration supplies the shapes: `K=5120`, `N=17408`, with both `N x K` and `K x N` projections. Benchmark:

- GEMV (`M=1`) for decode: `17408x5120` and `5120x17408`, FP16 weights/activations;
- GEMM verification-like batches `M=4,8,16` for the same shapes;
- an optional FP32 accumulation path if the selected cuBLAS routine requires it.

Report kernel time, effective payload bandwidth (`weight_bytes / seconds`), achieved FLOP/s, and numerical error against a deterministic CPU/reference result. Payload bandwidth is **derived**, not physical DRAM bandwidth; include matrix dimensions, dtype, layout, transposition, leading dimensions, alpha/beta, and whether scales/packing are included. GEMV M=1 is the decode-ceiling input; M>1 demonstrates whether batched verification can amortize weight traffic. Do not label a GEMM number as a full-model token rate.

If cuBLAS or CUDA compilation is unavailable, run no fake benchmark: record the build error and use the fallback route (WSL2 native CUDA helper, then a pinned PyTorch eager CUDA-event harness). A CPU-only matrix result is a separate environment and cannot replace the GPU result.

## 4. CPU/SIMD and RAM

Collect CPU model, physical/logical cores, instruction flags (AVX2, FMA, AVX-512 where exposed), nominal speed and installed/available RAM with CIM/PowerShell. For a native bandwidth baseline, compile a pinned C++ STREAM-like helper with MSVC `/O2`; use large arrays (chosen before the run and recorded) exceeding LLC, aligned allocation, and a read/write triad. Warm up, repeat, and report copy, scale, add and triad medians. The result is a measured host-memory proxy, not a universal RAM specification.

Add FFN-shaped CPU GEMV with `K=5120,N=17408`, batch 1 first, then M=4/8/16 if useful. Include a scalar/reference implementation and an AVX2 implementation only when CPUID confirms AVX2. Record correctness tolerance, thread count, affinity policy and bytes read. A failed AVX2 path must fall back to scalar for correctness and remain marked unsupported for the optimization route. This probe does not claim ternary/packed-kernel performance; it establishes the dense baseline and a later CPU split comparison point.

## 5. PCIe inventory and pinned transfers

`nvidia-smi -q -d PCI` identifies bus ID, negotiated link generation/width and max link. Inventory is useful context but not authoritative for tier planning. The authoritative application test is a CUDA helper sweeping pageable and pinned host memory:

- transfer sizes: 4 KiB, 64 KiB, 1 MiB, 4 MiB, 16 MiB, 64 MiB, 256 MiB (reduce the largest point if RAM pressure is documented);
- H2D and D2H, pageable synchronous and pinned asynchronous (`cudaMallocHost` + stream);
- 3 warmups and 10 timed repetitions per direction/size, with event synchronization;
- report median GB/s, p95 latency, and raw samples; verify one round-trip checksum per size.

The transfer result must state whether throughput is one-way, whether the timing includes allocation, and whether overlap was tested. Do not calculate a PCIe ceiling from link GT/s alone. If pinned allocation fails, keep pageable results, capture the exact CUDA status, and queue smaller pinned buffers or WSL2 as alternatives. Candidate engineering routes for a weak transfer path are (a) hidden-state-only transfers with larger batching/double buffering and (b) CPU-resident FFN with GPU-resident recurrent/attention state; the cheapest next test is rerun the smallest successful pinned size and compare median H2D/D2H against pageable.

## 6. SSD temporary sweep

Use a dedicated directory on the target SSD selected by `-TempRoot`; never touch `models/` or existing artifacts. Create a bounded temporary file (default 4 GiB, configurable and recorded; reduce to 1 GiB if free space is insufficient), write deterministic blocks, flush/close, then read it sequentially and in a fixed chunked pattern. Use unbuffered or explicitly documented buffered Win32 I/O; report which mode was used. Include file size, block size (for example 1 MiB), queue/concurrency, elapsed time, MB/s, and whether the run is cold-cache or warm-cache. A second read must be labeled warm/cache-affected, not combined with cold throughput.

PowerShell orchestration should check free space, refuse paths containing model artifacts, use a unique filename, and delete it in `finally`. If cleanup fails, report the path and failure. Candidate routes after a slow SSD are (a) mmap/page-cache warm tier with bounded prefetch and (b) larger RAM staging/double-buffering; the cheapest next test is a smaller sequential temporary file with cache state explicitly recorded. Existing-file reads alone do not satisfy this probe because they confound filesystem cache and model layout.

## 7. Canonical JSON and Markdown schema

JSON is canonical; Markdown is generated and must never be hand-edited. Recommended top-level shape:

```json
{
  "schema_version": "e0-hardware-1",
  "run_id": "E0-HW-<UTC>",
  "status": "complete|partial|failed",
  "environment": {"os":"Windows", "build":"...", "shell":"PowerShell", "host":"...", "power_source":"AC", "power_mode":"...", "script_sha256":"..."},
  "software": {"nvidia_smi":"...", "driver":"...", "cuda_toolkit":"...", "compiler":"...", "python":null, "pytorch":null},
  "hardware": {"gpu":{}, "cpu":{}, "ram":{}, "ssd":{}, "pcie":{}},
  "telemetry": {"temperature_c":{}, "power_w":{}, "clocks_mhz":{}, "samples":[]},
  "benchmarks": {
    "gpu_copy": {"status":"measured", "warmups":3, "repetitions":10, "samples":[], "summary":{}},
    "ffn_gemv_gemm": {"status":"measured|unavailable", "shapes":[], "samples":[], "summary":{}},
    "cpu_ram": {}, "pcie_transfers": {}, "ssd_temp_sweep": {}
  },
  "failures": [],
  "fallbacks": [{"route":"WSL2|PyTorch|smaller sweep", "trigger":"...", "command":"...", "expected":"..."}],
  "provenance": {"raw_files":[], "commands":[], "derived_formulas":[]}
}
```

Every result object should include `unit`, `measurement_kind` (`measured|derived|external|hypothesis`), `availability`, `error`, `raw_samples`, `median`, `spread`, and `conditions` where applicable. Null plus an error is preferable to zero. Markdown should render identity, environment, thermal state, each benchmark's repetitions/median/spread, and a failure/fallback table. Append a concise run record to `experiments/LOG.md` including hypothesis, numeric target, exact command, one changed variable, artifact paths, and Status / Numbers / Next Experiment.

## 8. Verification and failure routes

Verification is layered:

1. **Identity:** repeat `nvidia-smi` and CIM collection; compare immutable identity and report variance in dynamic fields.
2. **Numerical correctness:** checksums for copies; CPU/GPU GEMV/GEMM output tolerance; reject NaN/Inf and failed round trips.
3. **Timing validity:** CUDA-event synchronization, warmups excluded, raw samples retained, outlier policy declared, no profiling run used as the headline timing.
4. **Resource safety:** free-space/RAM checks, bounded SSD file, cleanup, no model overwrite, and no unbounded pinned allocation.
5. **Cross-route labeling:** native Windows and WSL2 artifacts have distinct `environment_id`; missing native tools do not silently become WSL2 numbers.

Failure classes and next routes:

- **No `nvidia-smi`/driver query:** capture command output; collect CPU/RAM/SSD facts; install/repair the OEM-supported driver or run the same probe in WSL2. Cheapest test: rerun `where.exe nvidia-smi` and `nvidia-smi -L`.
- **CUDA compiler/helper build failure:** retain compiler diagnostics; use a pinned PyTorch CUDA-event harness, then WSL2. Do not substitute a CPU result for GPU bandwidth.
- **OOM or pinned allocation failure:** reduce one sweep size at a time, preserve the failure threshold, and test smaller buffers; routes are hidden-state-only transfer and RAM-resident FFN.
- **Thermal/power telemetry unavailable:** continue timing with explicit null telemetry, use `nvidia-smi` query fallback and Windows event logs if available; mark thermal conclusions unavailable.
- **SSD permission/cache interference:** choose a user-writable dedicated temp directory, record buffered/unbuffered mode, and rerun cold/warm as separate records.
- **Unstable variance:** stop claiming a single number; inspect AC/power mode, background load and throttling, increase repetitions, and report median/p95 with telemetry.

No failure is a verdict about the inference route. Each failure records the numeric constraint, at least two candidate routes, and the cheapest command with an expected measurable result.

## Status / Numbers / Next Experiment

**Status:** Windows-native E0 probe design is specified for `nvidia-smi`/PowerShell identity, CUDA copy plus FFN GEMV/GEMM, CPU/RAM, PCIe pinned transfers, bounded SSD temporary sweeps, thermal telemetry, canonical JSON, generated Markdown, and explicit native/WSL2 failure separation. No experiments or local measurements have been run here.

**Numbers:** Proposed defaults are 3 warmups and 10 timed repetitions; GPU copy sizes 1 MiB–1 GiB; FFN shapes 17408×5120 and 5120×17408 at M=1,4,8,16; PCIe sizes 4 KiB–256 MiB; SSD temporary file 4 GiB with 1 MiB blocks. These are probe parameters, not measured results. Project context supplies 5120 hidden, 17408 intermediate and expected sm_86, but the laptop SKU/VRAM/link/bandwidth remain unverified.

**Next Experiment:** Implement and pre-register `scripts/01_hardware_probe.ps1` plus a pinned native CUDA helper, then run one AC warmup-and-measure pass. Expected result: a JSON artifact and generated `notes/hardware_profile.md` with raw samples and medians, or a partial report containing exact failures, at least two routes per blocker, and the cheapest reproducible fallback command.
