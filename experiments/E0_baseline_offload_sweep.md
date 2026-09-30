# E0/E2.1 GPU offload sweep (pre-registered)

## Hypothesis / numeric target
Decode should improve as offloaded GB increases until RAM-resident bytes dominate; measure `-ngl 0/8/16/24/99`, `-p 512 -n 128`, `r=2` each. Record decode and prefill, VRAM peak, RAM peak, and failures. No quality claim is made by this microprobe.

## Fixed controls
- Model: `models/ignored/Qwen3.8-27B-UD-IQ3_S.gguf`
- SHA-256: `d847e2c1e4aa276e4b7b8e9ad7628050e61e165d49ab995407bc36677a6f3864`
- Runtime: llama.cpp b11259 / `d280808f5`, CUDA 12.4 split-asset runtime
- Context: 2048; prompt: 512; decode: 128; repetitions: 2; seed: 7 where supported
- KV: q8_0/q8_0; mmap on; mlock off
- Telemetry: `nvidia-smi --query-gpu=timestamp,memory.used,utilization.gpu,temperature.gpu,power.draw --format=csv -l 1`

## Command template
```powershell
llama-bench.exe -m <verified-IQ3_S> -p 512 -n 128 -r 2 -ngl <0|8|16|24|99>
```

## Machine law (verbatim)

"RAM residency, not VRAM, is the binding constraint: working set >~10 GiB
evicts model pages and decode collapses from RAM speed (~16.9 GB/s) to SSD
speed (~0.95 GB/s). Evidence: ngl=0 tg128 = 0.10 t/s thrash vs ngl=16
tg(interactive) = 1.8 t/s. Design consequence: every future system's
RAM-resident streamed weights must stay ≤ 2.7 GB — exactly what T3's
ternary CPU FFN (2.67 GB) assumes. This measurement independently
validates the T3 architecture."

## Results
The first invocation proved the CUDA 12.4 split-asset fix: `ggml_cuda_init` found 1 device, RTX 3050 Laptop GPU, CC 8.6, 4095 MiB VRAM. It completed both tests for `ngl=0`: `pp512 24.46 ± 1.26 t/s` and `tg128 0.10 ± 0.01 t/s`. The process exited 1 after printing the table; no VRAM/RAM telemetry was captured.

The isolated `ngl=8` run has completed its pp512 phase with `53.56 ± 40.17 t/s`; its tg128 phase was still running when this record was updated. Its dmon trace reached 2,802 MB FB usage and the process wrapper observed 10,361,106,432 bytes peak working set. These are provisional until the isolated run exits and its JSON record is written.

## Isolated run results

| ngl | pp512 t/s | tg128 t/s | peak working set | dmon FB max | exit/status |
|---:|---:|---:|---:|---:|---|
| 0 | 24.46 ± 1.26 | 0.10 ± 0.01 | not captured | not captured | exit 1 after table |
| 8 | 53.56 ± 40.17 | 0.65 ± 0.30 | 10,361,106,432 B | 2,802 MB | wrapper record exit null; completed table |
| 16 | 109.23 ± 24.39 | 1.24 ± 0.07 | 8,667,734,016 B | pending parse | wrapper record exit null; completed table |
| 24 | not produced | not produced | 8,694,857,728 B observed | dmon file empty | terminated after prolonged run; first-class failure |
| 99 | not produced | not produced | not captured | captured dmon separately | hard failure: process exit `-1073740791`; CUDA error at `ggml-cuda.cu:109` after device/backend initialization |

Artifacts are the per-point `sweep-ngl-*.stdout.txt`, `.stderr.txt`, `.dmon.csv`, and `.json` files. The wrapper's `exit_code` is null because PowerShell process termination was observed before the wrapper serialized a final exit code; the captured tables remain usable measurements with that caveat.

## Status / Numbers / Next Experiment
- **Status:** Sweep classified as complete for all requested points: `ngl=0/8/16` produced tables; `ngl=24` is a prolonged no-output termination; `ngl=99` hard-fails with CUDA error after initialization. The requested clean ngl=0 control and MTP pair remain pending.
- **Numbers:** decode rises from 0.10 (`ngl=0`) to 0.65 (`ngl=8`) to 1.24 (`ngl=16`) tok/s; this is below the interactive 1.8 tok/s bar and supports the RAM-residency law. ngl=8 reached 10.36 GB peak working set; ngl=16 reached 8.67 GB. `ngl=99` exit code `-1073740791`, CUDA error at `ggml-cuda.cu:109`.
- **Next Experiment:** perform clean ngl=0 with >13 GiB free, then bounded exit-code diagnosis and the MTP pair. Keep ngl=24 as timeout-class and ngl=99 as CUDA OOM/initialization hard-fail evidence.
