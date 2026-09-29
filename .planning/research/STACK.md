# STACK — Reproducible runtimes/tools for Qwen3.8-27B on RTX 3050

**Scope.** Runtime/tooling stack for E0–E4 experiments on a Windows laptop RTX 3050 (4–8 GB VRAM, Ampere sm_86). This is a reproducibility plan, not a claim that any route has already run. The architecture facts and project constraints below are taken from `Deep Research  27B on RTX 3050.md`; all throughput and quality figures in that document remain estimates or results from cited external work, not measurements on this laptop.

## 1. Fixed facts and compatibility envelope

* Model target is Qwen/Qwen3.8-27B, 55.6 GB FP16/BF16, with 64 layers, hidden size 5120, intermediate size 17408, 24 query heads/4 KV heads, untied embeddings, a 27-layer vision tower, and one MTP layer. Only 16 layers are conventional full attention; 48 are Gated DeltaNet (GDN). This is a materially different execution path from Qwen2/3 dense-attention GGUF models.
* GPU must be identified rather than inferred from the product name: `nvidia-smi --query-gpu=name,compute_cap,driver_version,memory.total --format=csv`. RTX 3050 laptop parts are expected to report compute capability 8.6, but the exact VRAM (4/6/8 GB), power limit, driver, and memory bus vary.
* Windows adds three reproducibility variables: native Windows versus WSL2, MSVC versus MinGW, and CUDA toolkit/driver pairing. Prefer one declared environment per experiment and record all of them.
* Do not mix CUDA/PyTorch DLLs from multiple installations. `where.exe nvidia-smi`, `where.exe nvcc`, `python -c "import torch; print(torch.__version__,torch.version.cuda,torch.cuda.get_device_properties(0))"` belong in every run record.

### Version policy

There is no safe universal “latest” pin for this model because Qwen3.8/GDN support is moving across projects. Pin a **release tag or full commit SHA**, model revision SHA, Python version, CUDA runtime, and compiler. A floating `main`, unpinned Hugging Face revision, or auto-selected prebuilt wheel is not reproducible. The suggested versions below are **starting pins/ranges to test**, not claims that each combination is already validated.

| Component | Starting pin / build choice | Compatibility risk | Fallback |
|---|---|---|---|
| NVIDIA driver | Current Studio/Game Ready driver that supports the selected CUDA runtime; record exact version | Old OEM laptop drivers can reject a newer CUDA runtime; new drivers do not guarantee kernel support | Use the newest driver allowed by OEM, then select a matching PyTorch wheel; WSL2 only if native CUDA setup is unstable |
| CUDA toolkit | CUDA 12.4 or 12.6 for native builds; use the toolkit required by the pinned PyTorch wheel | CUDA toolkit is not the same as driver; CMake may find a different toolkit than Python | Build llama.cpp with the toolkit visible to CMake; use PyTorch bundled CUDA wheels for E0 and avoid compiling extensions until baseline works |
| PyTorch | Python 3.11, PyTorch 2.5/2.6-era CUDA wheel (select `cu124`/`cu126` matching the tested wheel); exact wheel URL recorded | Windows wheels may lag Linux; custom kernels may require a narrower torch ABI; BF16/FP8 support varies by kernel and GPU | FP16 tensors, eager PyTorch, or WSL2; avoid `torch.compile` until eager output is validated |
| llama.cpp | Pin a commit containing the required Qwen3.5/3.8 architecture and GGUF loader; build `Release` with CUDA and `CMAKE_CUDA_ARCHITECTURES=86` | Older GGUF loaders may parse Qwen3 but not GDN state/MTP/vision; generic `-ngl 99` does not prove all tensors are on GPU | Use the project’s CUDA build and a known compatible GGUF; if model architecture is unsupported, use E0 Transformers or an explicit fork port rather than silently converting |
| ik_llama.cpp | Pin a commit and record fork URL; compile the same CUDA arch | Fork-specific tensor names, quant formats, and CLI flags diverge from upstream; Windows build scripts may lag | Upstream llama.cpp for baseline; maintain separate model files if fork formats differ |
| ktransformers | Pin release/commit and its documented Python/CUDA dependencies | Frequently Linux-first and architecture/backend coverage is narrower; Windows native support and Qwen3.8 GDN support must be proven | WSL2 or E0; treat it as an optional offload comparison, not the baseline |
| BitNet/bitnet.cpp | Pin Microsoft BitNet repository commit and its documented compiler/CUDA requirements | BitNet conversion/training path and runtime kernels are not interchangeable; Qwen3.8 checkpoint conversion is unvalidated; kernels may target newer SMs | Use PyTorch fake-quant layer probe, bitnet.cpp on a supported small model, or BitBLAS INT2/INT1 microbenchmarks |
| BitBLAS | Pin repository commit and its matching PyTorch/CUDA/CUTLASS requirements | Primarily Linux-tested; Windows packaging/build may fail; autotuning can select kernels unsupported on sm_86; INT1/ternary path may be experimental | Run in WSL2, use prebuilt supported kernels, or write a small CUDA/PyTorch extension; compare against FP16/INT8 GEMM |
| Profilers | Nsight Systems/Compute versions compatible with driver; PyTorch Profiler/Chrome trace | Nsight counters can be restricted on consumer Windows GPUs; profiler overhead distorts decode | Time unprofiled runs separately; use CUDA events, `nvidia-smi dmon`, Windows Performance Recorder, and PyTorch profiler traces |

## 2. Experiment ladder (E0–E4)

### E0 — reference and loader smoke test (PyTorch Transformers)

**Purpose:** establish architecture correctness and a reproducible quality reference before quantization. This is a loader/quality gate, not expected to fit in 4–8 GB VRAM.

**Environment:** Windows native first; Python 3.11; pinned `transformers`, `safetensors`, `accelerate`, and PyTorch wheel. Use the exact model revision. Prefer `torch_dtype=torch.float16` on sm_86; do not assume BF16 kernels are fast or available. For a multimodal check, also pin the processor and image package versions.

**Checks:**
1. `AutoConfig.from_pretrained(..., revision=MODEL_SHA)` confirms the expected GDN/full-attention/MTP fields.
2. `AutoModelForCausalLM` (and the documented multimodal class, if available) loads with `trust_remote_code` only if the model card requires it; record the code revision.
3. One short text prompt and one image prompt (if supported) produce finite logits and deterministic greedy output with `torch.manual_seed`, `do_sample=False`.
4. Save parameter names, dtypes, and peak host memory. A full reference may require disk/RAM offload; that is an experiment, not a fit claim.

**Risks/fallbacks:** `transformers` may recognize Qwen3.8 only on a newer release than the pinned wheel; upgrade only that package and record the changed variable. If native Windows extension import fails, run the same environment in WSL2. If the full checkpoint cannot be loaded, use a small architecture fixture/config to validate the class, then use the published NVFP4 checkpoint as an E0 teacher only after verifying its tensor names.

### E1 — upstream llama.cpp GGUF baseline

**Purpose:** fastest route to a measured quantized baseline (Q4/Q3/IQ3/IQ2 where a compatible conversion exists), with CPU/RAM and partial CUDA offload.

**Build sketch (record actual commit and CMake output):**
```powershell
cmake -S . -B build -DGGML_CUDA=ON -DCMAKE_BUILD_TYPE=Release -DCMAKE_CUDA_ARCHITECTURES=86
cmake --build build --config Release -j
```

**Run variables:** context 2048 first; `-ngl` stepped from 0 to a safe value; `-ctk q8_0 -ctv q8_0` only as a separately logged change; then tensor overrides (`-ot`) only if the pinned build documents the syntax and tensor names. Record model quant, `-ngl`, context, prompt/decode token counts, load time, VRAM/RAM peaks, and generated text. Keep prompt template and sampler fixed.

**Key risks:** a GGUF may be Qwen3-compatible while lacking Qwen3.8 GDN recurrent-state support; vision tensors and MTP may be ignored; `-ngl 99` can trigger OOM rather than graceful partial offload; quantized KV flags may not apply to GDN state. Confirm architecture by startup logs and output, not by process exit alone. GGUF conversion can also lose multimodal behavior if the converter/runtime does not carry the vision tower and projector.

**Fallback routes:** (a) use text-only language path to establish E1, then add temporal vision staging; (b) upstream commit → ik_llama.cpp commit if low-bit kernels or tensor placement is missing; (c) ktransformers/WSL2 if native build fails; (d) return to E0 for an unsupported architecture rather than declaring a quant result valid.

### E2 — fork comparison: ik_llama.cpp and ktransformers

**Purpose:** test whether fork-specific low-bit kernels, tensor placement, or pipelined CPU/GPU execution improve the E1 baseline.

Run exactly the same prompt, context, quant file, sampler seed, and measurement method. Forks must be compared at matched quantization and output quality. Record fork SHA and all CLI help output because flags such as tensor override/offload names are not portable. A fork result is invalid as an apples-to-apples speed comparison if it uses a different quant, context, batch, or speculative setting.

**Compatibility risks:** GDN’s recurrent state may be implemented in one fork but not another; a fork may load weights but produce incorrect state transitions. ktransformers has historically had stronger Linux assumptions and may require WSL2. Windows CUDA builds can fail due to MSVC/CMake/CUDA version combinations. The cheapest correctness test is a 32–128-token greedy comparison against E0 or a trusted reference, checking token IDs, logits (where exposed), and recurrent-state reset behavior between independent prompts.

**Fallback:** keep E1 as the reproducible baseline and isolate only the missing feature (for example, a tensor placement patch) in a fork. Do not make a fork the sole runtime until it passes the same 50-prompt quality gate.

### E3 — BitBLAS / bitnet.cpp low-bit kernel probes

**Purpose:** measure kernels and memory behavior before attempting a full 27B ternary or 1.25-bit conversion. The project document explicitly identifies BitBLAS and BitNet CUDA kernels as promising but notes that laptop sm_86 throughput is unmeasured.

**Probe sequence (one variable at a time):**
1. FP16 GEMV/GEMM baseline for shapes derived from `17408×5120` and `5120×17408`, batch 1 and verification batch 4/8.
2. INT8/INT4 weight kernels with FP16 activation.
3. INT2/INT1/ternary kernel if the pinned commit exposes sm_86 support.
4. Only after numerical error and kernel speed are recorded, integrate one replaced FFN block in a PyTorch harness.

Use CUTLASS/BitBLAS autotuning caches as artifacts; warm up kernels; time with CUDA events; report effective bandwidth and absolute error against FP16. Compile for `sm_86` explicitly. A kernel that compiles for `sm_80` may still use instructions or tile assumptions that are wrong/slow on sm_86; verify generated architecture and runtime dispatch.

**BitNet risk:** `bitnet.cpp` is a runtime for a particular ternary representation, while BitDistill/Sherry describe training or conversion procedures. A Qwen3.8 GGUF cannot be relabeled as BitNet without a format conversion and numerical validation. Full 27B QAT/distillation is not an E3 laptop experiment; start with one layer or block-output matching.

**Fallbacks:** WSL2 Linux build; CPU bitnet.cpp/AVX2 probe; BitBLAS microbenchmark only; or a custom PyTorch CUDA extension using packed 2-bit weights. If the kernel is unsupported on Windows, preserve the numerical harness and move only compilation to WSL2.

### E4 — profiling, placement, and reproducibility

**Purpose:** identify whether decode is weight-bandwidth, PCIe transfer, kernel launch, recurrent-state, or KV limited, and make every result auditable.

**Instrumentation stack:**
* Coarse: `nvidia-smi --query-gpu=timestamp,utilization.gpu,utilization.memory,memory.used,power.draw --format=csv -l 1`, Windows Task Manager only as a sanity check.
* Precise latency: CUDA events around prefill and decode; report median and p95 over a warm run, excluding model load.
* PyTorch: `torch.profiler` with CPU/CUDA activities and a small schedule; export Chrome trace. Use eager mode first. `torch.compile`/Inductor is a separate experiment because graph breaks around GDN state, dynamic shapes, or custom quant kernels can erase benefits.
* Nsight Systems: timeline for CPU→GPU copies, kernel launches, synchronization, and overlap. Nsight Compute: achieved memory bandwidth, occupancy, register/shared-memory use for one representative GEMV. Consumer Windows counter restrictions are expected; if counters are unavailable, state that and use CUDA-event timings.
* Memory: `torch.cuda.max_memory_allocated/reserved`, `nvidia-smi`, and Windows process/RAM counters. Distinguish allocated from reserved and VRAM from shared system memory.

**Profiler risks:** profiling changes clocks and launch timing; Windows WDDM can preempt/timeout long kernels; laptop thermal/power management changes sustained rates. Run an unprofiled repeat after each profile. Never infer tok/s from one short decode or from prompt processing alone.

## 3. Reproducible experiment record

Every E0–E4 run appends to `experiments/LOG.md` (including failures):

```text
UTC timestamp:
Experiment: E0/E1/E2/E3/E4
Host: Windows build or WSL2 distro; CPU; RAM; SSD; GPU exact name/VRAM; driver
Software: git SHAs; Python; PyTorch/CUDA; compiler/CMake; model revision; quant file SHA256
Hypothesis + numeric target:
Exact command/config:
Prompt/template/seed; context; batch; quant; offload/tensor placement:
Warmups and measured repetitions:
Prefill tok/s; decode tok/s; median/p95 latency:
Peak VRAM allocated/reserved and nvidia-smi; peak RAM:
Quality: fixed output, token/logit agreement or PPL/eval result:
Failure or caveat; next route:
```

**Numerical targets are proposed, not measured:** E1 should first achieve a repeatable decode measurement at context 2048; E3 should reach at least 70% of the laptop’s measured STREAM/CUDA-memory-bandwidth proxy before deeper integration; E4 should explain >90% of decode wall time by timeline categories. The project’s initial ambition is ≥3 decode tok/s, while the architecture research’s 6–8 or 7 tok/s values are estimates requiring validation.

## 4. Decision tree and fallback routes

1. **E0 class/load fails:** pin a newer Transformers release or exact model code revision; test WSL2; use a small fixture to separate loader from memory failure.
2. **E1 GGUF does not recognize GDN/vision/MTP:** stop speed comparisons; locate a compatible converter/runtime commit, or port the missing architecture. A generic Qwen3 GGUF result is not evidence for Qwen3.8.
3. **E1 loads but OOMs:** reduce context, quantize KV where supported, lower `-ngl`, and place FFN/lm_head on CPU. Keep the 4/6/8 GB SKU as separate profiles.
4. **E2 fork build fails:** retain upstream E1; build in WSL2; record compiler error; isolate a patch rather than changing quant and runtime together.
5. **E3 kernel unsupported:** use INT4/INT8 baseline, CPU AVX2, or WSL2; preserve packed-weight numerical tests. A full ternary conversion is deferred until one-block error is acceptable.
6. **E4 profiler unavailable:** use CUDA events + nvidia-smi + host timing, state missing counters, and repeat without profiler.

## Status / Numbers / Next Experiment

**Status:** Stack is specified as a pinned, two-environment (native Windows first, WSL2 fallback) ladder. E0 establishes model correctness; E1 establishes a compatible GGUF baseline; E2 compares forks; E3 isolates BitBLAS/bitnet.cpp kernel risk on sm_86 before conversion; E4 attributes bottlenecks. No new laptop measurements are claimed here. The highest risk is not merely VRAM: it is Qwen3.8’s GDN state, vision/MTP preservation, and immature Windows support across low-bit projects.

**Numbers:** Model file is 55.6 GB FP16/BF16; 64 layers; 48 GDN + 16 full-attention layers; RTX 3050 target is sm_86 with 4–8 GB VRAM (verify exact SKU). Project’s initial decode ambition is ≥3 tok/s. Architecture research estimates 25.6B streamed parameters/token and mixed 1.25/2.5-bit payload ≈5.3 GB, but these are calculations/estimates, not measurements. Every run must report prefill/decode tok/s, peak VRAM/RAM, and quality.

**Next Experiment:** E0 smoke test on the actual laptop. Hypothesis: the pinned Transformers/model revision can load the Qwen3.8 config and produce deterministic text logits in an FP16/offload configuration, with no NaNs, before any quantization work. Commands:

```powershell
nvidia-smi --query-gpu=name,compute_cap,driver_version,memory.total --format=csv
python -m venv .venv-e0
.\.venv-e0\Scripts\python -m pip install --upgrade pip
# Install the chosen, recorded PyTorch CUDA wheel, then pinned transformers/accelerate/safetensors.
.\.venv-e0\Scripts\python scripts\e0_smoke.py --model Qwen/Qwen3.8-27B --revision <MODEL_SHA> --dtype float16 --prompt "Give one sentence about CUDA."
```

Expected measurable result: either deterministic token IDs/logits and a complete environment record, or a precisely classified loader/VRAM/Windows error that selects the next fallback. Do not proceed to E1 until E0’s model class and architecture fields are confirmed.
