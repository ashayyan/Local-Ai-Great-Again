# E0 Baseline Selection

**Date:** 2026-09-29 (workspace inspection; UTC date)
**Scope:** acquisition baseline only. No model weights were downloaded and no `LOG.md`, `REQUIREMENTS.md`, or `STATE` file was edited.

## Findings

| Item | Result | Evidence |
|---|---|---|
| llama.cpp checkout/binary | **Absent** | `runtimes/` contains no files; `Get-Command llama-cli` and `Get-Command llama-server` return no command; recursive `*llama*` search found none. |
| git | **Available** | `C:\Program Files\Git\cmd\git.exe` |
| cmake | **Absent** | `Get-Command cmake` = NOT_FOUND |
| Compilers/build helpers | **Absent on PATH** | `cl`, `gcc`, `g++`, `clang`, `clang++`, `nvcc`, `ninja`, `make` all NOT_FOUND |
| Python | Available | `C:\Users\lahd2\miniconda3\python.exe` |
| RAM | 16 GiB installed | 17,179,676,184 bytes from existing hardware record / probe |
| GPU | RTX 3050 Laptop, 4,096 MiB VRAM | NVIDIA device, compute capability 8.6; existing hardware profile records 3,825 MiB free at probe |
| Network metadata | **Works** | Hugging Face API HTTP 200 for repository and recursive tree; only JSON metadata was fetched |
| Local weights | **None** | `models/` has metadata/config files only; no GGUF/safetensors weights |

The Hugging Face repository `unsloth/Qwen3.8-27B-GGUF` lists the requested GGUF files and exact byte sizes. The API listing was metadata-only; no large file URL was fetched or downloaded.

## Selected quantization baseline

Primary baseline: **`Qwen3.8-27B-UD-IQ3_S.gguf`**, 12,040,883,104 bytes (about **12.0 GB decimal**). It is the best first quality/size point requested while leaving the largest margin among the listed practical IQ3 options for CPU/RAM and KV state.

Fallback sequence:

1. **`Qwen3.8-27B-UD-IQ3_XXS.gguf`**, 10,934,860,704 bytes (about **10.9 GB**).
2. **`Qwen3.8-27B-UD-IQ2_XXS.gguf`**, 7,266,070,528 bytes (about **7.3 GB**).

A conventional Q4 baseline is **forbidden by the current resource constraint**: the repository's `UD-Q4_K_*` files are approximately 15.4--17.6 GB, while the machine has 16 GiB RAM and only 4 GiB VRAM. Even the smallest listed Q4-family artifact exceeds installed RAM before runtime, KV cache, OS, and multimodal projector overhead; Q4 is therefore not an E0 acquisition target. This is a resource constraint, not a quality verdict: IQ3/IQ2 plus CPU/RAM offload and/or layer streaming are the two routes to test.

## Runtime and feature status

- **llama.cpp:** not installed or checked out locally, and no build toolchain is currently available for a native build. Runtime execution, GGUF loading, GDN support, vision support, and token speed are therefore **unverified**.
- **Qwen3.5 support:** no local runtime or pinned llama.cpp source was found, so Qwen3.5-family support status is **unknown/unverified**, not claimed. Do not infer support from a model filename.
- **MTP:** the repository metadata lists `MTP/mtp-Qwen3.8-27B-Q4_0.gguf` (1,369,590,656 bytes), but that is an artifact listing only. Native MTP loading/decoding support is **unverified** until a pinned runtime build and a real load/generation test succeed. The MTP artifact is not an E0 download target.

## Two routes and cheapest experiment

### Route A — stock llama.cpp, partial offload (primary)

Install/build or obtain a pinned Windows CUDA llama.cpp runtime, then acquire only the primary IQ3_S GGUF (plus required small tokenizer/projector metadata as applicable). Start with context 2048, quantized KV, and partial GPU offload; measure load success, peak VRAM/RAM, prefill/decode tok/s, and a fixed quality prompt. If IQ3_S cannot fit or is too slow, repeat unchanged harness with IQ3_XXS, then IQ2_XXS.

### Route B — streamed/layered CPU-RAM/SSD execution (fallback)

Use a runtime/fork that supports CPU/RAM offload or layer streaming, keeping attention/KV hot on GPU and paging FFN/weights from RAM/SSD. This directly addresses the 12.0 GB primary versus 4 GiB VRAM and 16 GiB RAM constraint; profile SSD bandwidth and decode speed. If stock llama.cpp lacks the needed architecture or streaming behavior, test a separately pinned fork rather than silently treating a failed stock load as a model failure.

**Cheapest next experiment (no model download):** verify the environment and metadata endpoints first, then install/build tooling before selecting a weight. Exact commands:

```powershell
Get-Location
Get-Command git,cmake,ninja,make,cl,gcc,g++,clang,clang++,nvcc -ErrorAction SilentlyContinue
Get-Command llama-cli,llama-server -ErrorAction SilentlyContinue
Get-CimInstance Win32_ComputerSystem | Select-Object TotalPhysicalMemory
Get-CimInstance Win32_VideoController | Select-Object Name,AdapterRAM,DriverVersion
Invoke-RestMethod 'https://huggingface.co/api/models/unsloth/Qwen3.8-27B-GGUF?expand[]=siblings' |
  Select-Object id,siblings
Invoke-RestMethod 'https://huggingface.co/api/models/unsloth/Qwen3.8-27B-GGUF/tree/main?recursive=true&expand=true' |
  Where-Object { $_.path -match 'UD-IQ[23]_(S|XXS)|UD-Q4|MTP/' } |
  Select-Object path,size
```

**Expected measurable result:** commands report git/Python but no llama.cpp, cmake, or compiler; GPU/RAM identify 4 GiB/16 GiB; Hugging Face returns HTTP 200 and exact file listings without creating any file in `models/`. After tooling is installed, the cheapest weight-bearing test is one 2048-context IQ3_S load/generation run with `-ngl 99 -ctk q8_0 -ctv q8_0`, falling back in the sequence above only on a recorded load/resource failure.

## Source and reproducibility

Metadata source: [Hugging Face model API](https://huggingface.co/api/models/unsloth/Qwen3.8-27B-GGUF?expand%5B%5D=siblings) and [recursive tree API](https://huggingface.co/api/models/unsloth/Qwen3.8-27B-GGUF/tree/main?recursive=true&expand=true). The repository tree response supplied the exact byte sizes above. GitHub's llama.cpp API was reachable at `https://api.github.com/repos/ggml-org/llama.cpp`; this confirms the upstream repository exists, not that a local checkout or feature support is present.

## Status / Numbers / Next Experiment

- **Status:** Baseline acquisition selection complete; no weights downloaded; runtime absent/unverified.
- **Numbers:** 16 GiB RAM; 4,096 MiB VRAM; primary IQ3_S 12.0 GB; fallbacks IQ3_XXS 10.9 GB and IQ2_XXS 7.3 GB; Q4 family 15.4--17.6 GB and forbidden for this resource-constrained E0.
- **Next Experiment:** install/pin a CUDA-capable llama.cpp toolchain (or obtain a pinned binary), then run one IQ3_S, context-2048, partial-offload load/generation test and record resource/speed/quality measurements.
