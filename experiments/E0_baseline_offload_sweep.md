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

## Results
The first invocation proved the CUDA 12.4 split-asset fix: `ggml_cuda_init` found 1 device, RTX 3050 Laptop GPU, CC 8.6, 4095 MiB VRAM. It completed both tests for `ngl=0`: `pp512 24.46 ± 1.26 t/s` and `tg128 0.10 ± 0.01 t/s`. The process exited 1 after printing the table; no VRAM/RAM telemetry was captured, and the remaining ngl points were not run.

## Status / Numbers / Next Experiment
- **Status:** Partial; `ngl=0` complete, sweep incomplete. Exit code 1 is retained as a first-class failure and is not treated as a clean sweep.
- **Numbers:** `ngl=0`: pp512 24.46 ± 1.26 t/s; tg128 0.10 ± 0.01 t/s; CUDA device 1, CC 8.6, 4095 MiB VRAM.
- **Next Experiment:** Run each remaining point as an isolated command (`-ngl 8/16/24/99`) with unique logs and concurrent `nvidia-smi` telemetry; diagnose the nonzero exit before claiming sweep completion.
